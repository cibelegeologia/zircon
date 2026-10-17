"""Exportação para publicação: figuras, Excel formatado, gráficos interativos e dados.

Tamanhos e resoluções seguem as instruções de arte da Elsevier
(largura de 90, 140 ou 190 mm; 300 dpi para cor e 1000 dpi para traço).
"""
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from .grupos import COR_CLASSE

LARGURAS_MM = {"1 coluna (90 mm)": 90, "1,5 coluna (140 mm)": 140, "2 colunas (190 mm)": 190}
FORMATOS_FIGURA = {"png": 600, "tif": 600, "svg": None, "pdf": None, "eps": None}

COLUNAS_SAIDA = {
    "amostra": ("Amostra", None), "analise": ("Análise", None),
    "r75": ("207Pb/235U", "0.00000"), "s75": ("± 1σ", "0.00000"),
    "r68": ("206Pb/238U", "0.000000"), "s68": ("± 1σ", "0.000000"), "rho": ("rho", "0.00"),
    "r76": ("207Pb/206Pb", "0.00000"), "s76": ("± 1σ", "0.00000"),
    "t68": ("Idade 206Pb/238U (Ma)", "0.0"), "s_t68": ("± 1σ (Ma)", "0.0"),
    "t75": ("Idade 207Pb/235U (Ma)", "0.0"), "s_t75": ("± 1σ (Ma)", "0.0"),
    "t76": ("Idade 207Pb/206Pb (Ma)", "0.0"), "s_t76": ("± 1σ (Ma)", "0.0"),
    "melhor": ("Melhor idade (Ma)", "0.0"), "s_melhor": ("± 1σ (Ma)", "0.0"),
    "discordancia": ("Discordância (%)", "0.0"), "classe": ("Classe", None), "grupo": ("Grupo", None),
    "valido": ("Usado na média", None),
}


class _Folha:
    """Imita o widget de gráfico para desenhar sem janela."""

    def __init__(self, largura_mm, altura_mm):
        from matplotlib.figure import Figure
        self.figura = Figure(figsize=(largura_mm / 25.4, altura_mm / 25.4), layout="constrained")
        self.canvas = self

    def draw_idle(self):
        pass

    def limpar(self, texto=""):
        self.figura.clear()


def _estilo_publicacao():
    import matplotlib
    matplotlib.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "legend.fontsize": 7,
        "xtick.labelsize": 7, "ytick.labelsize": 7, "axes.linewidth": 0.6,
        "svg.fonttype": "none", "pdf.fonttype": 42, "ps.fonttype": 42,
    })


def figuras(pasta, resultado, opcoes, largura_mm=90, formatos=("png", "svg", "pdf")):
    """Salva concórdia, média ponderada e distribuição nos formatos pedidos."""
    from ..interface import graficos  # só matplotlib; não abre janela
    from . import estatistica
    _estilo_publicacao()
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    g = resultado.graos
    altura = largura_mm * 0.8
    feitas = []
    desenhos = []
    if "r75" in g:
        disc = estatistica.discordia(g.r75, g.s75, g.r68, g.s68, g.rho) if len(g) >= 3 else None
        desenhos.append(("concordia", lambda f: graficos.concordia(f, g, opcoes.get("diagrama", "wetherill"),
                                                                    opcoes["agrupar"], disc)))
    coluna = {"68": "t68", "76": "t76", "melhor": "melhor"}[opcoes["media_de"]]
    media = next((r for r in resultado.conjunto if r["Cálculo"].startswith("Média ponderada")), None)
    if coluna in g:
        desenhos.append(("media_ponderada", lambda f: graficos.media_ponderada(f, g, coluna, media, opcoes["agrupar"])))
    desenhos.append(("distribuicao_idades", lambda f: graficos.densidade(f, g, "melhor", opcoes["agrupar"])))
    for nome, desenha in desenhos:
        folha = _Folha(largura_mm, altura)
        desenha(folha)
        for fmt in formatos:
            arq = pasta / f"{nome}.{fmt}"
            extra = {"pil_kwargs": {"compression": "tiff_lzw"}} if fmt == "tif" else {}
            folha.figura.savefig(arq, dpi=FORMATOS_FIGURA.get(fmt) or 300, **extra)
            feitas.append(arq)
    return feitas


