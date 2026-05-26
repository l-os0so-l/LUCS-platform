"""RSOD Platform — Extensible Data Validation Subsystem (Industrial Standard).

This module implements a **validator registry pattern** that decouples
validation logic from business workflow code.  New validators can be added
without touching the framework, and failures are collected rather than
short-circuited so users get a complete report.

Design Goals
------------
1. **Extensibility** — add new checks via ``@register_validator`` without
   modifying core code.
2. **Composability** — run any subset of validators on demand.
3. **Observability** — every check produces a structured ``CheckResult`` with
   level, message, and optional details.
4. **Resilience** — a single crashing validator does not abort the pipeline.

Quick Start
-----------
>>> from app.core.validation import CheckContext, DataValidator, register_validator, CheckResult, CheckLevel
>>>
>>> context = CheckContext(
...     images_dir=Path("/data/images"),
...     annotations_dir=Path("/data/annotations"),
...     classes=["aircraft", "oiltank"]
... )
>>> validator = DataValidator(context)
>>> passed = validator.validate_and_report()

Writing a Custom Validator
--------------------------
>>> @register_validator("my_custom_check")
>>> def check_something(ctx: CheckContext) -> list[CheckResult]:
...     results = []
...     if ctx.images_dir and not any(ctx.images_dir.iterdir()):
...         results.append(CheckResult(
...             level=CheckLevel.WARNING,
...             message="Image directory is empty"
...         ))
...     return results
"""

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol, Set

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _can_encode(char: str, encoding: str | None = None) -> bool:
    """Check whether *char* can be encoded to the target stream."""
    enc = encoding or sys.stdout.encoding or "utf-8"
    try:
        char.encode(enc)
        return True
    except UnicodeEncodeError:
        return False

# ---------------------------------------------------------------------------
# Check Levels
# ---------------------------------------------------------------------------


class CheckLevel(str, Enum):
    """Severity level of a validation check result.

    Using ``str`` mixin so serialisers (JSON, Pydantic) can treat the member
    as a plain string while we retain enum safety in code.
    """

    PASS = "pass"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

    @property
    def icon(self) -> str:
        """Human-readable Unicode icon for terminal reporting.

        Falls back to plain ASCII brackets on terminals that do not support
        Unicode (e.g. Windows CMD with GBK encoding).
        """
        icons = {
            CheckLevel.PASS: "✅",
            CheckLevel.INFO: "ℹ️ ",
            CheckLevel.WARNING: "⚠️ ",
            CheckLevel.ERROR: "❌",
        }
        fallback = {
            CheckLevel.PASS: "[PASS]",
            CheckLevel.INFO: "[INFO]",
            CheckLevel.WARNING: "[WARN]",
            CheckLevel.ERROR: "[ERR ]",
        }
        candidate = icons[self]
        return candidate if _can_encode(candidate) else fallback[self]


# ---------------------------------------------------------------------------
# Data Transfer Objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CheckResult:
    """Immutable record produced by a single validation check.

    Attributes:
        level: Severity of the finding.
        message: Human-readable description (should be actionable).
        check_name: Identifier of the validator that produced this result.
                    Automatically populated by the framework when absent.
        details: Arbitrary serialisable data (counts, file lists, etc.).
    """

    level: CheckLevel
    message: str
    check_name: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Frozen dataclass with mutable default is safe because field(...)
        # returns a new dict each time, but we keep the post-init guard for
        # defensiveness.
        object.__setattr__(
            self, "details", dict(self.details) if self.details else {}
        )


@dataclass
class CheckContext:
    """Shared context passed to every validator.

    Using a dataclass instead of loose parameters means:

    * New fields can be added without breaking existing validator signatures.
    * Validators can share intermediate state (e.g. one validator counts files
      and another reads them).
    * Type checkers catch misspelled attribute access.
    """

    annotations_dir: Optional[Path] = None
    images_dir: Optional[Path] = None
    classes: Optional[List[str]] = None
    image_extensions: List[str] = field(
        default_factory=lambda: [".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"]
    )
    extra: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Validator Protocol & Registry
# ---------------------------------------------------------------------------


class ValidatorFn(Protocol):
    """Structural type for validator callables.

    Any function matching this signature can be registered, regardless of
    whether it explicitly inherits from anything.
    """

    def __call__(self, ctx: CheckContext) -> List[CheckResult]: ...


#: Global registry mapping validator name → callable.
_validators: Dict[str, ValidatorFn] = {}


def register_validator(name: str) -> Callable[[ValidatorFn], ValidatorFn]:
    """Decorator that registers a function as a named validator.

    Example::

        @register_validator("directories_exist")
        def check_directories(ctx: CheckContext) -> list[CheckResult]:
            ...

    Args:
        name: Unique identifier for the validator.  Duplicate names will
              overwrite the previous registration (intentional — last wins).

    Returns:
        The same function, unmodified, so it can still be imported and tested
        directly.
    """

    def decorator(func: ValidatorFn) -> ValidatorFn:
        _validators[name] = func
        # Attach metadata for introspection and debugging
        setattr(func, "_validator_name", name)
        logger.debug("Registered validator: %s", name)
        return func

    return decorator


