"""Separação dos grãos em grupos e cores para os gráficos."""
import numpy as np
from scipy.signal import argrelextrema
from scipy.stats import gaussian_kde

# Paleta segura para daltônicos (Okabe e Ito 2008; Wong 2011, Nature Methods 8:441)
PALETA = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#F0E442", "#000000"]
COR_CLASSE = {"concordante": "#009E73", "discordante": "#E69F00", "rejeitado": "#999999"}

REFERENCIAS = {
    "classe": "Spencer, Kirkland e Taylor (2016), Geoscience Frontiers 7:581-589 (discordância)",
    "populacoes": "Vermeesch (2012), Chemical Geology 312-313:190-194 (estimativa de densidade)",
    "cores": "Wong (2011), Nature Methods 8:441 (paleta para daltônicos)",
}


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
