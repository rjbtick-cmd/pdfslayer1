@echo off
echo ===========================================
echo     LAUNCHING PDFSLAYER WORKSPACE...
echo ===========================================

:: === EDIT THESE PATHS TO MATCH YOUR MACHINE ===
SET PROJECT_PATH=C:\Users\fezzl\Desktop\pdfslayer
SET OBSIDIAN_VAULT=C:\Users\fezzl\Obsidian\YourVault
SET CODE_PATH=C:\Users\fezzl\AppData\Local\Programs\Microsoft VS Code\Code.exe

:: === Open VS Code in project folder ===
echo Opening VS Code...
start "" "%CODE_PATH%" "%PROJECT_PATH%"

:: === Open Obsidian Vault (replace YourVault with your vault name) ===
echo Opening Obsidian...
start "" "obsidian://open?vault=YourVault"

:: === Open File Explorer to project ===
echo Opening File Explorer...
start "" explorer "%PROJECT_PATH%"

:: === Open PowerShell window in project ===
echo Opening PowerShell...
start "" powershell -noexit -command "cd '%PROJECT_PATH%'"

:: === Optional: Activate Python venv automatically (uncomment if you have .venv) ===
:: start "" powershell -noexit -command "cd '%PROJECT_PATH%'; .\.venv\Scripts\activate"

:: === Optional: Auto-run a command (example: npm run dev on sample.pdf) ===
:: start "" powershell -noexit -command "cd '%PROJECT_PATH%'; npm run dev -- C:\path\to\sample.pdf"

echo All tools launched!
echo ===========================================
