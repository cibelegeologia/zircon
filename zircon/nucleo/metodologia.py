"""Texto de metodologia pronto para o artigo, em português e inglês.

Descreve o que foi calculado, com quais opções, e cita cada método.
O texto muda conforme o tipo de dado e as opções escolhidas.
"""
from datetime import date

from .. import __version__
from .exportacao import referencias_abnt

CITA_SOFTWARE = "Zircon v{v} (https://github.com/cibelegeologia/zircon)"


def _fmt(v, casas=2, decimal=","):
    s = f"{v:.{casas}f}"
    return s.replace(".", decimal) if decimal == "," else s


def _resultados(conjunto, idioma):
    dec = "," if idioma == "pt" else "."
    nomes_en = {"Média ponderada": "Weighted mean", "Idade concórdia": "Concordia age",
                "Discórdia: intercepto superior": "Discordia upper intercept",
                "Discórdia: intercepto inferior": "Discordia lower intercept",
                "melhor idade": "preferred age"}
    linhas = []
    for r in conjunto:
        nome = r["Cálculo"]
        if idioma == "en":
            for pt, en in nomes_en.items():
                nome = nome.replace(pt, en)
        linhas.append(f"- {nome}: {_fmt(r['Idade (Ma)'], 2, dec)} ± {_fmt(r['± 2σ (Ma)'], 2, dec)} Ma (2σ), "
                      f"MSWD = {_fmt(r['MSWD'], 2, dec)}, "
                      + (f"p < {_fmt(0.001, 3, dec)}" if r['p'] < 0.001 else f"p = {_fmt(r['p'], 3, dec)}")
                      + f", n = {r['n']}")
    return "\n".join(linhas)


