param(
    [ValidateSet("web", "api")]
    [string]$Mode = "web"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".env")) {
    Write-Host "请先运行: .\setup.ps1 -ApiKey `"你的API_KEY`"" -ForegroundColor Red
    exit 1
}

.\.venv\Scripts\Activate.ps1

if ($Mode -eq "web") {
    Write-Host "启动 Streamlit 界面 -> http://localhost:8501" -ForegroundColor Green
    streamlit run streamlit_app.py
} else {
    Write-Host "启动 FastAPI 服务 -> http://localhost:8000/docs" -ForegroundColor Green
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}
