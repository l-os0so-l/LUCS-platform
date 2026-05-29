@echo off
chcp 65001 >nul
echo ===========================================
echo   LUCS Platform 一键启动脚本
echo ===========================================
echo.

REM 设置 Python 路径（根据你的 conda 环境修改）
set PYTHON=D:\Anaconda\envs\rsod-web\python.exe

REM 检查 Python 是否存在
if not exist "%PYTHON%" (
    echo [错误] 找不到 Python: %PYTHON%
    echo 请修改本脚本中的 PYTHON 路径为你的 conda 环境路径。
    pause
    exit /b 1
)

REM 检查后端模型文件
echo [1/3] 检查模型文件...
if not exist "backend\models\land_seg_best.pth" (
    echo [警告] 未找到 backend\models\land_seg_best.pth
    echo 模型文件缺失，检测功能将不可用！
)

REM 启动后端
echo [2/3] 启动后端服务 (http://localhost:8000)...
start "LUCS Backend" cmd /k "cd /d %~dp0backend && %PYTHON% -m uvicorn main:app --host 0.0.0.0 --port 8000"

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 启动前端
echo [3/3] 启动前端服务 (http://localhost:5173)...
start "LUCS Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ===========================================
echo  两个服务已启动！
echo  后端: http://localhost:8000/docs
echo  前端: http://localhost:5173
echo  按任意键关闭此窗口（服务继续运行）
echo ===========================================
pause >nul
