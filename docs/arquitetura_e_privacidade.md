# Arquitetura e privacidade

Decisão de 17/10/2026: o Zircon é um programa de desktop para Windows, instalado por um assistente (.exe), que funciona sem internet. Motivos: muitos computadores ligados a equipamentos de laboratório não têm internet, e os pesquisadores preferem trabalhar com arquivos de projeto no próprio computador (Arquivo > Novo, Abrir, Salvar).

## Como é feito

- Python com interface Qt (PySide6) e gráficos em matplotlib.
- `zircon/nucleo/`: cálculos, sem interface. Conferidos com o IsoplotR 7.1 pelos testes em `testes/unitarios/`.
- `zircon/interface/`: janelas, menus e gráficos.
- O PyInstaller junta tudo numa pasta com `Zircon.exe`; o Inno Setup gera o instalador com assistente.
- O GitHub Actions (`.github/workflows/instaladores.yml`) roda os testes e gera os instaladores de Windows (.exe), macOS (.dmg, Apple Silicon e Intel) e Linux (.deb e .tar.gz) a cada envio. Uma etiqueta `v0.1.0` publica o instalador na página de versões do repositório.

## Arquivo de projeto (.zircon)

Um arquivo zip com `projeto.json` (opções, grupos, registro da importação, notas), `dados.csv` (dados padronizados) e uma cópia da planilha original. Abre de novo sem a planilha original.

## Instalador

Etapas: boas-vindas, licença (CC0, gratuito), formulário opcional (nome, instituição, país, e-mail, uso), pasta, componentes (programa, exemplos, referências), tarefas (atalho, associar .zircon), confirmação e conclusão.

## Registro e privacidade

- O programa não tem nenhum código que acesse a internet.
- O formulário do instalador é opcional e fica salvo só no computador (`%APPDATA%\Zircon\Zircon\registro.json`).
- Registrar é voluntário: o usuário abre Ajuda > Registrar, confere o texto e escolhe enviar por e-mail ou pelo navegador. Cada instalação tem um código anônimo aleatório, sem ligação com o computador.
- Para contar instalações sem coletar nada, use o número de downloads da página de versões do GitHub.
- `URL_FORMULARIO` em `zircon/interface/dialogos.py` pode apontar para um formulário (por exemplo, Google Forms com campos pré-preenchidos). Vazio, o registro vai por e-mail.

## Cores por grupo

Três modos: concordante, discordante ou rejeitado; populações de idade separadas pelos mínimos da curva de densidade (Vermeesch 2012); ou grupos escolhidos pelo usuário (Grupos > Colocar linhas selecionadas no grupo). Paleta segura para daltônicos (Okabe e Ito 2008; Wong 2011).
