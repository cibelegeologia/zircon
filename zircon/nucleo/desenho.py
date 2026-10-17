"""Desenho dos gráficos em matplotlib, sem depender da interface Qt.

Cada função recebe um objeto com os atributos `figura` (Figure) e
`canvas` (com `draw_idle`) e um método `limpar`.
"""
import numpy as np
from matplotlib.patches import Ellipse
from scipy.stats import gaussian_kde

from . import idades
from .grupos import COR_CLASSE


def _elipse(ax, x, y, sx, sy, rho, cor, n_sigma=2):
    cov = np.array([[sx**2, rho * sx * sy], [rho * sx * sy, sy**2]])
    val, vec = np.linalg.eigh(cov)
    ang = np.degrees(np.arctan2(vec[1, 1], vec[0, 1]))
    w, h = 2 * n_sigma * np.sqrt(np.maximum(val[::-1], 0))
    ax.add_patch(Ellipse((x, y), w, h, angle=ang, facecolor=cor + "80", edgecolor=cor, lw=0.8))


def _legenda(ax, graos, agrupar):
    from matplotlib.patches import Patch
    if agrupar == "classe":
        itens = [(c, COR_CLASSE[c]) for c in ("concordante", "discordante", "rejeitado") if (graos.classe == c).any()]
    else:
        itens = [(f"Grupo {int(g)}", graos.cor[graos.grupo == g].iloc[0]) for g in sorted(graos.grupo.unique())]
    ax.legend(handles=[Patch(facecolor=c + "80", edgecolor=c, label=n) for n, c in itens], loc="best", fontsize=8)


def concordia(graf, graos, diagrama="wetherill", agrupar="classe", discordia=None):
    graf.figura.clear()
    ax = graf.figura.add_subplot()
    g = graos.dropna(subset=["r75", "r68"])
    if diagrama == "wetherill":
        xs, sxs, ys, sys_, rhos = (g[c].to_numpy(float) for c in ("r75", "s75", "r68", "s68", "rho"))
        curva = idades.wetherill
        ax.set_xlabel("$^{207}$Pb/$^{235}$U")
        ax.set_ylabel("$^{206}$Pb/$^{238}$U")
    else:
        xs, sxs, ys, sys_, rhos = idades.wetherill_para_tw(g.r75, g.s75, g.r68, g.s68, g.rho)
        curva = idades.tera_wasserburg
        ax.set_xlabel("$^{238}$U/$^{206}$Pb")
        ax.set_ylabel("$^{207}$Pb/$^{206}$Pb")
    for x, y, sx, sy, r, cor in zip(xs, ys, sxs, sys_, rhos, g.cor):
        _elipse(ax, x, y, sx, sy, r, cor)
    xmin, xmax = np.nanmin(xs - 3 * sxs), np.nanmax(xs + 3 * sxs)
    ymin, ymax = np.nanmin(ys - 3 * sys_), np.nanmax(ys + 3 * sys_)
    tmin = max(1e-3, np.nanmin(g.t68) * 0.7)
    tmax = max(np.nanmax(g.t76) * 1.3, np.nanmax(g.t68) * 1.3)
    t = np.linspace(tmin, tmax, 800)
    cx, cy = curva(t)
    ax.plot(cx, cy, color="#444444", lw=1)
    for tm in _marcas(tmin, tmax):
        mx, my = curva(tm)
        ax.plot(mx, my, "o", color="#444444", ms=3)
        ax.annotate(f"{tm:g}", (mx, my), fontsize=7, xytext=(3, -8), textcoords="offset points")
    if discordia and diagrama == "wetherill" and "superior" in discordia:
        xx = np.linspace(xmin, xmax, 10)
        ax.plot(xx, discordia["a"] + discordia["b"] * xx, "--", color="#D55E00", lw=1)
    dx, dy = xmax - xmin, ymax - ymin
    ax.set_xlim(xmin - 0.1 * dx, xmax + 0.1 * dx)
    ax.set_ylim(ymin - 0.1 * dy, ymax + 0.1 * dy)
    ax.set_title("Diagrama concórdia (elipses 2σ)", fontsize=10)
    _legenda(ax, g, agrupar)
    graf.canvas.draw_idle()


def _marcas(tmin, tmax):
    passo = 10 ** np.floor(np.log10((tmax - tmin) / 5))
    for f in (1, 2, 5, 10):
        if (tmax - tmin) / (passo * f) <= 8:
            passo *= f
            break
    return np.arange(np.ceil(tmin / passo) * passo, tmax, passo)


def media_ponderada(graf, graos, coluna, media=None, agrupar="classe"):
    graf.figura.clear()
    ax = graf.figura.add_subplot()
    g = graos.dropna(subset=[coluna]).sort_values(coluna)
    s = g.get("s_" + coluna)
    pos = np.arange(1, len(g) + 1)
    if s is not None and s.notna().any():
        ax.bar(pos, 4 * s, bottom=g[coluna] - 2 * s, color=[c + "B0" for c in g.cor], edgecolor=g.cor, width=0.8)
    else:
        ax.scatter(pos, g[coluna], c=list(g.cor))
    if media is not None:
        m, e = media["Idade (Ma)"], media["± 2σ (Ma)"]
        ax.axhspan(m - e, m + e, color="#cccccc", zorder=0)
        ax.axhline(m, color="#333333", lw=1)
        ax.set_title(f"{media['Cálculo']}: {m:.2f} ± {e:.2f} Ma (2σ), MSWD {media['MSWD']:.2f}, n = {media['n']}",
                     fontsize=9)
    ax.set_xlabel("análises em ordem de idade (barras 2σ)")
    ax.set_ylabel("idade (Ma)")
    _legenda(ax, g, agrupar)
    graf.canvas.draw_idle()


def densidade(graf, graos, coluna="melhor", agrupar="classe"):
    graf.figura.clear()
    ax = graf.figura.add_subplot()
    g = graos.dropna(subset=[coluna])
    t = g[coluna].to_numpy(float)
    if len(t) < 2:
        graf.limpar("Poucas idades para a curva de densidade")
        return
    bins = np.histogram_bin_edges(t, bins="auto")
    grupos = sorted(g.grupo.unique())
    ax.hist([g[coluna][g.grupo == k] for k in grupos], bins=bins, stacked=True,
            color=[g.cor[g.grupo == k].iloc[0] for k in grupos], alpha=0.6, edgecolor="white")
    ax2 = ax.twinx()
    grade = np.linspace(t.min() - 0.05 * np.ptp(t), t.max() + 0.05 * np.ptp(t), 1000)
    ax2.plot(grade, gaussian_kde(t)(grade), color="#333333", lw=1.2)
    ax2.set_yticks([])
    ax.set_xlabel("idade (Ma)")
    ax.set_ylabel("número de grãos")
    ax.set_title(f"Histograma e densidade (KDE), n = {len(t)}", fontsize=10)
    _legenda(ax, g, agrupar)
    graf.canvas.draw_idle()
