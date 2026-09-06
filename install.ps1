[CmdletBinding()]
param(
    [string]$Python
)

$ErrorActionPreference = 'Stop'
$rootDir = Split-Path -Parent $PSCommandPath
$venvDir = Join-Path $rootDir '.venv'

if ($Python) {
    $pythonCommand = $Python
    $pythonPrefix = @()
} elseif ($pyLauncher = Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCommand = $pyLauncher.Source
    $pythonPrefix = @('-3')
} elseif ($pythonExe = Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCommand = $pythonExe.Source
    $pythonPrefix = @()
} else {
    throw 'Python 3.10 ou superior não foi encontrado.'
}

& $pythonCommand @pythonPrefix -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else "Python 3.10 ou superior é obrigatório.")'
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

& $pythonCommand @pythonPrefix -m venv --without-pip $venvDir
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

$venvPython = Join-Path $venvDir 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath $venvPython)) {
    throw 'Não foi possível localizar o Python do ambiente virtual.'
}

$sitePackages = Join-Path $venvDir 'Lib\site-packages'
& $pythonCommand @pythonPrefix -m pip install --upgrade --target $sitePackages -r (Join-Path $rootDir 'requirements.txt')
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host 'Instalação concluída. Teste com:'
Write-Host "  & `"$venvPython`" scripts\business_plan_pdf.py --input examples\cimol.sample.json --output plano_negocios.pdf"
