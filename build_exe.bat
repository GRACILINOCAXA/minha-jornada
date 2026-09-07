@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set "PYTHON=.venv\Scripts\python.exe"
) else (
    set "PYTHON=python"
)

%PYTHON% -m pip install -r requirements-desktop.txt
if errorlevel 1 exit /b 1
%PYTHON% -c "import PyInstaller, webview; print('Dependencias OK')"
if errorlevel 1 exit /b 1

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

%PYTHON% -m PyInstaller --clean --noconfirm MinhaJornada.spec
if errorlevel 1 exit /b 1

echo.
echo Build concluido: dist\MinhaJornada.exe
endlocal