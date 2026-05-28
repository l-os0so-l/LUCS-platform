"""
AI 问答接口 — 对接 Kimi (Moonshot) API
"""
import logging
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI

from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/qa", tags=["qa"])

# 系统提示词 — 让 AI 基于真实项目信息回答，禁止夸大
SYSTEM_PROMPT = (
    "你是 LUCS Platform（土地利用分类智能检测平台）的 AI 助手。"
    "请严格基于以下真实信息回答，禁止编造或夸大指标。"
    "\n\n【平台真实信息】"
    "\n- 模型：DeepLabV3+ / ResNet50，基于 LoveDA 数据集训练。"
    "\n- 支持 7 类：背景(background)、建筑(building)、道路(road)、水域(water)、裸地(barren)、林地(forest)、耕地(agriculture)。"
    "\n- 验证集各类别 IoU（交并比）：裸地 79.5%、背景 77.2%、耕地 74.4%、水域 66.0%、道路 62.9%、建筑 61.8%、林地 58.9%。"
    "\n- 平均 mIoU 约在 65%–70% 区间，属于教学/演示级别，远未达到生产环境精度。"
    "\n- 平台功能：单图分类、批量分类、视频帧实时分类、历史记录查看。不支持混淆矩阵、F1-score、Kappa 系数输出。"
    "\n- 模型仅能在已训练的 7 类上推理，不能识别其他土地类型。"
    "\n\n【回答原则】"
    "\n1. 如实说明指标，绝不夸大。"
    "\n2. 用户问及平台不支持的功能时，明确告知暂不支持。"
    "\n3. 用户问及平台不知道的信息时，坦诚说不知道，不要编造。"
    "\n4. 回答简洁、友好，使用中文。"
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    success: bool
    message: str
    data: dict = None


def _get_client() -> OpenAI:
    if not settings.MOONSHOT_API_KEY:
        raise HTTPException(status_code=500, detail="Kimi API Key 未配置，请在 backend/.env 中设置 MOONSHOT_API_KEY")
    return OpenAI(
        api_key=settings.MOONSHOT_API_KEY,
        base_url="https://api.moonshot.cn/v1",
    )


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """调用 Kimi API 进行单轮问答"""
    try:
        client = _get_client()
        completion = client.chat.completions.create(
            model="kimi-k2.6",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": req.message},
            ],
            max_tokens=2048,
        )
        reply = completion.choices[0].message.content
        return ChatResponse(
            success=True,
            message="请求成功",
            data={"reply": reply},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Kimi API 调用失败")
        raise HTTPException(status_code=500, detail=f"AI 服务暂时不可用: {str(e)}")
