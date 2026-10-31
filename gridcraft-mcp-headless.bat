@echo off
rem Mode 1 - headless MCP: Claude Code starts gridcraft-cli itself, no window is shown.
rem This script only registers the server (name: gridcraft) in the Claude Code user config.
rem Usage: gridcraft-mcp-headless.bat [workbook.xlsx]     (default: Planning seniors - couleurs.xlsx next to this script)
setlocal
set "HERE=%~dp0"
set "FILE=%~1"
if "%FILE%"=="" set "FILE=%HERE%Planning seniors - couleurs.xlsx"

claude mcp remove --scope user gridcraft >nul 2>&1
claude mcp add --scope user gridcraft -- "%HERE%gridcraft-cli.exe" mcp --in "%FILE%"
if errorlevel 1 (
  echo Registration failed: is the "claude" command on your PATH?
  pause
  exit /b 1
)

echo.
echo Registered with workbook: %FILE%
echo Restart Claude Code (or open a new session) to get the gridcraft tools.
pause
