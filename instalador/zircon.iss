; Instalador do Zircon para Windows (Inno Setup 6).
; Compilar: iscc /DVersao=0.1.0 instalador\zircon.iss
; O assistente tem: boas-vindas, licença, formulário opcional do usuário,
; pasta, componentes, tarefas, confirmação e conclusão.
; Nada é enviado pela internet: o formulário fica salvo só neste computador.

#ifndef Versao
  #define Versao "0.1.0"
#endif

[Setup]
AppId={{6E7A1F2C-3B8D-4C51-9E0A-7D2B5C4F1A90}
AppName=Zircon
AppVersion={#Versao}
AppVerName=Zircon {#Versao}
AppPublisher=Cibele (cibelegeologia)
AppPublisherURL=https://github.com/cibelegeologia/zircon
AppSupportURL=https://github.com/cibelegeologia/zircon/issues
DefaultDirName={autopf}\Zircon
DefaultGroupName=Zircon
PrivilegesRequiredOverridesAllowed=dialog
LicenseFile=licenca_instalador.txt
OutputDir=..\dist
OutputBaseFilename=Zircon-{#Versao}-instalador
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ChangesAssociations=yes
UninstallDisplayName=Zircon {#Versao}
ShowLanguageDialog=auto

[Languages]
Name: "pt"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "en"; MessagesFile: "compiler:Default.isl"

[Types]
Name: "completa"; Description: "Instalação completa"
Name: "minima"; Description: "Só o programa"
Name: "personalizada"; Description: "Personalizada"; Flags: iscustom

[Components]
Name: "programa"; Description: "Zircon (programa)"; Types: completa minima personalizada; Flags: fixed
Name: "exemplos"; Description: "Planilhas de exemplo para aprender"; Types: completa
Name: "documentos"; Description: "Referências bibliográficas (ABNT) e especificação dos métodos"; Types: completa

[Tasks]
Name: "atalho"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos:"
Name: "associar"; Description: "Abrir arquivos .zircon com o Zircon"; GroupDescription: "Arquivos:"

[Files]
Source: "..\dist\Zircon\*"; DestDir: "{app}"; Components: programa; Flags: recursesubdirs ignoreversion
Source: "..\testes\modulo2\entrada\UPb1.xlsx"; DestDir: "{userdocs}\Zircon\Exemplos"; Components: exemplos
Source: "..\testes\modulo2\entrada\UPb2.xlsx"; DestDir: "{userdocs}\Zircon\Exemplos"; Components: exemplos
Source: "..\testes\modulo2\entrada\DZ_detritico_so_idades.xlsx"; DestDir: "{userdocs}\Zircon\Exemplos"; Components: exemplos
Source: "..\testes\modulo2\entrada\UPb1_estilo_laboratorio_latin1.csv"; DestDir: "{userdocs}\Zircon\Exemplos"; Components: exemplos
Source: "..\docs\referencias_abnt.md"; DestDir: "{app}\docs"; Components: documentos
Source: "..\docs\especificacao_e_bibliografia.md"; DestDir: "{app}\docs"; Components: documentos

[Icons]
Name: "{group}\Zircon"; Filename: "{app}\Zircon.exe"
Name: "{group}\Exemplos do Zircon"; Filename: "{userdocs}\Zircon\Exemplos"; Components: exemplos
Name: "{group}\Desinstalar o Zircon"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Zircon"; Filename: "{app}\Zircon.exe"; Tasks: atalho

[Registry]
Root: HKA; Subkey: "Software\Classes\.zircon"; ValueType: string; ValueData: "Zircon.Projeto"; Flags: uninsdeletevalue; Tasks: associar
Root: HKA; Subkey: "Software\Classes\Zircon.Projeto"; ValueType: string; ValueData: "Projeto do Zircon"; Flags: uninsdeletekey; Tasks: associar
Root: HKA; Subkey: "Software\Classes\Zircon.Projeto\DefaultIcon"; ValueType: string; ValueData: "{app}\Zircon.exe,0"; Tasks: associar
Root: HKA; Subkey: "Software\Classes\Zircon.Projeto\shell\open\command"; ValueType: string; ValueData: """{app}\Zircon.exe"" ""%1"""; Tasks: associar

[Run]
Filename: "{app}\Zircon.exe"; Parameters: "--registrar"; Description: "Abrir o registro voluntário (você confere o texto antes de enviar)"; Flags: nowait postinstall skipifsilent unchecked; Check: QuerRegistrar
Filename: "{app}\Zircon.exe"; Description: "Abrir o Zircon agora"; Flags: nowait postinstall skipifsilent

[Code]
var
  PaginaUsuario: TInputQueryWizardPage;
  CaixaRegistro: TNewCheckBox;

procedure InitializeWizard;
begin
  PaginaUsuario := CreateInputQueryPage(wpLicense,
    'Sobre você (opcional)',
    'Estas informações ficam só neste computador.',
    'Todos os campos são opcionais. O Zircon não se conecta à internet e não envia nada sozinho. ' +
    'Se quiser se registrar, no fim da instalação você pode abrir o registro, conferir o texto e decidir se envia.');
  PaginaUsuario.Add('Nome:', False);
  PaginaUsuario.Add('Instituição:', False);
  PaginaUsuario.Add('País:', False);
  PaginaUsuario.Add('E-mail (para avisos de nova versão):', False);
  PaginaUsuario.Add('Para que vai usar o Zircon:', False);

  CaixaRegistro := TNewCheckBox.Create(PaginaUsuario);
  CaixaRegistro.Parent := PaginaUsuario.Surface;
  CaixaRegistro.Top := PaginaUsuario.Edits[4].Top + PaginaUsuario.Edits[4].Height + ScaleY(16);
  CaixaRegistro.Width := PaginaUsuario.SurfaceWidth;
  CaixaRegistro.Caption := 'Quero me registrar como usuário (voluntário)';
  CaixaRegistro.Checked := False;
end;

function QuerRegistrar: Boolean;
begin
  Result := CaixaRegistro.Checked;
end;

function JsonTexto(S: String): String;
begin
  StringChangeEx(S, '\', '\\', True);
  StringChangeEx(S, '"', '\"', True);
  Result := '"' + S + '"';
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Pasta, Json: String;
begin
  if CurStep = ssPostInstall then
  begin
    { Mesmo local que o programa usa (QStandardPaths AppDataLocation) }
    Pasta := ExpandConstant('{userappdata}\Zircon\Zircon');
    ForceDirectories(Pasta);
    Json := '{' + #13#10 +
      '  "nome": ' + JsonTexto(PaginaUsuario.Values[0]) + ',' + #13#10 +
      '  "instituicao": ' + JsonTexto(PaginaUsuario.Values[1]) + ',' + #13#10 +
      '  "pais": ' + JsonTexto(PaginaUsuario.Values[2]) + ',' + #13#10 +
      '  "email": ' + JsonTexto(PaginaUsuario.Values[3]) + ',' + #13#10 +
      '  "uso": ' + JsonTexto(PaginaUsuario.Values[4]) + #13#10 + '}';
    if not FileExists(Pasta + '\registro.json') then
      SaveStringToFile(Pasta + '\registro.json', Json, False);
  end;
end;