def excel(caminho, projeto, resultado, opcoes, referencias=None):
    """Planilha formatada: resultados, idades por grão (com cores dos grupos), opções, referências e registro."""
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    g = resultado.graos
    cols = [c for c in COLUNAS_SAIDA if c in g]
    graos = g[cols].copy()
    if "valido" in graos:
        graos["valido"] = graos["valido"].map({True: "sim", False: "não"})
    graos.columns = [COLUNAS_SAIDA[c][0] for c in cols]
    res = pd.DataFrame(resultado.conjunto)
    ops = pd.DataFrame({"Opção": list(opcoes), "Valor": [str(v) for v in opcoes.values()]})
    refs = pd.DataFrame({"Referências (ABNT)": referencias or []})
    reg = pd.DataFrame({"Registro": list(projeto.log) + list(resultado.avisos)})

    fino = Side(style="thin", color="999999")
    cab = PatternFill("solid", fgColor="DDE6EE")
    with pd.ExcelWriter(caminho, engine="openpyxl") as w:
        for nome, df in (("Resultados", res), ("Idades por grão", graos), ("Opções usadas", ops),
                         ("Referências", refs), ("Registro", reg)):
            df.to_excel(w, sheet_name=nome, index=False, startrow=2)
            ws = w.sheets[nome]
            ws["A1"] = f"Zircon - {projeto.nome} - {nome}"
            ws["A1"].font = Font(bold=True, size=12)
            ws["A2"] = f"Gerado em {date.today():%d/%m/%Y}. Erros em 1σ absoluto, salvo indicação."
            ws["A2"].font = Font(italic=True, size=9, color="666666")
            for c in ws[3]:
                c.font = Font(bold=True)
                c.fill = cab
                c.border = Border(bottom=fino, top=fino)
                c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            ws.freeze_panes = "A4"
            for i, col in enumerate(df.columns, 1):
                larg = max([len(str(col))] + [len(f"{v:.6g}" if isinstance(v, float) else str(v))
                                               for v in df[col].head(200)])
                ws.column_dimensions[get_column_letter(i)].width = min(max(10, larg + 2), 90)
            if nome == "Idades por grão":
                for i, c in enumerate(cols, 1):
                    fmt = COLUNAS_SAIDA[c][1]
                    if fmt:
                        for linha in ws.iter_rows(min_row=4, min_col=i, max_col=i):
                            linha[0].number_format = fmt
                for r, cor in enumerate(g["cor"], 4):
                    preenche = PatternFill("solid", fgColor=_clarear(cor))
                    for c in ws[r]:
                        c.fill = preenche
            if nome == "Resultados":
                for linha in ws.iter_rows(min_row=4, min_col=2, max_col=4):
                    for c in linha:
                        c.number_format = "0.00"
                for linha in ws.iter_rows(min_row=4, min_col=5, max_col=6):
                    for c in linha:
                        c.number_format = "0.000"
    return Path(caminho)


def _clarear(cor, f=0.75):
    r, g, b = (int(cor[i:i + 2], 16) for i in (1, 3, 5))
    return "".join(f"{int(v + (255 - v) * f):02X}" for v in (r, g, b))


def _elipse_xy(x, y, sx, sy, rho, n_sigma=2, n=60):
    cov = np.array([[sx**2, rho * sx * sy], [rho * sx * sy, sy**2]])
    val, vec = np.linalg.eigh(cov)
    a = np.linspace(0, 2 * np.pi, n)
    pts = vec @ (n_sigma * np.sqrt(np.maximum(val, 0))[:, None] * np.array([np.cos(a), np.sin(a)]))
    return x + pts[0], y + pts[1]


