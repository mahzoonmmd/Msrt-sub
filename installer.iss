[Setup]
AppName=MSRT
AppVersion=1.0
AppPublisher=MSRT
DefaultDirName={autopf}\MSRT
DefaultGroupName=MSRT
OutputDir=installer_output
OutputBaseFilename=MSRT_Setup_v1.0
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayName=MSRT
PrivilegesRequired=lowest
SetupIconFile=icon.ico
DisableProgramGroupPage=yes

[Tasks]
Name: "desktopicon"; Description: "Create desktop shortcut"; Flags: checkedonce

[Files]
Source: "dist\MSRT.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\MSRT"; Filename: "{app}\MSRT.exe"; IconFilename: "{app}\MSRT.exe"
Name: "{autodesktop}\MSRT"; Filename: "{app}\MSRT.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\MSRT.exe"; Description: "Launch MSRT"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\history.json"
