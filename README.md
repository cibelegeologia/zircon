# Zircon

Software no-code para calcular idades por isótopos de U, Th e Pb em zircão (U-Pb, Th-Pb, Pb-Pb e U-Th). O usuário escolhe em menus o que calcular e como, e cada opção traz a referência bibliográfica do método.

## Instalar

Baixe na página de versões (Releases) do repositório o arquivo do seu sistema:

- Windows: `Zircon-x.y.z-instalador.exe`, com assistente de instalação.
- macOS: `Zircon-x.y.z-macos-arm64.dmg` (Mac com chip Apple, M1 ou mais novo; Mac com Intel ainda não tem versão). Abra e arraste o Zircon para Aplicativos. Na primeira vez, clique com o botão direito no Zircon e escolha Abrir, porque o programa não tem assinatura paga da Apple.
- Linux: `Zircon-x.y.z-linux-amd64.deb` (Ubuntu, Debian, Mint; abre na Central de Programas) ou `.tar.gz` (qualquer distribuição; descompacte e rode `Zircon`).

 O programa é gratuito, funciona sem internet e não coleta dados.

Para rodar a partir do código: `pip install -r requirements.txt` e `python -m zircon`.

## Conteúdo

- `zircon/`: código do programa (`nucleo/` para os cálculos, `interface/` para as janelas).
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
