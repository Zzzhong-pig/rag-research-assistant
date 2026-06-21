param(
    [Parameter(Mandatory = $true)]
    [string]$GitHubUsername,
    [string]$RepoName = "rag-research-assistant"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$remote = "https://github.com/$GitHubUsername/$RepoName.git"

Write-Host "请先在浏览器创建空仓库（不要勾选 README）：" -ForegroundColor Yellow
Write-Host "  https://github.com/new?repo=$RepoName" -ForegroundColor Cyan
Write-Host ""
Read-Host "创建完成后按 Enter 继续"

git -c safe.directory=F:/RAG_Project remote remove origin 2>$null
git -c safe.directory=F:/RAG_Project remote add origin $remote
git -c safe.directory=F:/RAG_Project push -u origin main

Write-Host ""
Write-Host "上传成功！仓库地址：" -ForegroundColor Green
Write-Host "  https://github.com/$GitHubUsername/$RepoName" -ForegroundColor Cyan
