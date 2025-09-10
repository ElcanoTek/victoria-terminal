#define MyAppName "Victoria"
#define MyAppVersion "2025.9.8"
#define MyConfiguratorExeName "VictoriaConfigurator.exe"
#define MyTerminalExeName "VictoriaTerminal.exe"
#define MyBrowserExeName "VictoriaBrowser.exe"

[Setup]
AppId={{8F6B2C2B-21CC-4D66-877B-0E7D12FA8E3F}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
VersionInfoVersion={#MyAppVersion}.0
VersionInfoTextVersion={#MyAppVersion}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
UninstallDisplayIcon={app}\{#MyTerminalExeName}
OutputDir=..\dist
OutputBaseFilename=VictoriaSetup
Compression=lzma
SolidCompression=yes
SetupIconFile=..\assets\Victoria.ico

[Files]
Source: "..\dist\{#MyConfiguratorExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\{#MyTerminalExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\{#MyBrowserExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Victoria Configurator"; Filename: "{app}\{#MyConfiguratorExeName}"
Name: "{group}\Victoria Terminal"; Filename: "{app}\{#MyTerminalExeName}"
Name: "{group}\Victoria Browser"; Filename: "{app}\{#MyBrowserExeName}"
Name: "{commondesktop}\Victoria Terminal"; Filename: "{app}\{#MyTerminalExeName}";
Name: "{commondesktop}\Victoria Browser"; Filename: "{app}\{#MyBrowserExeName}";

[Run]
Filename: "{app}\{#MyTerminalExeName}"; Description: "Launch Victoria Terminal"; Flags: nowait postinstall skipifsilent
