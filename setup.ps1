param(
    [Parameter(Mandatory = $true, HelpMessage = "火山方舟 API Key")]
    [string]$ApiKey,
    [string]$Model = "deepseek-v4-pro-260425"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "==> [1/4] 写入 .env 配置" -ForegroundColor Cyan
$envContent = @"
DOUBAO_API_KEY=$ApiKey
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
DOUBAO_MODEL=$Model
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
VECTOR_STORE_PATH=./vector_store/faiss_index
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K=4
"@
[System.IO.File]::WriteAllText("$PSScriptRoot\.env", $envContent)

Write-Host "==> [2/4] 激活虚拟环境" -ForegroundColor Cyan
.\.venv\Scripts\Activate.ps1

Write-Host "==> [3/4] 检查向量库" -ForegroundColor Cyan
if (-not (Test-Path "vector_store\faiss_index")) {
    Write-Host "  向量库不存在，开始构建..." -ForegroundColor Yellow
    python -m app.ingest
} else {
    Write-Host "  向量库已存在，跳过构建" -ForegroundColor Green
}

Write-Host "==> [4/4] 运行演示问答" -ForegroundColor Cyan
python scripts\demo.py

Write-Host ""
Write-Host "全部完成！启动 Web 界面：" -ForegroundColor Green
Write-Host "  .\start.ps1" -ForegroundColor Yellow
