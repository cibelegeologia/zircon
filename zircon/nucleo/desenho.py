"""Desenho dos gráficos em matplotlib, sem depender da interface Qt.

Cada função recebe um objeto com os atributos `figura` (Figure) e
`canvas` (com `draw_idle`) e um método `limpar`.
"""
import numpy as np
from matplotlib.patches import Ellipse
from scipy.stats import gaussian_kde

import matplotlib

from ..idiomas import N_, num, tr
from ..idiomas import figura as F
from . import idades
from . import grupos
from .grupos import COR_CLASSE

# Fontes com chinês para os gráficos; o matplotlib usa a primeira que existir
# no computador para cada letra (Windows, Mac, Linux).
FONTES = ["DejaVu Sans", "Microsoft YaHei", "SimHei", "PingFang SC", "Hiragino Sans GB", "Noto Sans CJK SC",
          "WenQuanYi Micro Hei", "Arial Unicode MS"]
matplotlib.rcParams["font.sans-serif"] = FONTES
matplotlib.rcParams["axes.unicode_minus"] = False


def _tinta():
    """Cor das linhas de referência: a do texto do tema (preta no fundo branco)."""
    return matplotlib.rcParams["text.color"]


def _hachuras(graos, agrupar):
    """Padrão de cada grão, conforme a classe ou o grupo ("" se os padrões estão desligados)."""
    if agrupar == "classe":
        return [grupos.hachura(classe=c) for c in graos.classe]
    return [grupos.hachura(grupo=int(n)) for n in graos.grupo]


def _elipse(ax, x, y, sx, sy, rho, cor, n_sigma=2, hachura=""):
    cov = np.array([[sx**2, rho * sx * sy], [rho * sx * sy, sy**2]])
    val, vec = np.linalg.eigh(cov)
    ang = np.degrees(np.arctan2(vec[1, 1], vec[0, 1]))
    w, h = 2 * n_sigma * np.sqrt(np.maximum(val[::-1], 0))
    return ax.add_patch(Ellipse((x, y), w, h, angle=ang, facecolor=cor + "80", edgecolor=cor, lw=0.8,
                                hatch=hachura or None))


def info_grao(r):
    """Resumo de um grão para a legenda que aparece com o mouse em cima."""
    def v(c):
        x = r.get(c)
        return x if x is not None and x == x else None  # descarta NaN
    linhas = [f"{tr('Amostra')}: {r.get('amostra', '')}", f"{tr('Análise')}: {r.get('analise', '')}"]
    for t, s_, nome in (("melhor", "s_melhor", N_("Melhor idade")), ("t68", "s_t68", "206Pb/238U"),
                        ("t75", "s_t75", "207Pb/235U"), ("t76", "s_t76", "207Pb/206Pb")):
        if v(t) is not None:
            erro = f" ± {num(2 * v(s_), 1)}" if v(s_) is not None else ""
            linhas.append(f"{tr(nome)}: {num(v(t), 1)}{erro} Ma (2σ)")
    for c, nome in (("r75", "207Pb/235U"), ("r68", "206Pb/238U"), ("r64", "206Pb/204Pb"), ("r74", "207Pb/204Pb"),
                    ("r24", "232Th/204Pb"), ("r84", "208Pb/204Pb")):
        if v(c) is not None and v("melhor") is None:
            erro = f" ± {v('s' + c[1:]) * 2:.4g}" if v("s" + c[1:]) is not None else ""
            linhas.append(f"{nome}: {v(c):.5g}{erro} (2σ)")
    if v("discordancia") is not None:
        linhas.append(f"{tr('Discordância')}: {num(v('discordancia'), 1)} %")
    if r.get("classe") is not None:
        linhas.append(f"{tr('Classe')}: {tr(str(r['classe']))}")
    if r.get("grupo") is not None:
        linhas.append(f"{tr('Grupo')}: {r['grupo']}")
    if r.get("valido") is not None:
        linhas.append(f"{tr('Usado na média')}: {tr('sim') if bool(r['valido']) else tr('não')}")
    return "\n".join(linhas)


