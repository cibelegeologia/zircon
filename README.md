# Zircon

Software no-code para calcular idades por isótopos de U, Th e Pb em zircão (U-Pb, Th-Pb, Pb-Pb e U-Th). O usuário escolhe em menus o que calcular e como, e cada opção traz a referência bibliográfica do método.

## Instalar

Baixe na página de versões (Releases) do repositório o arquivo do seu sistema. O Zircon roda em computadores de 2010 para cá:

| Sistema | Arquivo | Versões |
| --- | --- | --- |
| Windows 64 bits | `Zircon-x.y.z-instalador-windows-x64.exe` | Windows 7 SP1, 8.1, 10 e 11 |
| Windows 32 bits | `Zircon-x.y.z-instalador-windows-x86.exe` | Windows 7 SP1, 8.1 e 10 |
| Mac com Intel | `Zircon-x.y.z-macos-x86_64.dmg` | macOS 10.13 (High Sierra) ou mais novo; roda também em Mac com chip Apple |
| Mac com chip Apple | `Zircon-x.y.z-macos-arm64.dmg` | macOS 14 (Sonoma) ou mais novo |
| Linux 64 bits | `Zircon-x.y.z-linux-amd64.deb` ou `.tar.gz` | Ubuntu 20.04, Debian 10, Mint 20, Pop!_OS 20.04, Fedora 29 ou mais novos; funciona em X11 e Wayland (GNOME, KDE, COSMIC) |

No Windows 7, o sistema precisa das atualizações KB2533623 e KB2999226 (vêm pelo Windows Update). Windows e Mac avisam na primeira abertura porque o programa não tem assinatura digital paga: no Windows, clique em "Mais informações > Executar assim mesmo"; no Mac, clique com o botão direito no Zircon e escolha Abrir.

Windows, Linux e Mac com Intel usam a montagem compatível (Python 3.8 e Qt 5, as últimas versões que rodam nesses sistemas). Os cálculos são os mesmos e passam pelos mesmos testes.

## Idiomas

O programa e as exportações (planilha Excel, gráficos, HTML interativo, LEIAME e metodologia) saem em português do Brasil, português de Portugal, espanhol, inglês, francês, alemão, chinês simplificado, hindi ou árabe. Na primeira abertura o Zircon usa o idioma do sistema (ou o escolhido no instalador do Windows); para mudar, use o menu Idioma ou a lista na tela inicial. Em árabe a janela fica da direita para a esquerda.

A metodologia sai no idioma escolhido e também em inglês. Nos gráficos em imagem (PNG, TIFF, PDF, SVG), hindi e árabe usam rótulos em inglês, porque a biblioteca de gráficos não monta essas escritas corretamente; o HTML interativo sai no idioma escolhido. As traduções ficam em `zircon/idiomas/`, uma por arquivo JSON, e podem ser corrigidas por qualquer pessoa: `python -m zircon.idiomas.extrair` mostra as frases que faltam.

## Acessibilidade

Tudo é opcional. No menu Acessibilidade há tamanho da letra (até o dobro; atalhos Ctrl + e Ctrl -) e temas claro, escuro e de alto contraste. No painel de opções, "Cores nos gráficos" alterna entre cores comuns e cores acessíveis para daltonismo (Okabe-Ito, Tol, cividis ou tons de cinza), e pode acrescentar padrões (listras e pontos) para separar os grupos sem depender da cor. As figuras exportadas seguem essas escolhas de cor.

O Zircon funciona com os leitores de tela mais comuns (NVDA, JAWS, Narrador, VoiceOver e Orca): cada campo, tabela e gráfico tem nome e descrição, e cada gráfico tem um resumo em texto.

## Ajuda

O Guia do Zircon (F1) explica cada recurso: para que serve, o artigo original e como usar. O botão "?  O que é isto?" mostra uma legenda curta sobre qualquer coisa na tela, inclusive os grãos dos gráficos. O programa não usa inteligência artificial: os cálculos são fórmulas fixas dos artigos citados e os textos de ajuda são arquivos fixos.

Para rodar a partir do código: `pip install -r requirements.txt` e `python -m zircon`.

## Conteúdo

- `CHANGELOG.md`: o que muda de versão para versão.
- `zircon/`: código do programa (`nucleo/` para os cálculos, `interface/` para as janelas, `idiomas/` para as traduções).
- `instalador/`: receita do PyInstaller e do instalador (Inno Setup).
- `docs/arquitetura_e_privacidade.md`: como o programa é feito, arquivo de projeto, registro e privacidade.

- `docs/especificacao_e_bibliografia.md`: bibliografia anotada, métodos de cálculo e estatísticos, menu de opções e planilha de entrada.
- `docs/referencias_abnt.md`: lista de referências no formato ABNT NBR 6023:2018.
- `testes/unitarios/`: testes que conferem os cálculos com o IsoplotR.
- `testes/modulo2/`: arquivos de entrada em .xlsx, .ods, .csv e .txt e resultados de referência calculados com o IsoplotR 7.1.

## Estrutura do software

- Módulo 1: cálculo a partir das leituras de cada isótopo.
- Módulo 2: cálculo de idades de amostra a partir de razões ou idades por grão (primeiro a ser desenvolvido).

## Licença

O conteúdo deste repositório está sob CC0 1.0 (arquivo `LICENSE`), exceto os dados de exemplo em `testes/modulo2/`, derivados do IsoplotR, que seguem a licença GPL-3 do IsoplotR.