def list_validators() -> List[str]:
    """Return a sorted list of all registered validator names."""
    return sorted(_validators.keys())


def get_validator(name: str) -> Optional[ValidatorFn]:
    """Look up a validator by name.

    Returns ``None`` if *name* is not registered, allowing callers to
    gracefully skip unknown validators rather than crashing.
    """
    return _validators.get(name)


def run_validators(
    context: CheckContext,
    validator_names: Optional[List[str]] = None,
    fail_fast: bool = False,
) -> List[CheckResult]:
    """Execute validators and aggregate their results.

    Args:
        context: Shared data bundle passed to every validator.
        validator_names: Whitelist of validators to run.  If ``None``,
                         all registered validators are executed.
        fail_fast: If ``True``, stop on the first *ERROR* result.  Default
                   is ``False`` so users receive a full diagnostic report.

    Returns:
        Flattened list of ``CheckResult`` objects in execution order.
    """
    names = validator_names if validator_names is not None else list_validators()
    results: List[CheckResult] = []

    for name in names:
        validator = get_validator(name)
        if validator is None:
            logger.warning("Skipping unknown validator: %s", name)
            results.append(
                CheckResult(
                    level=CheckLevel.ERROR,
                    message=f"Unknown validator: {name}",
                    check_name="_framework_",
                )
            )
            continue

        try:
            check_results = validator(context)
        except Exception as exc:  # noqa: BLE001
            # A single broken validator must not kill the pipeline.
            logger.exception("Validator %s crashed", name)
            results.append(
                CheckResult(
                    level=CheckLevel.ERROR,
                    message=f"Validator '{name}' raised {type(exc).__name__}: {exc}",
                    check_name=name,
                    details={"exception": str(exc)},
                )
            )
            if fail_fast:
                break
            continue

        # Attach validator name if the implementer forgot to set it
        for r in check_results:
            if not r.check_name:
                object.__setattr__(r, "check_name", name)
            results.append(r)

        # Optional short-circuit for ERROR-level findings
        if fail_fast and any(r.level == CheckLevel.ERROR for r in check_results):
            break

    return results


# ---------------------------------------------------------------------------
# Built-in Validators
# ---------------------------------------------------------------------------


@register_validator("directories_exist")
def _check_directories_exist(ctx: CheckContext) -> List[CheckResult]:
    """Verify that required directories exist on disk."""
    results: List[CheckResult] = []

    for label, dir_path in (
        ("annotations", ctx.annotations_dir),
        ("images", ctx.images_dir),
    ):
        if dir_path is None:
            continue
        if dir_path.exists() and dir_path.is_dir():
            results.append(
                CheckResult(
                    level=CheckLevel.PASS,
                    message=f"{label.capitalize()} directory exists: {dir_path}",
                )
            )
        else:
            results.append(
                CheckResult(
                    level=CheckLevel.ERROR,
                    message=f"{label.capitalize()} directory missing: {dir_path}",
                )
            )

    return results


@register_validator("annotation_files")
def _check_annotation_files(ctx: CheckContext) -> List[CheckResult]:
    """Check for the presence of annotation files (XML by default)."""
    results: List[CheckResult] = []

    if ctx.annotations_dir is None or not ctx.annotations_dir.exists():
        return results

    xml_files = list(ctx.annotations_dir.glob("*.xml"))

    if not xml_files:
        results.append(
            CheckResult(
                level=CheckLevel.ERROR,
                message="No XML annotation files found",
            )
        )
    else:
        results.append(
            CheckResult(
                level=CheckLevel.PASS,
                message=f"Found {len(xml_files)} XML annotation files",
                details={"count": len(xml_files)},
            )
        )

    return results


@register_validator("image_annotation_match")
def _check_image_annotation_match(ctx: CheckContext) -> List[CheckResult]:
    """Detect orphaned images (no XML) and orphaned annotations (no image).

    Returns ``WARNING`` rather than ``ERROR`` because partial mismatches
    often occur in real-world datasets and do not necessarily block training.
    """
    results: List[CheckResult] = []

    if ctx.annotations_dir is None or ctx.images_dir is None:
        return results

    if not ctx.annotations_dir.exists() or not ctx.images_dir.exists():
        return results

    xml_stems = {f.stem for f in ctx.annotations_dir.glob("*.xml")}

    image_stems: Set[str] = set()
    for ext in ctx.image_extensions:
        image_stems.update({f.stem for f in ctx.images_dir.glob(f"*{ext}")})

    missing_images = xml_stems - image_stems
    missing_annotations = image_stems - xml_stems

    if missing_images:
        results.append(
            CheckResult(
                level=CheckLevel.WARNING,
                message=f"{len(missing_images)} annotations lack a matching image",
                details={
                    "missing": sorted(missing_images)[:10],
                    "hint": "These XML files will be skipped during conversion.",
                },
            )
        )

    if missing_annotations:
        results.append(
            CheckResult(
                level=CheckLevel.WARNING,
                message=f"{len(missing_annotations)} images lack a matching annotation",
                details={
                    "missing": sorted(missing_annotations)[:10],
                    "hint": "These images will be treated as unlabelled data.",
                },
            )
        )

    if not missing_images and not missing_annotations:
        matched = len(xml_stems & image_stems)
        results.append(
            CheckResult(
                level=CheckLevel.PASS,
                message=f"Image-to-annotation match complete: {matched} pairs",
            )
        )

    return results


