@echo off
REM One-click runner: drop PDFs into the pdfs/ folder, then double-click this file.

setlocal enabledelayedexpansion
set "PROJECT_DIR=%~dp0"
set "PDF_DIR=%PROJECT_DIR%pdfs"

REM Ensure pdfs folder exists
if not exist "%PDF_DIR%" (
  mkdir "%PDF_DIR%"
  echo [info] Created folder: "%PDF_DIR%"
)

REM Determine target output (Obsidian vault Notes or fallback)
if not "%OBSIDIAN_VAULT%"=="" (
  set "TARGET_BASE=%OBSIDIAN_VAULT%"
) else (
  set "TARGET_BASE=%PROJECT_DIR%output"
  echo [info] OBSIDIAN_VAULT not set; using fallback: "%TARGET_BASE%"
)
set "NOTES_DIR=%TARGET_BASE%\Notes"
if not exist "%NOTES_DIR%" mkdir "%NOTES_DIR%"

REM Add Node.js to PATH for this session
set "PATH=%ProgramFiles%\nodejs;%PATH%"

REM Prefer npm.cmd from standard install
set "NPM_CMD=npm"
if exist "%ProgramFiles%\nodejs\npm.cmd" set "NPM_CMD=%ProgramFiles%\nodejs\npm.cmd"

REM Prefer py on Windows; CLI will also fallback internally
set "PYTHON_BIN=py"

REM Guard: if no PDFs present, prompt user
dir /b "%PDF_DIR%\*.pdf" >nul 2>&1
if errorlevel 1 (
  echo [warn] No PDFs found in "%PDF_DIR%".
  echo [warn] Drop PDFs into that folder, then double-click this file again.
  goto :eof
)

echo [info] Writing outputs to "%NOTES_DIR%"
echo [info] Processing PDFs in "%PDF_DIR%"
echo.

REM Loop through PDFs and run the extractor
for %%f in ("%PDF_DIR%\*.pdf") do (
  echo [run] %%~nxf
  "%NPM_CMD%" run dev -- "%%f"
  echo.
)

echo [done] Finished. Check: "%NOTES_DIR%" for the extracted JSON and Markdown.
endlocal
