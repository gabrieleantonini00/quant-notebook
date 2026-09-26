# Run from PowerShell: .\Start-Notebook.ps1
$ErrorActionPreference = 'Stop'
$notebookPython = Get-Command python -ErrorAction SilentlyContinue
if ($notebookPython) {
    $notebookPythonPath = $notebookPython.Source
} else {
    $notebookPythonPath = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
}
if (-not (Test-Path -LiteralPath $notebookPythonPath)) {
    Write-Host 'Python was not found. Opening the notebook directly instead.'
    Start-Process (Join-Path $PSScriptRoot 'index.html')
    exit 0
}
Write-Host 'Your notebook: http://127.0.0.1:8000'
Write-Host 'Press Ctrl+C to stop the local server.'
& $notebookPythonPath (Join-Path $PSScriptRoot 'serve.py')
