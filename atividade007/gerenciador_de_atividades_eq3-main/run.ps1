# Sobe a Atividade 007: cria o ambiente, instala dependências e inicia o servidor.
# Uso: .\run.ps1  |  .\run.ps1 -Reset (recria dados)  |  .\run.ps1 -Test (testa e sai)
[CmdletBinding()]
param(
    [switch]$Reset,
    [switch]$Test,
    [switch]$NoSeed
)

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

Write-Host "=== Atividade 007 - Gerenciador de Atividades (Equipe 3) ===" -ForegroundColor Cyan

# 1) Localiza o Python
$python = $null
foreach ($cand in @("py", "python", "python3")) {
    $cmd = Get-Command $cand -ErrorAction SilentlyContinue
    if ($cmd) { $python = $cmd.Source; break }
}
if (-not $python) {
    throw "Python nao encontrado no PATH. Instale o Python 3 (python.org) e tente novamente."
}
Write-Host "Python: $python"

# 2) Ambiente virtual
$venv = Join-Path $PSScriptRoot ".venv"
$venvPy = Join-Path $venv "Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
    Write-Host "Criando ambiente virtual em .venv ..." -ForegroundColor Yellow
    & $python -m venv $venv
}

# 3) Dependências
Write-Host "Instalando dependencias ..." -ForegroundColor Yellow
& $venvPy -m pip install --upgrade pip --quiet
& $venvPy -m pip install -r (Join-Path $PSScriptRoot "requirements.txt") --quiet

# 4) Dados de exemplo
if (-not $NoSeed) {
    if ($Reset) {
        Write-Host "Populando o banco (reset) ..." -ForegroundColor Yellow
        & $venvPy (Join-Path $PSScriptRoot "seed.py") --reset
    } else {
        Write-Host "Populando o banco ..." -ForegroundColor Yellow
        & $venvPy (Join-Path $PSScriptRoot "seed.py")
    }
}

# 5) Testes
if ($Test) {
    Write-Host "Rodando testes ..." -ForegroundColor Yellow
    & $venvPy (Join-Path $PSScriptRoot "test_app.py")
    exit $LASTEXITCODE
}

# 6) Servidor
Write-Host "Servidor em http://127.0.0.1:5000  (Ctrl+C para parar)" -ForegroundColor Green
& $venvPy (Join-Path $PSScriptRoot "app.py")
