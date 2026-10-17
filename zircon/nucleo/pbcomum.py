"""Correção de Pb comum pelo 204Pb.

Pb radiogênico = Pb medido − 204Pb × (Pb/204Pb do Pb comum). A composição
do Pb comum pode ser fixa (informada pelo usuário) ou a do modelo de
evolução de Stacey e Kramers (1975) na idade do grão.
"""
import numpy as np

from ..idiomas import N_
from . import idades
from .constantes import LAMBDA_232, LAMBDA_235, LAMBDA_238, U238_U235

# Pb primordial de Canyon Diablo (Tatsumoto et al. 1973), padrão do IsoplotR
CANYON_DIABLO = {"64": 9.307, "74": 10.294, "84": 29.476}

REFERENCIAS = {
    "fixo": N_("Williams (1998); composição de Canyon Diablo de Tatsumoto, Knight e Allègre (1973)"),
    "stacey_kramers": N_("Stacey e Kramers (1975), Earth and Planetary Science Letters 26:207-221"),
}


def stacey_kramers(t):
    """Composição do Pb comum (206/204, 207/204, 208/204) na idade t (Ma)."""
    t = np.asarray(t, float)
    jovem = t < 3700
    a64 = np.where(jovem, 11.152, 9.307)
    a74 = np.where(jovem, 12.998, 10.294)
    a84 = np.where(jovem, 31.23, 29.487)
    mu = np.where(jovem, 9.74, 7.19)
    w = np.where(jovem, 36.84, 33.21)
    ti = np.where(jovem, 3700.0, 4570.0)
    i64 = a64 + mu * (np.exp(LAMBDA_238 * ti) - np.exp(LAMBDA_238 * t))
    i74 = a74 + mu * (np.exp(LAMBDA_235 * ti) - np.exp(LAMBDA_235 * t)) / U238_U235
    i84 = a84 + w * (np.exp(LAMBDA_232 * ti) - np.exp(LAMBDA_232 * t))
    return i64, i74, i84


def _corrige(r75, s75, r68, s68, r48, s48, rxy, rxz, ryz, c64, c74):
    """Razões radiogênicas e covariância, propagando o erro do 204Pb."""
    c48_75 = rxz * s75 * s48
    c48_68 = ryz * s68 * s48
    x75 = r75 - r48 * c74
    x68 = r68 - r48 * c64
    v75 = s75**2 + (c74 * s48) ** 2 - 2 * c74 * c48_75
    v68 = s68**2 + (c64 * s48) ** 2 - 2 * c64 * c48_68
    cov = rxy * s75 * s68 - c64 * c48_75 - c74 * c48_68 + c74 * c64 * s48**2
    return x75, np.sqrt(v75), x68, np.sqrt(v68), cov / np.sqrt(v75 * v68)


def corrigir_204(d, modelo="stacey_kramers", c64=None, c74=None):
    """Devolve (r75, s75, r68, s68, rho) radiogênicos para cada grão.

    d precisa das colunas r75, s75, r68, s68, r48, s48 e das correlações
    rho (75-68), rho_xz (75-48) e rho_yz (68-48); as que faltarem valem 0.
    """
    g = {k: np.asarray(d[k], float) if k in d else np.zeros(len(d))
         for k in ("r75", "s75", "r68", "s68", "r48", "s48", "rho", "rho_xz", "rho_yz")}
    args = [g[k] for k in ("r75", "s75", "r68", "s68", "r48", "s48", "rho", "rho_xz", "rho_yz")]
    if modelo != "stacey_kramers":
        c64 = CANYON_DIABLO["64"] if c64 is None else c64
        c74 = CANYON_DIABLO["74"] if c74 is None else c74
        return _corrige(*args, c64, c74)
    # Stacey e Kramers: a composição depende da idade, que depende da correção;
    # itera até a idade 206Pb/238U corrigida parar de mudar (Williams 1998).
    t = np.full(len(d), 1000.0)
    for _ in range(100):
        i64, i74, _ = stacey_kramers(t)
        corrigido = _corrige(*args, i64, i74)
        novo = idades.idade_68(corrigido[2])[0]
        if np.allclose(novo, t, atol=1e-9, equal_nan=True):
            break
        t = novo
    return corrigido
