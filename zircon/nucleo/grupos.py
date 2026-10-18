"""Separação dos grãos em grupos e cores para os gráficos."""
import numpy as np
from scipy.signal import argrelextrema
from scipy.stats import gaussian_kde

from ..idiomas import N_, tr

# Paletas para quem tem daltonismo. A escolhida fica em PALETA e COR_CLASSE,
# que são alterados no lugar para quem já os importou ver a troca.
PALETAS = {
    # cores comuns do matplotlib (tab10); verde e vermelho podem se confundir no daltonismo
    "comum": {"grupos": ["#1F77B4", "#FF7F0E", "#2CA02C", "#D62728", "#9467BD", "#8C564B", "#E377C2", "#7F7F7F"],
              "classes": {"concordante": "#2CA02C", "discordante": "#D62728", "rejeitado": "#7F7F7F"}},
    # Okabe e Ito (2008); Wong (2011), Nature Methods 8:441
    "okabe_ito": {"grupos": ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#F0E442",
                             "#000000"],
                  "classes": {"concordante": "#009E73", "discordante": "#E69F00", "rejeitado": "#999999"}},
    # Tol (2021), esquema "bright": cores mais vivas, também seguras
    "tol": {"grupos": ["#4477AA", "#EE6677", "#228833", "#CCBB44", "#66CCEE", "#AA3377", "#BBBBBB", "#000000"],
            "classes": {"concordante": "#4477AA", "discordante": "#EE6677", "rejeitado": "#BBBBBB"}},
    # cividis (Nuñez, Anderton e Renslow 2018): do azul ao amarelo, igual para todos os tipos de visão
    "cividis": {"grupos": ["#00224E", "#FEE838", "#575C6D", "#C3B369", "#2C3E6C", "#8A8779", "#E2CC50",
                           "#00336F"],
                "classes": {"concordante": "#00336F", "discordante": "#D9C55B", "rejeitado": "#8A8779"}},
    # tons de cinza, para impressão em preto e branco (use com os padrões)
    "cinza": {"grupos": ["#000000", "#9E9E9E", "#525252", "#D0D0D0", "#2B2B2B", "#757575", "#BDBDBD",
                         "#404040"],
              "classes": {"concordante": "#2B2B2B", "discordante": "#9E9E9E", "rejeitado": "#D0D0D0"}},
}
PALETA = list(PALETAS["comum"]["grupos"])
COR_CLASSE = dict(PALETAS["comum"]["classes"])

# Padrões (hachuras) além da cor, para separar grupos sem depender dela
HACHURA_CLASSE = {"concordante": "", "discordante": "////", "rejeitado": "xxxx"}
HACHURAS = ["", "////", "....", "\\\\\\\\", "xxxx", "oo", "++++", "----"]
_estado = {"padroes": False}


def definir_paleta(nome, padroes=None):
    """Escolhe a paleta das cores e liga ou desliga os padrões além da cor."""
    p = PALETAS.get(nome, PALETAS["comum"])
    PALETA[:] = p["grupos"]
    COR_CLASSE.clear()
    COR_CLASSE.update(p["classes"])
    if padroes is not None:
        _estado["padroes"] = bool(padroes)


def usar_padroes():
    return _estado["padroes"]


def hachura(classe=None, grupo=None):
    """Padrão de preenchimento de uma classe ou grupo ("" = liso)."""
    if not _estado["padroes"]:
        return ""
    if classe is not None:
        return HACHURA_CLASSE.get(classe, "")
    return HACHURAS[(int(grupo) - 1) % len(HACHURAS)] if grupo and grupo > 0 else ""

REFERENCIAS = {
    "classe": N_("Spencer, Kirkland e Taylor (2016), Geoscience Frontiers 7:581-589 (discordância)"),
    "populacoes": N_("Vermeesch (2012), Chemical Geology 312-313:190-194 (estimativa de densidade)"),
    "cores": N_("Wong (2011), Nature Methods 8:441 (paleta para daltônicos)"),
    "okabe_ito": N_("Okabe e Ito (2008); Wong (2011), Nature Methods 8:441"),
    "tol": N_("Tol (2021), SRON/EPS/TN/09-002"),
    "cividis": N_("Nuñez, Anderton e Renslow (2018), PLOS ONE 13:e0199239"),
}
# Nomes das classes, para tradução
N_("concordante"), N_("discordante"), N_("rejeitado"), N_("Amostra {n}"), N_("{amostra}, população {n}")