def gerar(projeto, resultado, opcoes, arquivo_referencias=None):
    """Devolve o texto em Markdown (português, depois inglês, depois referências ABNT)."""
    tipo = projeto.tipo
    op = opcoes
    razoes = tipo in ("wetherill", "wetherill-204", "tera-wasserburg")
    if tipo in ("pb-pb", "th-pb"):
        return _isocrona(projeto, resultado, arquivo_referencias)
    corte = f"{op['corte_76']:.0f}"
    disc = f"{op['limite_discordancia']:g}"
    sw = CITA_SOFTWARE.format(v=__version__)
    citacoes = ["Jaffey et al. (1971)", "Hiess et al. (2012)", "Horstwood et al. (2016)", "Vermeesch (2018a)"]
    pt, en = [], []

    if razoes:
        entrada_pt = ("As razões isotópicas 207Pb/235U e 206Pb/238U" if tipo == "wetherill"
                      else "As razões isotópicas 238U/206Pb e 207Pb/206Pb") + \
            " e as correlações de erro (rho) fornecidas pelo laboratório"
        entrada_en = ("The 207Pb/235U and 206Pb/238U ratios" if tipo == "wetherill"
                      else "The 238U/206Pb and 207Pb/206Pb ratios") + \
            " and error correlations (rho) reported by the laboratory"
    else:
        entrada_pt = "As idades por grão fornecidas pelo laboratório"
        entrada_en = "The single-grain ages reported by the laboratory"
    pt.append(f"{entrada_pt} foram processadas no programa {sw}, cujos cálculos reproduzem os do IsoplotR "
              f"(Vermeesch, 2018a). Os erros foram convertidos para 1σ absoluto antes dos cálculos.")
    en.append(f"{entrada_en} were processed with {sw}, whose calculations reproduce those of IsoplotR "
              f"(Vermeesch, 2018a). Uncertainties were converted to absolute 1σ before calculation.")
    if razoes:
        pt.append("As idades foram calculadas com as constantes de decaimento de Jaffey et al. (1971) e a razão "
                  "238U/235U = 137,818 de Hiess et al. (2012).")
        en.append("Ages were calculated with the decay constants of Jaffey et al. (1971) and a 238U/235U ratio "
                  "of 137.818 (Hiess et al., 2012).")
    if tipo == "wetherill-204" and op.get("pb_comum", "nenhuma") != "nenhuma":
        if op["pb_comum"] == "stacey_kramers":
            citacoes += ["Stacey e Kramers (1975)", "Williams (1998)"]
            pt.append("O Pb comum foi corrigido pelo 204Pb, com a composição do modelo de Stacey e Kramers (1975) "
                      "na idade de cada grão, calculada de forma iterativa (Williams, 1998).")
            en.append("Common Pb was corrected using 204Pb and the Stacey and Kramers (1975) model composition at "
                      "the age of each grain, calculated iteratively (Williams, 1998).")
        else:
            citacoes += ["Tatsumoto et al. (1973)", "Williams (1998)"]
            pt.append("O Pb comum foi corrigido pelo 204Pb com a composição fixa de Canyon Diablo "
                      "(Tatsumoto et al., 1973; Williams, 1998).")
            en.append("Common Pb was corrected using 204Pb and the Canyon Diablo composition "
                      "(Tatsumoto et al., 1973; Williams, 1998).")
    if razoes or "t76" in resultado.graos:
        citacoes += ["Gehrels (2014)", "Spencer et al. (2016)"]
        pt.append(f"Como idade de cada grão foi usada a idade 206Pb/238U para grãos mais jovens que {corte} Ma e a "
                  f"idade 207Pb/206Pb para os mais antigos (Gehrels, 2014). A discordância foi calculada como "
                  f"100 × (1 − t206/238 / t207/206), e grãos com discordância acima de {disc} % foram "
                  + ("mantidos" if op["usar_discordantes"] else "excluídos") + " dos cálculos de idade da amostra "
                  "(Spencer et al., 2016).")
        en.append(f"The 206Pb/238U age was used for grains younger than {corte} Ma and the 207Pb/206Pb age for "
                  f"older grains (Gehrels, 2014). Discordance was calculated as 100 × (1 − t206/238 / t207/206), "
                  f"and grains more than {disc} % discordant were "
                  + ("retained in" if op["usar_discordantes"] else "excluded from") +
                  " the sample age calculations (Spencer et al., 2016).")
    media = next((r for r in resultado.conjunto if r["Cálculo"].startswith("Média ponderada")), None)
    if media:
        citacoes.append("Wendt e Carl (1991)")
        frase_pt = ("A idade da amostra foi calculada como média ponderada pelo inverso da variância, com o MSWD e "
                    "o valor-p do teste qui-quadrado como medidas de homogeneidade (Wendt e Carl, 1991)")
        frase_en = ("The sample age was calculated as an inverse-variance weighted mean, with the MSWD and the "
                    "chi-square p-value as measures of homogeneity (Wendt and Carl, 1991)")
        if op["efeitos_aleatorios"]:
            frase_pt += (". Foi usado o modelo de efeitos aleatórios, que estima a dispersão geológica além da "
                         "incerteza analítica (Vermeesch, 2018a)")
            frase_en += (". A random-effects model was used, which estimates the geological dispersion in excess "
                         "of the analytical uncertainty (Vermeesch, 2018a)")
        if op["rejeitar_outliers"]:
            frase_pt += ". Outliers foram rejeitados pelo critério de Chauvenet generalizado (Vermeesch, 2018a)"
            frase_en += ". Outliers were rejected with a generalised Chauvenet criterion (Vermeesch, 2018a)"
        pt.append(frase_pt + ".")
        en.append(frase_en + ".")
    if any(r["Cálculo"] == "Idade concórdia" for r in resultado.conjunto):
        citacoes.append("Ludwig (1998)")
        pt.append("A idade concórdia foi calculada pelo método de Ludwig (1998).")
        en.append("The concordia age was calculated following Ludwig (1998).")
    if any(r["Cálculo"].startswith("Discórdia") for r in resultado.conjunto):
        citacoes.append("York et al. (2004)")
        pt.append("Os interceptos da discórdia foram obtidos por regressão linear com erros correlacionados "
                  "(York et al., 2004) no diagrama de Wetherill.")
        en.append("Discordia intercepts were obtained by linear regression with correlated errors "
                  "(York et al., 2004) in Wetherill space.")
    if op["agrupar"] == "populacoes":
        citacoes.append("Vermeesch (2012)")
        pt.append("As populações de idade foram separadas pelos mínimos da curva de densidade (KDE) das idades "
                  "(Vermeesch, 2012).")
        en.append("Age populations were separated at the minima of the kernel density estimate (Vermeesch, 2012).")
    pt.append("As incertezas das idades da amostra são apresentadas em 2σ e incluem só a incerteza analítica, sem "
              "a das constantes de decaimento e da calibração (nível x ± y de Horstwood et al., 2016).")
    en.append("Sample age uncertainties are quoted at 2σ and include analytical uncertainty only, without decay "
              "constant or calibration uncertainties (the x ± y level of Horstwood et al., 2016).")

    partes = [f"# Metodologia: {projeto.nome}", "",
              f"*Texto gerado pelo Zircon {__version__} em {date.today():%d/%m/%Y}. Revise antes de usar.*", "",
              "## Português", "", " ".join(pt), ""]
    if resultado.conjunto:
        partes += ["Resultados:", "", _resultados(resultado.conjunto, "pt"), ""]
    partes += ["## English", "", " ".join(en), ""]
    if resultado.conjunto:
        partes += ["Results:", "", _resultados(resultado.conjunto, "en"), ""]
    if arquivo_referencias:
        refs = referencias_abnt(citacoes, arquivo_referencias)
        partes += ["## Referências (ABNT NBR 6023)", ""] + [f"{r}\n" for r in refs]
    return "\n".join(partes)


