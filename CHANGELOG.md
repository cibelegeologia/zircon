# Histórico de versões

Todas as mudanças do Zircon que o usuário percebe, da mais nova para a mais antiga. As versões seguem o padrão maior.menor.correção: o último número muda em correções, o do meio quando entra algo novo.

## 0.9.0 (18/10/2026)

Preparar a planilha para o Zircon.

- Arquivo > Salvar modelo de planilha: grava um .xlsx com as colunas que o Zircon lê (Amostra, Análise, 207Pb/235U, ± 2σ, 206Pb/238U, ± 2σ, rho), cinco linhas de exemplo inventadas e uma aba de instruções no idioma do programa.
- Novo tópico no guia: "Preparar a planilha (modelo)", com o passo a passo para passar a planilha do laboratório para o modelo.
- Correção: um erro com unidade no cabeçalho, como "± 2σ (Ma)" ou "± 2σ (%)", era lido como 1σ. Agora é lido como 2σ.
- Correção: colunas de idade calculadas pelo laboratório, à direita das razões, não são mais confundidas com a razão 207Pb/206Pb.
- O guia corrige duas informações: o cabeçalho deve ocupar uma só linha, e a discórdia usa todos os grãos do projeto (os grupos não a restringem).

## 0.8.0 (17/10/2026)

Mudanças pedidas depois do primeiro teste no Pop!_OS.

- Nada é calculado sozinho. Depois de importar a planilha, o Zircon mostra os dados e espera você escolher as opções e clicar em Calcular (ou F5). Se mudar uma opção, cor ou grupo depois do cálculo, o botão avisa "Calcular (as opções mudaram)" e os gráficos só mudam quando você clicar. Projetos salvos abrem com o último cálculo.
- As abas viraram janelas: cada uma pode ser solta, arrastada, posta lado a lado com outra, fechada e reaberta pelo menu Exibir. Solta, vira uma janela comum, com minimizar, maximizar e fechar. O Zircon lembra a arrumação; "Exibir > Voltar à arrumação inicial" desfaz tudo.
- Tela cheia com a tecla do sistema (F11 no Windows e no Linux; Ctrl+Cmd+F no Mac) ou por "Exibir > Tela cheia".
- Seleção ligada: o grão selecionado na tabela ou clicado num gráfico fica destacado na tabela e em todos os gráficos, sem trocar a janela que está à frente. Ctrl ou Shift juntam vários grãos.
- O menu Ajuda passou a ser o último da barra, como nos outros programas.
- Novo tópico no guia: "Janelas, seleção e tela cheia".

## 0.7.0 (17/10/2026)

- Ajuda > Verificar atualizações: pergunta ao GitHub se há versão nova e, se houver, indica o arquivo certo para o seu sistema e abre a página de download. É a única função do Zircon que usa a internet, e só quando você clica nela; não envia nenhum dado seu e não baixa nem instala nada sozinho.
- O instalador do Windows avisa quando já existe um Zircon instalado e pergunta se deve substituí-lo. Projetos e preferências são mantidos.
- Novo tópico no guia: "Verificar atualizações".

## 0.6.1 (17/10/2026)

- Linux: as janelas voltam a ter barra de título com os botões de minimizar, maximizar e fechar no Pop!_OS 24.04 e em outros sistemas com Wayland. O Zircon agora abre pelo XWayland, e quem desenha a barra é a própria área de trabalho.

## 0.6.0 (17/10/2026)

Ajuda e leitores de tela.

- Guia do Zircon (menu Ajuda ou F1), com 23 tópicos e busca. Cada tópico diz para que serve o recurso e em que casos usar, indica o artigo original em ABNT e explica como usar no programa. Cada opção do painel tem um botão "?" que abre o tópico dela.
- Botão "?  O que é isto?" na barra de ferramentas: com ele ligado, o mouse vira uma interrogação e mostra uma legenda curta sobre botões, menus, abas e opções. Clicando, a legenda fica parada até o próximo clique. Esc desliga.
- Passando o mouse sobre um grão nos gráficos aparece um resumo: amostra, análise, idades ± 2σ, discordância, classe e grupo.
- Leitores de tela (NVDA, JAWS e Narrador no Windows, VoiceOver no Mac, Orca no Linux): cada campo, botão, tabela e gráfico tem nome e descrição. Cada gráfico tem um resumo em texto do resultado.
- Barra de ferramentas com ícones para Novo, Abrir, Salvar, Calcular, Exportar e Guia; as dicas da barra dos gráficos foram traduzidas.

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
