# Histórico de versões

Todas as mudanças do Zircon que o usuário percebe, da mais nova para a mais antiga. As versões seguem o padrão maior.menor.correção: o último número muda em correções, o do meio quando entra algo novo.

## 0.3.1 (17/10/2026)

- Linux: o programa fechava ao abrir no Pop!_OS e no Ubuntu 22.04 ou mais novo, por falta de bibliotecas gráficas (X11/xcb). Agora elas vêm dentro do pacote.
- Linux: ícone e atalho no menu de aplicativos (GNOME, KDE, COSMIC).
- Ícone novo do programa no Windows, Mac e Linux.
- A montagem do pacote Linux agora abre o programa numa tela virtual para conferir que ele inicia.

## 0.3.0 (17/10/2026)

- Roda em computadores de 2010 em diante:
  - Windows 7 SP1, 8.1, 10 e 11, em 64 e 32 bits;
  - Linux com Ubuntu 20.04, Debian 10 ou mais novos;
  - Mac com Intel a partir do macOS 10.13 (High Sierra).
- Mac com chip Apple continua com a montagem moderna (macOS 14 ou mais novo).
- Os cálculos são os mesmos; os testes rodam nas duas montagens.
- Removida a montagem separada para Mac com Intel no macOS 13, que travava a fila de montagem do GitHub.

## 0.2.0 (17/10/2026)

- Correção de Pb comum pelo 204Pb, com composição fixa (Canyon Diablo) ou de Stacey e Kramers (1975), conferida com o IsoplotR.
- Isócronas Pb-Pb (inversa, como no IsoplotR) e Th-Pb, conferidas com o IsoplotR.
- Diagrama de isócrona com elipses, em gráfico e na exportação.
- Aviso quando nenhum grão passa no limite de discordância, em vez de erro.

## 0.1.0 (17/10/2026)

Primeira versão.

- Programa de desktop que funciona sem internet, com projetos `.zircon` (Arquivo > Novo, Abrir, Salvar).
- Instalador do Windows com assistente: licença, formulário opcional, componentes, atalhos e associação de arquivos.
- Pacotes para Linux (.deb e .tar.gz) e Mac (.dmg).
- Importação de xlsx, xls, ods, csv e txt, com detecção de vírgula ou ponto, erros em 2σ ou %, linhas de título e cabeçalho em duas linhas.
- Idades por grão, discordância, melhor idade, média ponderada (MSWD, efeitos aleatórios, Chauvenet generalizado), idade concórdia e discórdia, conferidas com o IsoplotR 7.1.
- Cores por classe, por população de idade ou por grupos escolhidos pelo usuário.
- Exportação para publicação: figuras (PNG, TIFF, PDF, SVG, EPS), Excel formatado, gráficos interativos em HTML, dados para repositório e texto de metodologia em português e inglês com referências ABNT.
- Registro voluntário, sem conexão com a internet.