def classifica(discordancia, valido, limite=10.0):
    """Concordante, discordante (|disc| > limite %) ou rejeitado (outlier)."""
    disc = np.asarray(discordancia, float)
    classe = np.where(np.abs(disc) > limite, "discordante", "concordante").astype(object)
    classe[~np.asarray(valido, bool)] = "rejeitado"
    return classe


def populacoes(idades, largura=None, minimo=1):
    """Separa as idades em populações pelos mínimos da curva de densidade.

    Devolve o número da população (1, 2, ...) de cada idade, em ordem
    crescente de idade, e os limites entre populações.
    """
    t = np.asarray(idades, float)
    ok = np.isfinite(t)
    grupo = np.zeros(len(t), int)
    if ok.sum() < 3:
        grupo[ok] = 1
        return grupo, []
    kde = gaussian_kde(t[ok], bw_method=largura)
    grade = np.linspace(t[ok].min(), t[ok].max(), 2000)
    dens = kde(grade)
    cortes = [grade[i] for i in argrelextrema(dens, np.less)[0]]
    # junta populações com menos de `minimo` grãos à vizinha
    while True:
        rotulos = np.digitize(t[ok], cortes) + 1
        contagem = np.bincount(rotulos, minlength=len(cortes) + 2)[1:len(cortes) + 2]
        pequenos = [i for i, c in enumerate(contagem) if c < minimo]
        if not pequenos or not cortes:
            break
        i = pequenos[0]
        cortes.pop(min(i, len(cortes) - 1))
    grupo[ok] = np.digitize(t[ok], cortes) + 1
    return grupo, cortes


def cor_do_grupo(n):
    """Cor da paleta para o grupo n (1, 2, ...); 0 = sem grupo (cinza)."""
    return "#999999" if n <= 0 else PALETA[(n - 1) % len(PALETA)]


# Símbolos que o pesquisador pode escolher para cada conjunto (os mais usados em
# artigos e no Excel): código do matplotlib -> (nome, código do plotly)
SIMBOLOS = {
    "nenhum": (N_("Nenhum (só a cor)"), None),
    "o": (N_("Círculo"), "circle"),
    "s": (N_("Quadrado"), "square"),
    "D": (N_("Losango"), "diamond"),
    "^": (N_("Triângulo para cima"), "triangle-up"),
    "v": (N_("Triângulo para baixo"), "triangle-down"),
    "<": (N_("Triângulo para a esquerda"), "triangle-left"),
    ">": (N_("Triângulo para a direita"), "triangle-right"),
    "p": (N_("Pentágono"), "pentagon"),
    "h": (N_("Hexágono"), "hexagon"),
    "H": (N_("Hexágono deitado"), "hexagon2"),
    "8": (N_("Octógono"), "octagon"),
    "*": (N_("Estrela"), "star"),
    "d": (N_("Losango estreito"), "diamond-tall"),
    "P": (N_("Cruz cheia"), "cross"),
    "X": (N_("Xis cheio"), "x"),
    "+": (N_("Cruz de traços"), "cross-thin"),
    "x": (N_("Xis de traços"), "x-thin"),
    "1": (N_("Tripé"), "y-down"),
    "_": (N_("Traço horizontal"), "line-ew"),
    "|": (N_("Traço vertical"), "line-ns"),
}
SIMBOLOS_DE_TRACO = {"+", "x", "1", "_", "|"}  # sem preenchimento: a cor vai no traço
SIMBOLO_CLASSE = {"concordante": "o", "discordante": "s", "rejeitado": "x"}
# padrões de preenchimento que o pesquisador pode escolher: código do matplotlib -> nome
NOMES_HACHURA = {"": N_("Liso"), "////": N_("Listras inclinadas"), "\\\\\\\\": N_("Listras inclinadas ao contrário"),
                 "....": N_("Pontos"), "xxxx": N_("Quadriculado inclinado"), "++++": N_("Quadriculado"),
                 "----": N_("Listras horizontais"), "||||": N_("Listras verticais"), "oo": N_("Círculos")}
