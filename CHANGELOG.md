# Histórico de versões

Todas as mudanças do Zircon que o usuário percebe, da mais nova para a mais antiga. As versões seguem o padrão maior.menor.correção: o último número muda em correções, o do meio quando entra algo novo.

## 0.5.0 (17/10/2026)

Acessibilidade. Tudo é opcional e fica guardado no computador de cada usuário.

- Menu Acessibilidade: tamanho da letra (normal, grande, muito grande, enorme; também com Ctrl + e Ctrl -) e tema (como o sistema, claro, escuro, alto contraste com fundo preto ou branco).
- No painel "Cores nos gráficos", uma escolha entre cores comuns e cores acessíveis. As acessíveis podem ser Okabe-Ito, Tol, cividis ou tons de cinza, cada uma com a sua referência.
- Opção de padrões além das cores (listras e pontos nas elipses, barras e histogramas; formatos diferentes nos pontos do HTML), para separar grupos sem depender da cor.
- As figuras exportadas seguem as cores e os padrões escolhidos e ficam sempre com fundo branco.
- O padrão agora são as cores comuns; quem usava a versão anterior vê as cores de antes escolhendo "Cores acessíveis > Okabe-Ito".

## 0.4.0 (17/10/2026)

- Escolha do idioma do programa e das exportações: português do Brasil, português de Portugal, espanhol, inglês, francês, alemão, chinês simplificado, hindi e árabe. Fica no menu Idioma e na tela inicial; na primeira abertura vale o idioma do sistema.
- Em árabe, a janela fica da direita para a esquerda.
- Planilha Excel, gráficos, HTML interativo, LEIAME dos dados e metodologia saem no idioma escolhido. A metodologia vem também em inglês.
- Números com vírgula decimal em português, espanhol, francês e alemão.
- Nos gráficos em imagem, hindi e árabe usam rótulos em inglês.
- Instalador do Windows em português do Brasil e de Portugal, espanhol, inglês, francês e alemão; o programa abre no idioma escolhido na instalação.

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