def _isocrona(projeto, resultado, arquivo_referencias):
    iso = resultado.isocrona
    sw = CITA_SOFTWARE.format(v=__version__)
    r = resultado.conjunto[0]
    idade_pt = f"{_fmt(r['Idade (Ma)'])} ± {_fmt(r['± 2σ (Ma)'])} Ma (2σ), MSWD = {_fmt(r['MSWD'])}, n = {r['n']}"
    idade_en = idade_pt.replace(",", ".").replace(". n", ", n").replace(". MSWD", ", MSWD")
    if iso["tipo"] == "th-pb":
        pt = (f"As razões 232Th/204Pb e 208Pb/204Pb foram regredidas por mínimos quadrados com erros correlacionados "
              f"(York et al., 2004) no programa {sw}. A idade foi obtida da inclinação da isócrona com a constante de "
              f"decaimento do 232Th de Le Roux e Glendenin (1963): {idade_pt}.")
        en = (f"The 232Th/204Pb and 208Pb/204Pb ratios were regressed by least squares with correlated errors "
              f"(York et al., 2004) using {sw}. The age was calculated from the isochron slope with the 232Th decay "
              f"constant of Le Roux and Glendenin (1963): {idade_en}.")
        cits = ["York et al. (2004)", "Le Roux e Glendenin (1963)", "Vermeesch (2018a)"]
    else:
        pt = (f"As razões 206Pb/204Pb e 207Pb/204Pb foram regredidas numa isócrona inversa (204Pb/206Pb x "
              f"207Pb/206Pb) com erros correlacionados (York et al., 2004) no programa {sw}, como no IsoplotR "
              f"(Vermeesch, 2018a). A idade Pb-Pb foi obtida da razão 207Pb/206Pb radiogênica (intercepto), com as "
              f"constantes de Jaffey et al. (1971) e 238U/235U = 137,818 (Hiess et al., 2012): {idade_pt}.")
        en = (f"The 206Pb/204Pb and 207Pb/204Pb ratios were regressed as an inverse isochron (204Pb/206Pb vs "
              f"207Pb/206Pb) with correlated errors (York et al., 2004) using {sw}, as in IsoplotR (Vermeesch, "
              f"2018a). The Pb-Pb age was calculated from the radiogenic 207Pb/206Pb intercept with the decay "
              f"constants of Jaffey et al. (1971) and 238U/235U = 137.818 (Hiess et al., 2012): {idade_en}.")
        cits = ["York et al. (2004)", "Vermeesch (2018a)", "Jaffey et al. (1971)", "Hiess et al. (2012)"]
    partes = [f"# Metodologia: {projeto.nome}", "",
              f"*Texto gerado pelo Zircon {__version__} em {date.today():%d/%m/%Y}. Revise antes de usar.*", "",
              "## Português", "", pt, "", "## English", "", en, ""]
    if arquivo_referencias:
        partes += ["## Referências (ABNT NBR 6023)", ""] + [f"{x}\n" for x in referencias_abnt(cits, arquivo_referencias)]
    return "\n".join(partes)
