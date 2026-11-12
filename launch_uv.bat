@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

rem === Self-contained uv launcher ============================================
rem All state (uv cache, Python interpreter, model cache, temp files) stays
rem inside this folder under runtime\. Nothing touches your system Python.
set "UV_CACHE_DIR=%~dp0runtime\uv_cache"
set "UV_PYTHON_INSTALL_DIR=%~dp0runtime\python"
set "HF_HOME=%~dp0runtime\hf_cache"
set "GRADIO_TEMP_DIR=%~dp0runtime\gradio_tmp"
set "HF_HUB_DISABLE_SYMLINKS_WARNING=1"

where uv >nul 2>nul
if errorlevel 1 (
    echo [ERROR] uv was not found on PATH.
    echo         Install it once from https://docs.astral.sh/uv/  e.g. in PowerShell:
    echo         powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    pause
    exit /b 1
)

rem First run: uv creates .venv and installs the pinned dependencies automatically.
uv run scripts\launch.py %*
pause
endlocal