def _guarda_info(ax, pares):
    """Liga cada elipse ou barra ao resumo do grão (usado pela janela ao passar o mouse)."""
    ax.zircon_info = list(pares)


def _legenda(ax, graos, agrupar):
    from matplotlib.patches import Patch
    if agrupar == "classe":
        itens = [(F(c), COR_CLASSE[c], grupos.hachura(classe=c)) for c in ("concordante", "discordante", "rejeitado")
                 if (graos.classe == c).any()]
    else:
        itens = [(F("Grupo {n}").format(n=int(g)), graos.cor[graos.grupo == g].iloc[0], grupos.hachura(grupo=int(g)))
                 for g in sorted(graos.grupo.unique())]
    ax.legend(handles=[Patch(facecolor=c + "80", edgecolor=c, hatch=h or None, label=n) for n, c, h in itens],
              loc="best", fontsize="small")


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
    elipses = [_elipse(ax, x, y, sx, sy, r, cor, hachura=h)
               for x, y, sx, sy, r, cor, h in zip(xs, ys, sxs, sys_, rhos, g.cor, _hachuras(g, agrupar))]
    _guarda_info(ax, zip(elipses, (info_grao(r) for _, r in g.iterrows())))
    xmin, xmax = np.nanmin(xs - 3 * sxs), np.nanmax(xs + 3 * sxs)
    ymin, ymax = np.nanmin(ys - 3 * sys_), np.nanmax(ys + 3 * sys_)
    tmin = max(1e-3, np.nanmin(g.t68) * 0.7)
    tmax = max(np.nanmax(g.t76) * 1.3, np.nanmax(g.t68) * 1.3)
    t = np.linspace(tmin, tmax, 800)
    cx, cy = curva(t)
    ax.plot(cx, cy, color=_tinta(), lw=matplotlib.rcParams["lines.linewidth"] * 0.7)
    for tm in _marcas(tmin, tmax):
        mx, my = curva(tm)
        ax.plot(mx, my, "o", color=_tinta(), ms=3)
        ax.annotate(f"{tm:g}", (mx, my), fontsize="small", xytext=(3, -8), textcoords="offset points")
    if discordia and diagrama == "wetherill" and "superior" in discordia:
        xx = np.linspace(xmin, xmax, 10)
        ax.plot(xx, discordia["a"] + discordia["b"] * xx, "--", color="#D55E00", lw=1)
    dx, dy = xmax - xmin, ymax - ymin
    ax.set_xlim(xmin - 0.1 * dx, xmax + 0.1 * dx)
    ax.set_ylim(ymin - 0.1 * dy, ymax + 0.1 * dy)
    ax.set_title(F("Diagrama concórdia (elipses 2σ)"), fontsize="medium")
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
        barras = ax.bar(pos, 4 * s, bottom=g[coluna] - 2 * s, color=[c + "B0" for c in g.cor], edgecolor=g.cor,
                        width=0.8)
        for barra, h in zip(barras, _hachuras(g, agrupar)):
            barra.set_hatch(h or None)
        _guarda_info(ax, zip(barras, (info_grao(r) for _, r in g.iterrows())))
    else:
        pontos = ax.scatter(pos, g[coluna], c=list(g.cor))
        _guarda_info(ax, [(pontos, [info_grao(r) for _, r in g.iterrows()])])
    if media is not None:
        m, e = media["Idade (Ma)"], media["± 2σ (Ma)"]
        ax.axhspan(m - e, m + e, color="#999999", alpha=0.35, zorder=0)
        ax.axhline(m, color=_tinta(), lw=matplotlib.rcParams["lines.linewidth"] * 0.7)
        ax.set_title(f"{F(media['Cálculo'])}: {num(m)} ± {num(e)} Ma (2σ), MSWD {num(media['MSWD'])}, "
                     f"n = {media['n']}", fontsize="medium")
    ax.set_xlabel(F("análises em ordem de idade (barras 2σ)"))
    ax.set_ylabel(F("idade (Ma)"))
    _legenda(ax, g, agrupar)
    graf.canvas.draw_idle()


