# Conjunto de teste do módulo 2

Arquivos para conferir a importação e os cálculos do software contra o IsoplotR 7.1 (Vermeesch 2018, doi:10.1016/j.gsf.2018.04.001).

Os dados vêm dos exemplos que acompanham o IsoplotR (https://github.com/pvermees/IsoplotR, pasta `inst/`, licença GPL-3). Nenhum valor foi inventado: só foram renomeadas as colunas para os nomes da planilha de entrada e mudados o separador e o formato dos números.

## entrada/

Cada conjunto aparece em cinco formatos:

| Arquivo | Formato |
| --- | --- |
| `*.xlsx` | Excel |
| `*.ods` | LibreOffice/OpenOffice |
| `*_virgula-ponto.csv` | colunas separadas por vírgula, decimal com ponto |
| `*_pontoevirgula-virgula.csv` | colunas separadas por ponto e vírgula, decimal com vírgula (padrão brasileiro) |
| `*_tab.txt` | texto separado por tabulação, decimal com ponto |

| Conjunto | O que testa | Origem no IsoplotR |
| --- | --- | --- |
| UPb1 | Razões de Wetherill com rho; conjunto discordante (perda de Pb recente) | UPb1.csv |
| UPb2 | Razões de Tera-Wasserburg | UPb2.csv |
| UPb4 | Pb comum por 204Pb | UPb4.csv |
| UPb7 | U-Pb-Th com 208Pb e Th/U | UPb7.csv |
| ThPb1 | Isócrona Th-Pb | ThPb1.csv |
| PbPb1 | Isócrona Pb-Pb | PbPb1.csv |
| ThU1 | Isócrona 230Th-238U | ThU1.csv |
| UPb1_so_idades | Entrada só com idades por grão (saída do IsoplotR para UPb1) | idades calculadas |
| DZ_detritico_so_idades | 16 amostras detríticas, só idades, formato longo | DZ.csv |

`UPb1_estilo_laboratorio_latin1.csv` imita uma planilha de laboratório: duas linhas de título, cabeçalho em duas linhas, nomes como "Pb207/U235", erros em 2s %, ponto e vírgula, vírgula decimal e codificação Latin-1.

Erros: todos os arquivos têm erros 1σ absolutos (padrão do IsoplotR), exceto a variante de laboratório (2s %).

## referencia/

`resultados_referencia_IsoplotR.csv` traz o valor que o software deve reproduzir para cada cálculo: idade concórdia, interceptos da discórdia, médias ponderadas (com e sem Chauvenet generalizado e efeitos aleatórios), correção de Pb comum, isócronas Th-Pb, Pb-Pb e U-Th. Erros em 1σ absoluto, sem incertezas externas. Os demais arquivos trazem as idades grão a grão, o ajuste completo da discórdia e as distâncias KS e coordenadas MDS das amostras detríticas.

Constantes usadas pelo IsoplotR 7.1: λ238 = 1,55125 × 10⁻¹⁰ a⁻¹ (Jaffey et al. 1971) e 238U/235U = 137,818 (Hiess et al. 2012).

## scripts/

- `ref.R`: gera os resultados de referência com o IsoplotR.
- `build.py`: gera os arquivos de entrada a partir dos exemplos do IsoplotR.
