; Instalador do Zircon para Windows (Inno Setup 6).
; Compilar: iscc /DVersao=0.1.0 instalador\zircon.iss
; O assistente tem: boas-vindas, licença, formulário opcional do usuário,
; pasta, componentes, tarefas, confirmação e conclusão.
; Nada é enviado pela internet: o formulário fica salvo só neste computador.

#ifndef Versao
  #define Versao "0.1.0"
#endif
#ifndef Arq
  #define Arq "x64"
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
OutputBaseFilename=Zircon-{#Versao}-instalador-windows-{#Arq}
MinVersion=6.1sp1
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=zircon.ico
UninstallDisplayIcon={app}\Zircon.exe
ChangesAssociations=yes
UninstallDisplayName=Zircon {#Versao}
ShowLanguageDialog=auto
#if Arq == "x64"
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
#endif

[Languages]
Name: "pt"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "ptpt"; MessagesFile: "compiler:Languages\Portuguese.isl"
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "fr"; MessagesFile: "compiler:Languages\French.isl"
Name: "de"; MessagesFile: "compiler:Languages\German.isl"

[CustomMessages]
pt.JaInstalado=O Zircon %1 já está instalado neste computador.%n%nDeseja substituí-lo pela versão %2? Seus projetos e preferências serão mantidos.
ptpt.JaInstalado=O Zircon %1 já está instalado neste computador.%n%nPretende substituí-lo pela versão %2? Os seus projetos e preferências serão mantidos.
en.JaInstalado=Zircon %1 is already installed on this computer.%n%nReplace it with version %2? Your projects and preferences will be kept.
es.JaInstalado=Zircon %1 ya está instalado en este equipo.%n%n¿Desea reemplazarlo por la versión %2? Sus proyectos y preferencias se conservarán.
fr.JaInstalado=Zircon %1 est déjà installé sur cet ordinateur.%n%nLe remplacer par la version %2 ? Vos projets et préférences seront conservés.
de.JaInstalado=Zircon %1 ist auf diesem Computer bereits installiert.%n%nDurch Version %2 ersetzen? Ihre Projekte und Einstellungen bleiben erhalten.
pt.MesmaVersao=O Zircon %1 já está instalado neste computador.%n%nDeseja instalá-lo de novo?
ptpt.MesmaVersao=O Zircon %1 já está instalado neste computador.%n%nPretende instalá-lo novamente?
en.MesmaVersao=Zircon %1 is already installed on this computer.%n%nInstall it again?
es.MesmaVersao=Zircon %1 ya está instalado en este equipo.%n%n¿Desea instalarlo de nuevo?
fr.MesmaVersao=Zircon %1 est déjà installé sur cet ordinateur.%n%nLe réinstaller ?
de.MesmaVersao=Zircon %1 ist auf diesem Computer bereits installiert.%n%nErneut installieren?
pt.TipoCompleta=Instalação completa
ptpt.TipoCompleta=Instalação completa
en.TipoCompleta=Full installation
es.TipoCompleta=Instalación completa
fr.TipoCompleta=Installation complète
de.TipoCompleta=Vollständige Installation
pt.TipoMinima=Só o programa
ptpt.TipoMinima=Apenas o programa
en.TipoMinima=Program only
es.TipoMinima=Solo el programa
fr.TipoMinima=Programme seul
de.TipoMinima=Nur das Programm
pt.TipoPersonalizada=Personalizada
ptpt.TipoPersonalizada=Personalizada
en.TipoPersonalizada=Custom
es.TipoPersonalizada=Personalizada
fr.TipoPersonalizada=Personnalisée
de.TipoPersonalizada=Benutzerdefiniert
pt.CompPrograma=Zircon (programa)
ptpt.CompPrograma=Zircon (programa)
en.CompPrograma=Zircon (program)
es.CompPrograma=Zircon (programa)
fr.CompPrograma=Zircon (programme)
de.CompPrograma=Zircon (Programm)
pt.CompExemplos=Planilhas de exemplo para aprender
ptpt.CompExemplos=Folhas de cálculo de exemplo para aprender
en.CompExemplos=Example spreadsheets for learning
es.CompExemplos=Hojas de cálculo de ejemplo para aprender
fr.CompExemplos=Feuilles de calcul d'exemple pour apprendre
de.CompExemplos=Beispieltabellen zum Lernen
pt.CompDocumentos=Referências bibliográficas (ABNT) e especificação dos métodos
ptpt.CompDocumentos=Referências bibliográficas (ABNT) e especificação dos métodos
en.CompDocumentos=Bibliographic references (ABNT) and method specification
es.CompDocumentos=Referencias bibliográficas (ABNT) y especificación de los métodos
fr.CompDocumentos=Références bibliographiques (ABNT) et spécification des méthodes
de.CompDocumentos=Literaturverzeichnis (ABNT) und Methodenbeschreibung
pt.TarefaAtalho=Criar atalho na área de trabalho
ptpt.TarefaAtalho=Criar atalho no ambiente de trabalho
en.TarefaAtalho=Create a desktop shortcut
es.TarefaAtalho=Crear acceso directo en el escritorio
fr.TarefaAtalho=Créer un raccourci sur le bureau
de.TarefaAtalho=Verknüpfung auf dem Desktop erstellen
pt.GrupoAtalhos=Atalhos:
ptpt.GrupoAtalhos=Atalhos:
en.GrupoAtalhos=Shortcuts:
es.GrupoAtalhos=Accesos directos:
fr.GrupoAtalhos=Raccourcis :
de.GrupoAtalhos=Verknüpfungen:
pt.TarefaAssociar=Abrir arquivos .zircon com o Zircon
ptpt.TarefaAssociar=Abrir ficheiros .zircon com o Zircon
en.TarefaAssociar=Open .zircon files with Zircon
es.TarefaAssociar=Abrir archivos .zircon con Zircon
fr.TarefaAssociar=Ouvrir les fichiers .zircon avec Zircon
de.TarefaAssociar=.zircon-Dateien mit Zircon öffnen
pt.GrupoArquivos=Arquivos:
ptpt.GrupoArquivos=Ficheiros:
en.GrupoArquivos=Files:
es.GrupoArquivos=Archivos:
fr.GrupoArquivos=Fichiers :
de.GrupoArquivos=Dateien:
pt.IconeExemplos=Exemplos do Zircon
ptpt.IconeExemplos=Exemplos do Zircon
en.IconeExemplos=Zircon examples
es.IconeExemplos=Ejemplos de Zircon
fr.IconeExemplos=Exemples Zircon
de.IconeExemplos=Zircon-Beispiele
pt.IconeDesinstalar=Desinstalar o Zircon
ptpt.IconeDesinstalar=Desinstalar o Zircon
en.IconeDesinstalar=Uninstall Zircon
es.IconeDesinstalar=Desinstalar Zircon
fr.IconeDesinstalar=Désinstaller Zircon
de.IconeDesinstalar=Zircon deinstallieren
pt.TipoArquivo=Projeto do Zircon
ptpt.TipoArquivo=Projeto do Zircon
en.TipoArquivo=Zircon project
es.TipoArquivo=Proyecto de Zircon
fr.TipoArquivo=Projet Zircon
de.TipoArquivo=Zircon-Projekt
pt.AbrirRegistro=Abrir o registro voluntário (você confere o texto antes de enviar)
ptpt.AbrirRegistro=Abrir o registo voluntário (confere o texto antes de enviar)
en.AbrirRegistro=Open the voluntary registration (you check the text before sending)
es.AbrirRegistro=Abrir el registro voluntario (revisa el texto antes de enviarlo)
fr.AbrirRegistro=Ouvrir l'enregistrement volontaire (vous vérifiez le texte avant l'envoi)
de.AbrirRegistro=Freiwillige Registrierung öffnen (Sie prüfen den Text vor dem Senden)
pt.AbrirAgora=Abrir o Zircon agora
ptpt.AbrirAgora=Abrir o Zircon agora
en.AbrirAgora=Open Zircon now
es.AbrirAgora=Abrir Zircon ahora
fr.AbrirAgora=Ouvrir Zircon maintenant
de.AbrirAgora=Zircon jetzt öffnen
pt.FormTitulo=Sobre você (opcional)
ptpt.FormTitulo=Sobre si (opcional)
en.FormTitulo=About you (optional)
es.FormTitulo=Sobre usted (opcional)
fr.FormTitulo=À propos de vous (facultatif)
de.FormTitulo=Über Sie (optional)
pt.FormSubtitulo=Estas informações ficam só neste computador.
ptpt.FormSubtitulo=Estas informações ficam apenas neste computador.
en.FormSubtitulo=This information stays on this computer only.
es.FormSubtitulo=Esta información se queda solo en este equipo.
fr.FormSubtitulo=Ces informations restent uniquement sur cet ordinateur.
de.FormSubtitulo=Diese Angaben bleiben nur auf diesem Computer.
pt.FormTexto=Todos os campos são opcionais. O Zircon não se conecta à internet e não envia nada sozinho. Se quiser se registrar, no fim da instalação você pode abrir o registro, conferir o texto e decidir se envia.
ptpt.FormTexto=Todos os campos são opcionais. O Zircon não se liga à internet e não envia nada sozinho. Se quiser registar-se, no fim da instalação pode abrir o registo, conferir o texto e decidir se o envia.
en.FormTexto=All fields are optional. Zircon does not connect to the internet and never sends anything by itself. If you want to register, at the end of the installation you can open the registration, check the text and decide whether to send it.
es.FormTexto=Todos los campos son opcionales. Zircon no se conecta a internet y no envía nada por sí solo. Si desea registrarse, al final de la instalación puede abrir el registro, revisar el texto y decidir si lo envía.
fr.FormTexto=Tous les champs sont facultatifs. Zircon ne se connecte pas à Internet et n'envoie rien de lui-même. Si vous souhaitez vous enregistrer, à la fin de l'installation vous pourrez ouvrir l'enregistrement, vérifier le texte et décider de l'envoyer ou non.
de.FormTexto=Alle Felder sind optional. Zircon verbindet sich nicht mit dem Internet und sendet nichts von selbst. Wenn Sie sich registrieren möchten, können Sie am Ende der Installation die Registrierung öffnen, den Text prüfen und entscheiden, ob Sie ihn senden.
pt.CampoNome=Nome:
ptpt.CampoNome=Nome:
en.CampoNome=Name:
es.CampoNome=Nombre:
fr.CampoNome=Nom :
de.CampoNome=Name:
pt.CampoInstituicao=Instituição:
ptpt.CampoInstituicao=Instituição:
en.CampoInstituicao=Institution:
es.CampoInstituicao=Institución:
fr.CampoInstituicao=Institution :
de.CampoInstituicao=Institution:
pt.CampoPais=País:
ptpt.CampoPais=País:
en.CampoPais=Country:
es.CampoPais=País:
fr.CampoPais=Pays :
de.CampoPais=Land:
pt.CampoEmail=E-mail (para avisos de nova versão):
ptpt.CampoEmail=E-mail (para avisos de nova versão):
en.CampoEmail=E-mail (for new version notices):
es.CampoEmail=Correo electrónico (para avisos de nuevas versiones):
fr.CampoEmail=E-mail (pour les annonces de nouvelle version) :
de.CampoEmail=E-Mail (für Hinweise auf neue Versionen):
pt.CampoUso=Para que vai usar o Zircon:
ptpt.CampoUso=Para que vai usar o Zircon:
en.CampoUso=What you will use Zircon for:
es.CampoUso=Para qué usará Zircon:
fr.CampoUso=À quoi servira Zircon :
de.CampoUso=Wofür Sie Zircon verwenden:
pt.QueroRegistrar=Quero me registrar como usuário (voluntário)
ptpt.QueroRegistrar=Quero registar-me como utilizador (voluntário)
en.QueroRegistrar=I want to register as a user (voluntary)
es.QueroRegistrar=Quiero registrarme como usuario (voluntario)
fr.QueroRegistrar=Je veux m'enregistrer comme utilisateur (volontaire)
de.QueroRegistrar=Ich möchte mich als Nutzer registrieren (freiwillig)
pt.IdiomaPrograma=pt_BR
ptpt.IdiomaPrograma=pt_PT
en.IdiomaPrograma=en
es.IdiomaPrograma=es
fr.IdiomaPrograma=fr
de.IdiomaPrograma=de

[Types]
Name: "completa"; Description: "{cm:TipoCompleta}"
Name: "minima"; Description: "{cm:TipoMinima}"
Name: "personalizada"; Description: "{cm:TipoPersonalizada}"; Flags: iscustom

[Components]
Name: "programa"; Description: "{cm:CompPrograma}"; Types: completa minima personalizada; Flags: fixed
Name: "exemplos"; Description: "{cm:CompExemplos}"; Types: completa
Name: "documentos"; Description: "{cm:CompDocumentos}"; Types: completa

[Tasks]
Name: "atalho"; Description: "{cm:TarefaAtalho}"; GroupDescription: "{cm:GrupoAtalhos}"
Name: "associar"; Description: "{cm:TarefaAssociar}"; GroupDescription: "{cm:GrupoArquivos}"

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
Name: "{group}\{cm:IconeExemplos}"; Filename: "{userdocs}\Zircon\Exemplos"; Components: exemplos
Name: "{group}\{cm:IconeDesinstalar}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Zircon"; Filename: "{app}\Zircon.exe"; Tasks: atalho

[Registry]
Root: HKA; Subkey: "Software\Classes\.zircon"; ValueType: string; ValueData: "Zircon.Projeto"; Flags: uninsdeletevalue; Tasks: associar
Root: HKA; Subkey: "Software\Classes\Zircon.Projeto"; ValueType: string; ValueData: "{cm:TipoArquivo}"; Flags: uninsdeletekey; Tasks: associar
Root: HKA; Subkey: "Software\Classes\Zircon.Projeto\DefaultIcon"; ValueType: string; ValueData: "{app}\Zircon.exe,0"; Tasks: associar
Root: HKA; Subkey: "Software\Classes\Zircon.Projeto\shell\open\command"; ValueType: string; ValueData: """{app}\Zircon.exe"" ""%1"""; Tasks: associar

; O programa abre no idioma escolhido no instalador (o usuário pode mudar no menu Idioma).
; Mesmo lugar onde o programa guarda as preferências (QSettings).
Root: HKCU; Subkey: "Software\Zircon\Zircon"; ValueType: string; ValueName: "idioma"; ValueData: "{cm:IdiomaPrograma}"; Flags: createvalueifdoesntexist

[Run]
Filename: "{app}\Zircon.exe"; Parameters: "--registrar"; Description: "{cm:AbrirRegistro}"; Flags: nowait postinstall skipifsilent unchecked; Check: QuerRegistrar
Filename: "{app}\Zircon.exe"; Description: "{cm:AbrirAgora}"; Flags: nowait postinstall skipifsilent

[Code]
const
  ChaveDesinstalar = 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{6E7A1F2C-3B8D-4C51-9E0A-7D2B5C4F1A90}_is1';

var
  PaginaUsuario: TInputQueryWizardPage;
  CaixaRegistro: TNewCheckBox;

{ Versão do Zircon já instalada (vazio se não houver) }
function VersaoInstalada: String;
begin
  Result := '';
  if not RegQueryStringValue(HKCU, ChaveDesinstalar, 'DisplayVersion', Result) then
    if not RegQueryStringValue(HKLM, ChaveDesinstalar, 'DisplayVersion', Result) then
      if IsWin64 then
        RegQueryStringValue(HKLM64, ChaveDesinstalar, 'DisplayVersion', Result);
end;

{ Avisa que há uma versão instalada e pergunta se substitui }
function InitializeSetup: Boolean;
var
  Antiga, Texto: String;
begin
  Result := True;
  Antiga := VersaoInstalada;
  if (Antiga = '') or WizardSilent then
    Exit;
  if Antiga = '{#Versao}' then
    Texto := FmtMessage(CustomMessage('MesmaVersao'), [Antiga])
  else
    Texto := FmtMessage(CustomMessage('JaInstalado'), [Antiga, '{#Versao}']);
  Result := MsgBox(Texto, mbConfirmation, MB_YESNO) = IDYES;
end;

procedure InitializeWizard;
begin
  PaginaUsuario := CreateInputQueryPage(wpLicense,
    CustomMessage('FormTitulo'), CustomMessage('FormSubtitulo'), CustomMessage('FormTexto'));
  PaginaUsuario.Add(CustomMessage('CampoNome'), False);
  PaginaUsuario.Add(CustomMessage('CampoInstituicao'), False);
  PaginaUsuario.Add(CustomMessage('CampoPais'), False);
  PaginaUsuario.Add(CustomMessage('CampoEmail'), False);
  PaginaUsuario.Add(CustomMessage('CampoUso'), False);

  CaixaRegistro := TNewCheckBox.Create(PaginaUsuario);
  CaixaRegistro.Parent := PaginaUsuario.Surface;
  CaixaRegistro.Top := PaginaUsuario.Edits[4].Top + PaginaUsuario.Edits[4].Height + ScaleY(16);
  CaixaRegistro.Width := PaginaUsuario.SurfaceWidth;
  CaixaRegistro.Caption := CustomMessage('QueroRegistrar');
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