SIMBOLOS_GRUPO = ["o", "s", "^", "D", "v", "p", "*", "h"]


def chave_conjunto(classe, grupo, agrupar, amostra=None):
    """Nome interno do conjunto de um grão: a classe, "g<n>" para grupos e populações, ou
    "a<n>:<amostra>" para a n-ésima amostra da planilha."""
    if agrupar == "classe":
        return str(classe)
    if agrupar in ("amostra", "amostra_populacoes"):
        return f"a{int(grupo)}:{amostra}"
    return f"g{int(grupo)}"


def chaves_amostras(amostras):
    """Número (1, 2, ... na ordem em que aparecem) e chave da amostra de cada grão."""
    import pandas as pd
    nomes = pd.Series(amostras).fillna("").astype(str).to_numpy()
    numero = pd.factorize(nomes)[0] + 1
    return numero, [f"a{n}:{a}" for n, a in zip(numero, nomes)]


def populacoes_por_amostra(amostras, idades, minimo=1):
    """Populações separadas dentro de cada amostra: número sequencial (para a cor) e chave
    "a<n>:<amostra>|<população>" de cada grão."""
    import pandas as pd
    nomes = pd.Series(amostras).fillna("").astype(str).to_numpy()
    t = np.asarray(idades, float)
    numero = np.zeros(len(t), int)
    chaves = [""] * len(t)
    n = 0
    for a in pd.unique(nomes):
        sel = np.flatnonzero(nomes == a)
        pop, _ = populacoes(t[sel], minimo=minimo)
        for p_ in sorted(set(pop)):
            n += 1
            for i in sel[pop == p_]:
                numero[i] = n
                chaves[i] = f"a{n}:{a}|{p_}"
    return numero, chaves


def numero_conjunto(chave):
    """Número de um grupo, população ou amostra ("g2" -> 2, "a3:ARA" -> 3)."""
    return int(chave[1:].split(":", 1)[0])


def nome_conjunto(chave, traduz=tr):
    """Nome do conjunto para mostrar: "Concordante", "Grupo 2" ou o nome da amostra (traduz: função de tradução)."""
    if chave is None:
        return ""
    if chave in SIMBOLO_CLASSE:
        return traduz(chave).capitalize()
    if chave.startswith("a"):
        resto = chave.split(":", 1)[1]
        if "|" in resto:  # população dentro de uma amostra
            amostra, pop = resto.rsplit("|", 1)
            return traduz("{amostra}, população {n}").format(amostra=amostra, n=pop)
        return resto or traduz("Amostra {n}").format(n=numero_conjunto(chave))
    return traduz("Grupo {n}").format(n=numero_conjunto(chave))


def ordem_conjunto(chave):
    """Ordem dos conjuntos nas tabelas: classes na ordem de SIMBOLO_CLASSE, depois grupos pelo número."""
    classes = list(SIMBOLO_CLASSE)
    return (classes.index(chave), 0) if chave in classes else (len(classes), numero_conjunto(chave))


def estilo_padrao(chave):
    """Cor, símbolo e padrão de um conjunto antes de o pesquisador mudar algo (da paleta escolhida)."""
    if chave in SIMBOLO_CLASSE:
        return COR_CLASSE[chave], SIMBOLO_CLASSE[chave], hachura(classe=chave)
    n = numero_conjunto(chave)
    return cor_do_grupo(n), SIMBOLOS_GRUPO[(n - 1) % len(SIMBOLOS_GRUPO)] if n > 0 else "o", hachura(grupo=n)


def cores_seguras():
    """Cores da paleta atual: no modo para daltônicos, só estas podem ser escolhidas."""
    return list(dict.fromkeys(PALETA + list(COR_CLASSE.values())))