def interativo(caminho, resultado, opcoes, titulo="Zircon"):
    """Página HTML autônoma (funciona sem internet) com os gráficos interativos.

    Serve como material suplementar: passando o mouse sobre cada grão aparecem
    a análise, as idades e a discordância.
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    from . import idades

    g = resultado.graos
    tem_razoes = "r75" in g
    linhas = 3 if tem_razoes else 2
    nomes = (["Concórdia (Wetherill, elipses 2σ)"] if tem_razoes else []) + \
        ["Melhor idade por grão (barras 2σ)", "Distribuição de idades"]
    fig = make_subplots(rows=linhas, cols=1, subplot_titles=nomes, vertical_spacing=0.08)
    rotulo = lambda k: k if opcoes["agrupar"] == "classe" else f"Grupo {k}"
    chave = "classe" if opcoes["agrupar"] == "classe" else "grupo"

    def dica(r):
        partes = [f"<b>{r.analise}</b>", f"melhor idade: {r.melhor:.1f} ± {2 * r.s_melhor:.1f} Ma (2σ)"
                  if pd.notna(r.get("s_melhor")) else f"idade: {r.melhor:.1f} Ma"]
        if pd.notna(r.get("discordancia")):
            partes.append(f"discordância: {r.discordancia:.1f} %")
        partes.append(f"classe: {r.classe}")
        return "<br>".join(partes)

    linha = 1
    if tem_razoes:
        t = np.linspace(max(1e-3, np.nanmin(g.t68) * 0.7), max(np.nanmax(g.t76), np.nanmax(g.t68)) * 1.3, 400)
        cx, cy = idades.wetherill(t)
        fig.add_trace(go.Scatter(x=cx, y=cy, mode="lines", line=dict(color="#444", width=1), name="concórdia",
                                 hovertext=[f"{v:.0f} Ma" for v in t], hoverinfo="text"), row=1, col=1)
        vistos = set()
        for _, r in g.dropna(subset=["r75", "r68"]).iterrows():
            ex, ey = _elipse_xy(r.r75, r.r68, r.s75, r.s68, r.rho)
            k = r[chave]
            fig.add_trace(go.Scatter(x=ex, y=ey, fill="toself", mode="lines", line=dict(color=r.cor, width=1),
                                     fillcolor=r.cor + "80", name=rotulo(k), legendgroup=str(k),
                                     showlegend=k not in vistos, hovertext=dica(r), hoverinfo="text"),
                          row=1, col=1)
            vistos.add(k)
        fig.update_xaxes(title_text="207Pb/235U", row=1, col=1)
        fig.update_yaxes(title_text="206Pb/238U", row=1, col=1)
        linha = 2
    o = g.dropna(subset=["melhor"]).sort_values("melhor").reset_index(drop=True)
    erro = 2 * o["s_melhor"] if "s_melhor" in o else None
    fig.add_trace(go.Scatter(x=np.arange(1, len(o) + 1), y=o.melhor, mode="markers",
                             marker=dict(color=list(o.cor), size=7),
                             error_y=dict(type="data", array=erro, visible=erro is not None, color="#888"),
                             hovertext=[dica(r) for _, r in o.iterrows()], hoverinfo="text", showlegend=False),
                  row=linha, col=1)
    media = next((r for r in resultado.conjunto if r["Cálculo"].startswith("Média ponderada")), None)
    if media:
        fig.add_hline(y=media["Idade (Ma)"], line=dict(color="#333", width=1), row=linha, col=1,
                      annotation_text=f"{media['Idade (Ma)']:.2f} ± {media['± 2σ (Ma)']:.2f} Ma (2σ), "
                                      f"MSWD {media['MSWD']:.2f}")
    fig.update_yaxes(title_text="idade (Ma)", row=linha, col=1)
    fig.update_xaxes(title_text="análises em ordem de idade", row=linha, col=1)
    for k in sorted(o[chave].unique(), key=str):
        sub = o[o[chave] == k]
        fig.add_trace(go.Histogram(x=sub.melhor, name=rotulo(k), marker_color=sub.cor.iloc[0], opacity=0.7,
                                   legendgroup=str(k), showlegend=not tem_razoes), row=linha + 1, col=1)
    fig.update_layout(barmode="stack", title=titulo, height=420 * linhas, template="simple_white",
                      font=dict(family="Arial", size=12))
    fig.update_xaxes(title_text="idade (Ma)", row=linha + 1, col=1)
    fig.update_yaxes(title_text="número de grãos", row=linha + 1, col=1)
    fig.write_html(caminho, include_plotlyjs=True, full_html=True,
                   config={"toImageButtonOptions": {"format": "svg"}, "displaylogo": False})
    return Path(caminho)


def dados_repositorio(pasta, projeto, resultado, opcoes):
    """CSV + LEIAME para depositar os dados (Mendeley Data, Zenodo, PANGAEA)."""
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    g = resultado.graos
    cols = [c for c in COLUNAS_SAIDA if c in g]
    g[cols].to_csv(pasta / "idades_por_grao.csv", index=False)
    pd.DataFrame(resultado.conjunto).to_csv(pasta / "resultados.csv", index=False)
    if projeto.dados is not None:
        projeto.dados.to_csv(pasta / "dados_importados.csv", index=False)
    descr = "\n".join(f"- {c}: {COLUNAS_SAIDA[c][0]}" for c in cols)
    (pasta / "LEIAME.txt").write_text(
        f"Dados do projeto {projeto.nome}, gerados pelo Zircon em {date.today():%d/%m/%Y}.\n\n"
        "Arquivos: idades_por_grao.csv (uma linha por análise), resultados.csv (idades da amostra), "
        "dados_importados.csv (razões como lidas da planilha do laboratório, padronizadas).\n"
        "Erros em 1 sigma absoluto. Idades em Ma. Separador: vírgula; decimal: ponto.\n"
        "Constantes: lambda238 = 1,55125e-10/a e lambda235 = 9,8485e-10/a (Jaffey et al. 1971); "
        "238U/235U = 137,818 (Hiess et al. 2012).\n\n"
        f"Colunas de idades_por_grao.csv:\n{descr}\n\nOpções do cálculo:\n"
        + "\n".join(f"- {k}: {v}" for k, v in opcoes.items()) + "\n", encoding="utf-8")
    return pasta


def pacote(pasta, projeto, resultado, opcoes, largura_mm=90, formatos=("png", "tif", "svg", "pdf"),
           referencias=None, arquivo_referencias=None):
    """Gera tudo numa pasta: figuras/, interativo/, dados_repositorio/, planilha Excel e metodologia."""
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    figuras(pasta / "figuras", resultado, opcoes, largura_mm, formatos)
    excel(pasta / f"{projeto.nome}_tabelas.xlsx", projeto, resultado, opcoes, referencias)
    (pasta / "interativo").mkdir(exist_ok=True)
    interativo(pasta / "interativo" / f"{projeto.nome}_graficos_interativos.html", resultado, opcoes,
               f"Zircon - {projeto.nome}")
    dados_repositorio(pasta / "dados_repositorio", projeto, resultado, opcoes)
    from .metodologia import gerar
    texto = gerar(projeto, resultado, opcoes, arquivo_referencias)
    (pasta / "metodologia.md").write_text(texto, encoding="utf-8")
    (pasta / "metodologia.txt").write_text(texto.replace("**", "").replace("*", "").replace("# ", ""),
                                           encoding="utf-8")
    return pasta


def referencias_abnt(citacoes, arquivo):
    """Entradas da lista ABNT que correspondem às citações curtas (ex.: 'Ludwig (1998)')."""
    import re
    try:
        entradas = [l for l in Path(arquivo).read_text(encoding="utf-8").splitlines() if l[:1].isupper() and "," in l]
    except OSError:
        return sorted(set(citacoes))
    achadas = []
    for cit in citacoes:
        for parte in re.split(r";", cit):
            m = re.search(r"([A-ZÀ-Ú][\wÀ-ú]+).*?\(?(\d{4}[a-z]?)", parte)
            if not m:
                continue
            autor, ano = m.group(1).upper(), m.group(2)
            for e in entradas:
                if e.upper().startswith(autor) and re.search(rf"\b{ano}\b" if ano[-1].isalpha() else rf"\b{ano}[a-z]?\b", e) and e not in achadas:
                    achadas.append(e)
    return sorted(achadas)
