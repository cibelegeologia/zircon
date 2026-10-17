"""Cálculos de conjunto: média ponderada, idade concórdia e discórdia.

Erros em 1 sigma absoluto. Cada função devolve um dicionário com o
resultado e a referência do método.
"""
import numpy as np
from scipy import stats
from scipy.optimize import brentq, minimize_scalar

from ..idiomas import N_
from . import idades


def _mswd(ss, gl):
    if gl <= 0:
        return 1.0, 1.0
    return ss / gl, float(stats.chi2.sf(ss, gl))


def _mistura_continua(z, s):
    """Média e dispersão por máxima verossimilhança (Galbraith 2005, p. 100)."""
    if len(np.unique(z)) < 2:
        w = 1 / s**2
        return z[0], 1 / np.sqrt(w.sum()), 0.0
    sigma = np.std(z, ddof=1)
    for _ in range(30):
        w = 1 / (sigma**2 + s**2)
        mu = np.sum(w * z) / np.sum(w)
        kappa = np.log(sigma)

        def eq69(k):
            wk = 1 / (np.exp(k) ** 2 + s**2)
            return (1 - np.sum((wk * (z - mu)) ** 2) / np.sum(wk)) ** 2

        sigma = np.exp(minimize_scalar(eq69, bounds=(kappa - 3, kappa + 3), method="bounded",
                                       options={"xatol": 1e-10}).x)
    w = 1 / (sigma**2 + s**2)
    return mu, 1 / np.sqrt(w.sum()), sigma


def _media(x, s, efeitos_aleatorios):
    n = len(x)
    if efeitos_aleatorios and np.all(x > 0):
        z, sz = np.log(x), s / x
        mu, smu, sigma = _mistura_continua(z, sz)
        t = np.exp(mu)
        ss = np.sum((z / sz) ** 2) - np.sum(z / sz**2) ** 2 / np.sum(1 / sz**2)
        mswd, p = _mswd(ss, n - 1)
        return {"media": t, "erro": t * smu, "dispersao": sigma * t, "mswd": mswd, "p": p}
    w = 1 / s**2
    m = np.sum(w * x) / np.sum(w)
    mswd, p = _mswd(np.sum(((x - m) / s) ** 2), n - 1)
    return {"media": m, "erro": 1 / np.sqrt(w.sum()), "dispersao": 0.0, "mswd": mswd, "p": p}


def _chauvenet(x, s, valido, efeitos_aleatorios):
    r = _media(x[valido], s[valido], efeitos_aleatorios)
    if efeitos_aleatorios and np.all(x > 0):
        z, mu = np.log(x), np.log(r["media"])
        sigma = np.sqrt((r["dispersao"] / r["media"]) ** 2 + (s / x) ** 2)
    else:
        z, mu = x, r["media"]
        sigma = np.sqrt(r["erro"] ** 2 + max(1, r["mswd"]) * s**2)
    desvio = np.where(valido, np.abs(z - mu) / sigma, -np.inf)
    pior = int(np.argmax(desvio))
    prob = 2 * stats.norm.sf(desvio[pior])
    if valido.sum() * prob < 0.5:
        valido = valido.copy()
        valido[pior] = False
    return valido


def media_ponderada(x, s, efeitos_aleatorios=False, rejeitar_outliers=False):
    """Média ponderada pelo inverso da variância, com MSWD e valor-p.

    efeitos_aleatorios: modelo com dispersão geológica extra (Vermeesch 2018).
    rejeitar_outliers: critério de Chauvenet generalizado (Vermeesch 2018).
    """
    x, s = np.asarray(x, float), np.asarray(s, float)
    valido = np.isfinite(x) & np.isfinite(s) & (s > 0)
    if rejeitar_outliers:
        while valido.sum() > 2:
            novo = _chauvenet(x, s, valido, efeitos_aleatorios)
            if novo.sum() == valido.sum():
                break
            valido = novo
    r = _media(x[valido], s[valido], efeitos_aleatorios)
    r.update(n=int(valido.sum()), valido=valido,
             referencia=N_("Wendt e Carl (1991); Vermeesch (2018a)") if (efeitos_aleatorios or rejeitar_outliers)
             else N_("Wendt e Carl (1991)"))
    return r


def _cov(sx, sy, rho):
    c = rho * sx * sy
    return np.array([[sx**2, c], [c, sy**2]]).transpose(2, 0, 1)


def idade_concordia(r75, s75, r68, s68, rho):
    """Idade concórdia de Ludwig (1998) no diagrama de Wetherill."""
    X = np.column_stack([r75, r68]).astype(float)
    C = _cov(np.asarray(s75, float), np.asarray(s68, float), np.asarray(rho, float))
    O = np.linalg.inv(C)
    n = len(X)
    # composição média ponderada e sua covariância
    Osum = O.sum(axis=0)
    Cbar = np.linalg.inv(Osum)
    xbar = Cbar @ np.einsum("nij,nj->i", O, X)
    d = X - xbar
    ss_eq = float(np.einsum("ni,nij,nj->", d, O, d))

    def ss_conc(t):
        dd = xbar - np.array(idades.wetherill(t))
        return float(dd @ Osum @ dd)

    t0 = float(idades.idade_68(xbar[1])[0])
    t = minimize_scalar(ss_conc, bounds=(t0 * 0.5, t0 * 1.5 + 10), method="bounded",
                        options={"xatol": 1e-9}).x
    J = np.array([idades.LAMBDA_235 * np.exp(idades.LAMBDA_235 * t),
                  idades.LAMBDA_238 * np.exp(idades.LAMBDA_238 * t)])
    st = 1 / np.sqrt(J @ Osum @ J)
    sc = ss_conc(t)
    mswd, p = _mswd(ss_eq + sc, 2 * n - 1)
    return {"idade": t, "erro": st, "mswd": mswd, "p": p, "n": n,
            "mswd_equivalencia": ss_eq / (2 * n - 2) if n > 1 else 0.0,
            "mswd_concordancia": sc,
            "referencia": "Ludwig (1998)"}


