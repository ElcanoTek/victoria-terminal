#define MyAppName "Victoria"
#define MyAppVersion "1.0"
#define MyAppExeName "Victoria.exe"

[Setup]
AppId={{8F6B2C2B-21CC-4D66-877B-0E7D12FA8E3F}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
VersionInfoVersion={#MyAppVersion}.0
VersionInfoTextVersion={#MyAppVersion}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
OutputDir=..\dist
OutputBaseFilename=VictoriaSetup
Compression=lzma
SolidCompression=yes
SetupIconFile=..\assets\icon.ico

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Victoria"; Flags: nowait postinstall skipifsilent