@register_validator("class_validation")
def _check_classes(ctx: CheckContext) -> List[CheckResult]:
    """Validate that annotation classes are within the expected set.

    Only the first 100 XML files are inspected to keep runtime bounded.
    """
    results: List[CheckResult] = []

    if ctx.annotations_dir is None or not ctx.classes:
        return results

    import xml.etree.ElementTree as ET

    expected = set(ctx.classes)
    found: Set[str] = set()
    unknown: Set[str] = set()
    invalid_files: List[str] = []

    xml_files = list(ctx.annotations_dir.glob("*.xml"))[:100]
    for xml_file in xml_files:
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            for obj in root.findall("object"):
                name_elem = obj.find("name")
                if name_elem is not None and name_elem.text:
                    cls = name_elem.text.strip()
                    found.add(cls)
                    if cls not in expected:
                        unknown.add(cls)
        except ET.ParseError as exc:
            invalid_files.append(f"{xml_file.name} ({exc})")
        except Exception as exc:  # noqa: BLE001
            invalid_files.append(f"{xml_file.name} ({type(exc).__name__})")

    if found:
        results.append(
            CheckResult(
                level=CheckLevel.INFO,
                message=f"Classes discovered in dataset: {sorted(found)}",
            )
        )

    if unknown:
        results.append(
            CheckResult(
                level=CheckLevel.WARNING,
                message=f"Unknown classes found: {sorted(unknown)}",
                details={
                    "expected": sorted(expected),
                    "hint": "Update the class list or fix annotations.",
                },
            )
        )

    if invalid_files:
        results.append(
            CheckResult(
                level=CheckLevel.WARNING,
                message=f"Failed to parse {len(invalid_files)} XML file(s)",
                details={"samples": invalid_files[:5]},
            )
        )

    if not unknown and not invalid_files:
        results.append(
            CheckResult(
                level=CheckLevel.PASS,
                message="Class validation passed",
            )
        )

    return results


# ---------------------------------------------------------------------------
# High-level Facade
# ---------------------------------------------------------------------------


class DataValidator:
    """Convenience façade that wraps context + reporting.

    Typical usage::

        validator = DataValidator(context)
        ok = validator.validate_and_report()
        if not ok:
            sys.exit(1)
    """

    def __init__(
        self,
        context: CheckContext,
        validator_names: Optional[List[str]] = None,
        fail_fast: bool = False,
    ):
        self.context = context
        self.validator_names = validator_names
        self.fail_fast = fail_fast

    def validate(self) -> List[CheckResult]:
        """Run validators and return raw results."""
        return run_validators(
            self.context,
            validator_names=self.validator_names,
            fail_fast=self.fail_fast,
        )

    def validate_and_report(self, output: Optional[Callable[[str], None]] = None) -> bool:
        """Run validators, print a formatted report, and return overall status.

        Args:
            output: Callable that receives each line of the report.
                    Defaults to ``print``.

        Returns:
            ``True`` if no ERROR-level results were found.
        """
        results = self.validate()
        printer = output if output is not None else print

        # Summary counters
        errors = sum(1 for r in results if r.level == CheckLevel.ERROR)
        warnings = sum(1 for r in results if r.level == CheckLevel.WARNING)
        infos = sum(1 for r in results if r.level == CheckLevel.INFO)
        passes = sum(1 for r in results if r.level == CheckLevel.PASS)

        # Header
        printer("")
        printer("=" * 60)
        printer("Data Validation Report")
        printer("=" * 60)
        printer("")

        # Group by level for readability
        for level in (CheckLevel.ERROR, CheckLevel.WARNING, CheckLevel.INFO, CheckLevel.PASS):
            level_results = [r for r in results if r.level == level]
            for r in level_results:
                line = f"{level.icon} [{level.value.upper()}] {r.check_name}: {r.message}"
                printer(line)
                if r.details:
                    for key, value in r.details.items():
                        if isinstance(value, list):
                            printer(f"   {key}: {value}")
                        else:
                            printer(f"   {key}: {value}")

        # Footer
        printer("")
        printer("-" * 40)
        total = len(results)
        printer(f"Total checks: {total}")
        if errors:
            printer(f"  Errors  : {errors}")
        if warnings:
            printer(f"  Warnings: {warnings}")
        if infos:
            printer(f"  Info    : {infos}")
        if passes:
            printer(f"  Passed  : {passes}")
        printer("-" * 40)

        return errors == 0
