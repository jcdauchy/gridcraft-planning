@echo off
rem Mode 2 - live MCP: opens the GridCraft window with the JSON control channel on a port,
rem and registers an MCP server (name: gridcraft-live) bridged to that window.
rem Usage: gridcraft-mcp-live.bat [workbook.xlsx] [port]
rem Defaults: Planning seniors - couleurs.xlsx next to this script, port 7979.
setlocal
set "HERE=%~dp0"
set "FILE=%~1"
set "PORT=%~2"
if "%FILE%"=="" set "FILE=%HERE%Planning seniors - couleurs.xlsx"
if "%PORT%"=="" set "PORT=7979"

claude mcp remove --scope user gridcraft-live >nul 2>&1
claude mcp add --scope user gridcraft-live -- "%HERE%gridcraft-cli.exe" mcp --connect %PORT%
if errorlevel 1 (
  echo Registration failed: is the "claude" command on your PATH?
  pause
  exit /b 1
)

start "" "%HERE%gridcraft.exe" "%FILE%" --control %PORT%

echo.
echo GridCraft is starting with %FILE%
echo Control channel on port %PORT%.
echo Restart Claude Code (or open a new session) to get the gridcraft-live tools,
echo and keep the GridCraft window open while you use them.
pause
