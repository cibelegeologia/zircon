# Zircon

Software no-code para calcular idades por isótopos de U, Th e Pb em zircão (U-Pb, Th-Pb, Pb-Pb e U-Th). O usuário escolhe em menus o que calcular e como, e cada opção traz a referência bibliográfica do método.

## Conteúdo

- `docs/especificacao_e_bibliografia.md`: bibliografia anotada, métodos de cálculo e estatísticos, menu de opções e planilha de entrada.
- `docs/referencias_abnt.md`: lista de referências no formato ABNT NBR 6023:2018.
- `testes/modulo2/`: arquivos de entrada em .xlsx, .ods, .csv e .txt e resultados de referência calculados com o IsoplotR 7.1.

## Estrutura do software

- Módulo 1: cálculo a partir das leituras de cada isótopo.
- Módulo 2: cálculo de idades de amostra a partir de razões ou idades por grão (primeiro a ser desenvolvido).

## Licença

O conteúdo deste repositório está sob CC0 1.0 (arquivo `LICENSE`), exceto os dados de exemplo em `testes/modulo2/`, derivados do IsoplotR, que seguem a licença GPL-3 do IsoplotR.
