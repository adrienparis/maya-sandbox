@echo off
setlocal

set "psCommand="(new-object -COM 'Shell.Application')^
.BrowseForFolder(0,'Choisissez le projet source',0,0).self.path""

for /f "usebackq delims=" %%I in (`powershell %psCommand%`) do set "srcFolder=%%I"

set "psCommand="(new-object -COM 'Shell.Application')^
.BrowseForFolder(0,'Choisissez le projet de destination',0,0).self.path""

for /f "usebackq delims=" %%I in (`powershell %psCommand%`) do set "destFolder=%%I"


set pythonPath="%UserProfile%\Documents\CreativeSeeds\ProjectDownloader.py"
set batchPath="%UserProfile%\Documents\CreativeSeeds\ProjectDownloader.bat"
set batchStartPath="%UserProfile%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\ProjectDownloader.bat"
set batchLocalPath=".\sync.bat"

if not exist "%UserProfile%\Documents\CreativeSeeds" mkdir "%UserProfile%\Documents\CreativeSeeds"
echo "C:/Program Files/Autodesk/Maya2020/bin/mayapy.exe" %pythonPath% "%srcFolder%" "%destFolder%" > %batchPath%
echo "C:/Program Files/Autodesk/Maya2020/bin/mayapy.exe" %pythonPath% "%srcFolder%" "%destFolder%" > %batchLocalPath%
if not exist "%pythonPath%" xcopy /s .\syncProject.py "%pythonPath%"

SCHTASKS /CREATE /SC DAILY /TN "CreativeSeeds\UpdateProjectDaily" /TR "%batchPath%" /ST 08:32
SCHTASKS /CREATE /SC ONLOGON /TN "CreativeSeeds\UpdateProjectLogOn" /TR "%batchPath%" /RU %USERNAME% /IT