def york(x, sx, y, sy, rho, tol=1e-15):
    """Reta de regressão com erros correlacionados (York et al. 2004)."""
    x, sx, y, sy, rho = (np.asarray(v, float) for v in (x, sx, y, sy, rho))
    wx, wy = 1 / sx**2, 1 / sy**2
    b = np.polyfit(x, y, 1)[0]
    for _ in range(200):
        a_ = np.sqrt(wx * wy)
        W = wx * wy / (wx + b**2 * wy - 2 * b * rho * a_)
        xb, yb = np.sum(W * x) / W.sum(), np.sum(W * y) / W.sum()
        U, V = x - xb, y - yb
        beta = W * (U / wy + b * V / wx - (b * U + V) * rho / a_)
        b_novo = np.sum(W * beta * V) / np.sum(W * beta * U)
        if abs(b_novo - b) < tol * abs(b):
            b = b_novo
            break
        b = b_novo
    a = yb - b * xb
    xi = xb + beta
    xib = np.sum(W * xi) / W.sum()
    u = xi - xib
    sb2 = 1 / np.sum(W * u**2)
    sa2 = 1 / W.sum() + xib**2 * sb2
    cab = -xib * sb2
    n = len(x)
    mswd, p = _mswd(np.sum(W * (y - b * x - a) ** 2), n - 2)
    return {"a": a, "b": b, "sa": np.sqrt(sa2), "sb": np.sqrt(sb2), "cov_ab": cab,
            "mswd": mswd, "p": p, "n": n, "referencia": "York et al. (2004)"}


def discordia(r75, s75, r68, s68, rho):
    """Interceptos inferior e superior da discórdia no diagrama de Wetherill.

    Regressão de York (2004) e erros propagados pela covariância de a e b.
    """
    fit = york(r75, s75, r68, s68, rho)
    a, b = fit["a"], fit["b"]
    covab = np.array([[fit["sa"] ** 2, fit["cov_ab"]], [fit["cov_ab"], fit["sb"] ** 2]])

    def f(t):
        x, y = idades.wetherill(t)
        return a + b * x - y

    grade = np.linspace(-3000, 4600, 7601)
    vals = f(grade)
    raizes = []
    for i in np.nonzero(np.sign(vals[:-1]) != np.sign(vals[1:]))[0]:
        raizes.append(brentq(f, grade[i], grade[i + 1], xtol=1e-12))
    resultado = {"mswd": fit["mswd"], "p": fit["p"], "n": fit["n"], "a": a, "b": b,
                 "referencia": "York et al. (2004); Ludwig (1998)"}
    erros = []
    for t in raizes:
        x, _ = idades.wetherill(t)
        dfdt = b * idades.LAMBDA_235 * np.exp(idades.LAMBDA_235 * t) - idades.LAMBDA_238 * np.exp(idades.LAMBDA_238 * t)
        g = -np.array([1.0, x]) / dfdt
        erros.append(float(np.sqrt(g @ covab @ g)))
    if len(raizes) >= 2:
        resultado.update(inferior=raizes[0], erro_inferior=erros[0],
                         superior=raizes[-1], erro_superior=erros[-1])
    elif len(raizes) == 1:
        resultado.update(superior=raizes[0], erro_superior=erros[0])
    return resultado



def isocrona_thpb(r24, s24, r84, s84, rho):
    """Isócrona 232Th/204Pb x 208Pb/204Pb: inclinação = exp(λ232 t) − 1."""
    fit = york(r24, s24, r84, s84, rho)
    t = np.log1p(fit["b"]) / idades.LAMBDA_232
    st = fit["sb"] / ((1 + fit["b"]) * idades.LAMBDA_232)
    return {"idade": t, "erro": st, "mswd": fit["mswd"], "p": fit["p"], "n": fit["n"],
            "a": fit["a"], "b": fit["b"], "inicial": fit["a"], "erro_inicial": fit["sa"],
            "referencia": "York et al. (2004)"}


def isocrona_pbpb(r64, s64, r74, s74, rho):
    """Isócrona Pb-Pb inversa (204Pb/206Pb x 207Pb/206Pb), como no IsoplotR.

    O intercepto em 204Pb/206Pb = 0 é a razão 207Pb/206Pb radiogênica.
    """
    X, sX, Y, sY, r = (np.asarray(v, float) for v in (r64, s64, r74, s74, rho))
    x, y = 1 / X, Y / X
    sx = sX / X**2
    rx, ry = sX / X, sY / Y
    sy = y * np.sqrt(rx**2 + ry**2 - 2 * r * rx * ry)
    cxy = x * y * (rx**2 - r * rx * ry)
    fit = york(x, sx, y, sy, cxy / (sx * sy))
    t, st = idades.idade_76(fit["a"], fit["sa"])
    return {"idade": float(t[0]), "erro": float(st[0]), "mswd": fit["mswd"], "p": fit["p"], "n": fit["n"],
            "a": fit["a"], "b": fit["b"], "referencia": "York et al. (2004); Vermeesch (2018a)"}