def densidade(graf, graos, coluna="melhor", agrupar="classe"):
    graf.figura.clear()
    ax = graf.figura.add_subplot()
    g = graos.dropna(subset=[coluna])
    t = g[coluna].to_numpy(float)
    if len(t) < 2:
        graf.limpar(N_("Poucas idades para a curva de densidade"))
        return
    bins = np.histogram_bin_edges(t, bins="auto")
    ks = sorted(g.grupo.unique())
    _, _, conjuntos = ax.hist([g[coluna][g.grupo == k] for k in ks], bins=bins, stacked=True,
                              color=[g.cor[g.grupo == k].iloc[0] for k in ks], alpha=0.6, edgecolor="white")
    if grupos.usar_padroes():
        for k, barras in zip(ks, conjuntos if len(ks) > 1 else [conjuntos]):
            sub = g[g.grupo == k]
            h = grupos.hachura(classe=sub.classe.iloc[0]) if agrupar == "classe" else grupos.hachura(grupo=int(k))
            for barra in barras:
                barra.set_hatch(h or None)
                barra.set_edgecolor(_tinta())
    ax2 = ax.twinx()
    grade = np.linspace(t.min() - 0.05 * np.ptp(t), t.max() + 0.05 * np.ptp(t), 1000)
    ax2.plot(grade, gaussian_kde(t)(grade), color=_tinta())
    ax2.set_yticks([])
    ax.set_xlabel(F("idade (Ma)"))
    ax.set_ylabel(F("número de grãos"))
    ax.set_title(F("Histograma e densidade (KDE), n = {n}").format(n=len(t)), fontsize="medium")
    _legenda(ax, g, agrupar)
    graf.canvas.draw_idle()


def isocrona(graf, graos, iso):
    """Diagrama de isócrona Th-Pb (232Th/204Pb x 208Pb/204Pb) ou Pb-Pb (206Pb/204Pb x 207Pb/204Pb)."""
    graf.figura.clear()
    ax = graf.figura.add_subplot()
    if iso["tipo"] == "th-pb":
        x, sx, y, sy = (graos[c].to_numpy(float) for c in ("r24", "s24", "r84", "s84"))
        a, b = iso["a"], iso["b"]
        ax.set_xlabel("$^{232}$Th/$^{204}$Pb")
        ax.set_ylabel("$^{208}$Pb/$^{204}$Pb")
    else:
        x, sx, y, sy = (graos[c].to_numpy(float) for c in ("r64", "s64", "r74", "s74"))
        a, b = iso["b"], iso["a"]  # reta da isócrona inversa vista no diagrama normal
        ax.set_xlabel("$^{206}$Pb/$^{204}$Pb")
        ax.set_ylabel("$^{207}$Pb/$^{204}$Pb")
    rho = graos["rho"].to_numpy(float)
    elipses = [_elipse(ax, xi, yi, sxi, syi, r, cor) for xi, yi, sxi, syi, r, cor in zip(x, y, sx, sy, rho, graos.cor)]
    _guarda_info(ax, zip(elipses, (info_grao(r) for _, r in graos.iterrows())))
    xx = np.linspace(min(0, np.nanmin(x)), np.nanmax(x + 3 * sx) * 1.05, 10)
    ax.plot(xx, a + b * xx, "--", color="#D55E00", lw=1)
    ax.set_title(F("Isócrona: {idade} ± {erro} Ma (2σ), MSWD {mswd}, n = {n} (elipses 2σ)").format(
        idade=num(iso["idade"]), erro=num(2 * iso["erro"]), mswd=num(iso["mswd"]), n=iso["n"]), fontsize="medium")
    graf.canvas.draw_idle()
