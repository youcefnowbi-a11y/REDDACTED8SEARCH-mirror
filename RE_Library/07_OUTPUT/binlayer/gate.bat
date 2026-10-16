@echo off
REM ===========================================================================
REM  gate.bat -- cmd-side gate for the Ghidra harness.
REM
REM  PowerShell-to-cmd.exe quoting is the unreliable link, so path handling
REM  lives entirely here and PowerShell passes only fixed tokens.
REM
REM  NOTE: this file must use REM, not #, for comments. A '#' first character
REM  is not a batch comment -- cmd tries to execute it, and %1/%2 substitution
REM  inside those lines silently corrupts the whole script. That cost one run.
REM
REM  %1 = target binary
REM  %2 = staged output path (MUST be space-free)
REM  %3 = ghidra script directory
REM  %4 = script name (optional)
REM ===========================================================================

set "GHIDRA=C:\tools\ghidra_12.1.4_PUBLIC"
set "TARGET=%~1"
set "STAGE=%~2"
set "SCRIPTDIR=%~3"
set "SCRIPT=%~4"
if "%SCRIPT%"=="" set "SCRIPT=DumpSyms.java"

if not exist "%TARGET%" (
  echo GATE_ERROR=target_not_found
  exit /b 3
)
if not exist "%SCRIPTDIR%\%SCRIPT%" (
  echo GATE_ERROR=script_not_found
  exit /b 4
)

set "PROJDIR=%TEMP%\ghproj_%RANDOM%%RANDOM%"
if not exist "%PROJDIR%" mkdir "%PROJDIR%"
if not exist "%PROJDIR%" (
  echo GATE_ERROR=projdir_not_created
  exit /b 5
)

cd /d "%GHIDRA%\support"
call analyzeHeadless.bat "%PROJDIR%" ghprobe -import "%TARGET%" -analysisTimeoutPerFile 1800 -scriptPath "%SCRIPTDIR%" -postScript "%SCRIPT%" "%STAGE%" <nul

set "RC=%ERRORLEVEL%"
rmdir /s /q "%PROJDIR%" 2>nul

if exist "%STAGE%" (
  echo GATE_STAGE_OK
) else (
  echo GATE_STAGE_MISSING
  if "%RC%"=="0" set "RC=7"
)
exit /b %RC%
