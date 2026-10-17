"""Idades U-Pb por grão a partir de razões isotópicas.

Erros sempre em 1 sigma absoluto. Tempo em Ma.
"""
import numpy as np
from scipy.optimize import brentq

from .constantes import LAMBDA_235, LAMBDA_238, U238_U235


def idade_68(r68, s68=0.0):
    """Idade 206Pb/238U (Ma) e seu erro."""
    r68 = np.asarray(r68, float)
    t = np.log1p(r68) / LAMBDA_238
    st = np.asarray(s68, float) / ((1 + r68) * LAMBDA_238)
    return t, st


def idade_75(r75, s75=0.0):
    """Idade 207Pb/235U (Ma) e seu erro."""
    r75 = np.asarray(r75, float)
    t = np.log1p(r75) / LAMBDA_235
    st = np.asarray(s75, float) / ((1 + r75) * LAMBDA_235)
    return t, st


def razao_76(t):
    """207Pb/206Pb radiogênico esperado para a idade t (Ma)."""
    t = np.asarray(t, float)
    return np.expm1(LAMBDA_235 * t) / (U238_U235 * np.expm1(LAMBDA_238 * t))


def _derivada_76(t):
    e5, e8 = np.exp(LAMBDA_235 * t), np.exp(LAMBDA_238 * t)
    num = LAMBDA_235 * e5 * (e8 - 1) - LAMBDA_238 * e8 * (e5 - 1)
    return num / (U238_U235 * (e8 - 1) ** 2)


def idade_76(r76, s76=0.0):
    """Idade 207Pb/206Pb (Ma), resolvida numericamente, e seu erro."""
    r76 = np.atleast_1d(np.asarray(r76, float))
    s76 = np.broadcast_to(np.asarray(s76, float), r76.shape)
    t = np.full(r76.shape, np.nan)
    for i, r in enumerate(r76):
        if np.isfinite(r) and r > razao_76(1e-6):
            t[i] = brentq(lambda x: razao_76(x) - r, 1e-6, 1e4)
    st = s76 / np.abs(_derivada_76(t))
    return t, st


def wetherill(t):
    """Coordenadas (207Pb/235U, 206Pb/238U) da concórdia para a idade t."""
    t = np.asarray(t, float)
    return np.expm1(LAMBDA_235 * t), np.expm1(LAMBDA_238 * t)


def tera_wasserburg(t):
    """Coordenadas (238U/206Pb, 207Pb/206Pb) da concórdia para a idade t."""
    t = np.asarray(t, float)
    return 1 / np.expm1(LAMBDA_238 * t), razao_76(t)


def tw_para_wetherill(x, sx, y, sy, rho):
    """Converte 238U/206Pb e 207Pb/206Pb em 207Pb/235U e 206Pb/238U.

    Propagação linear dos erros (Ludwig 1998).
    """
    x, sx, y, sy, rho = (np.asarray(v, float) for v in (x, sx, y, sy, rho))
    r75 = U238_U235 * y / x
    r68 = 1 / x
    # jacobiano de (r75, r68) em relação a (x, y)
    j = np.array([[-U238_U235 * y / x**2, U238_U235 / x], [-1 / x**2, np.zeros_like(x)]])
    cxy = rho * sx * sy
    cov = np.array([[sx**2, cxy], [cxy, sy**2]])
    c = np.einsum("ijn,jkn,lkn->iln", j, cov, j)
    s75, s68 = np.sqrt(c[0, 0]), np.sqrt(c[1, 1])
    return r75, s75, r68, s68, c[0, 1] / (s75 * s68)


def wetherill_para_tw(r75, s75, r68, s68, rho):
    """Converte 207Pb/235U e 206Pb/238U em 238U/206Pb e 207Pb/206Pb."""
    r75, s75, r68, s68, rho = (np.asarray(v, float) for v in (r75, s75, r68, s68, rho))
    x = 1 / r68
    y = r75 / (U238_U235 * r68)
    j = np.array([[np.zeros_like(r68), -1 / r68**2],
                  [1 / (U238_U235 * r68), -r75 / (U238_U235 * r68**2)]])
    c75_68 = rho * s75 * s68
    cov = np.array([[s75**2, c75_68], [c75_68, s68**2]])
    c = np.einsum("ijn,jkn,lkn->iln", j, cov, j)
    sx, sy = np.sqrt(c[0, 0]), np.sqrt(c[1, 1])
    return x, sx, y, sy, c[0, 1] / (sx * sy)


def discordancia(t68, t76):
    """Discordância relativa (%) entre as idades 206Pb/238U e 207Pb/206Pb."""
    return 100 * (1 - np.asarray(t68, float) / np.asarray(t76, float))


def melhor_idade(t68, s68, t76, s76, corte=1000.0):
    """Idade 206Pb/238U abaixo do corte (Ma) e 207Pb/206Pb acima dele."""
    t68, s68, t76, s76 = (np.asarray(v, float) for v in (t68, s68, t76, s76))
    usa76 = t68 >= corte
    return np.where(usa76, t76, t68), np.where(usa76, s76, s68)
