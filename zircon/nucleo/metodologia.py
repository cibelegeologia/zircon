"""Texto de metodologia pronto para o artigo.

Descreve o que foi calculado, com quais opções, e cita cada método. Sai no
idioma escolhido no programa e, se ele não for o inglês, também em inglês,
que é a língua da maioria das revistas. O texto muda conforme o tipo de
dado e as opções escolhidas.
"""
from datetime import date

from .. import __version__, idiomas
from .exportacao import referencias_abnt
from .grupos import nome_conjunto

CITA_SOFTWARE = "Zircon v{v} (https://github.com/cibelegeologia/zircon)"


def _fmt(v, casas, cod):
    s = f"{v:.{casas}f}"
    return s.replace(".", ",") if cod in idiomas._DECIMAL_VIRGULA else s


def _resultados(conjunto, cod):
    t = lambda s: idiomas.em(cod, s)  # noqa: E731
    linhas = []
    for r in conjunto:
        p = (f"p < {_fmt(0.001, 3, cod)}" if r["p"] < 0.001 else f"p = {_fmt(r['p'], 3, cod)}")
        conj = f"{nome_conjunto(r['Conjunto'], t)}, " if r.get("Conjunto") else ""
        linhas.append(f"- {conj}{t(r['Cálculo'])}: {_fmt(r['Idade (Ma)'], 2, cod)} ± {_fmt(r['± 2σ (Ma)'], 2, cod)} Ma (2σ), "
                      f"MSWD = {_fmt(r['MSWD'], 2, cod)}, {p}, n = {r['n']}")
    return "\n".join(linhas)


def _frases(cod, projeto, resultado, op):
    """Frases da metodologia num idioma e as citações usadas."""
    t = lambda s: idiomas.em(cod, s)  # noqa: E731
    tipo = projeto.tipo
    razoes = tipo in ("wetherill", "wetherill-204", "tera-wasserburg")
    sw = CITA_SOFTWARE.format(v=__version__)
    corte = f"{op['corte_76']:.0f}"
    disc = _fmt(op["limite_discordancia"], 1, cod).rstrip("0").rstrip(",.")
    citacoes = ["Jaffey et al. (1971)", "Hiess et al. (2012)", "Horstwood et al. (2016)", "Vermeesch (2018a)"]
    f = []
    if tipo == "wetherill":
        f.append(t("As razões isotópicas 207Pb/235U e 206Pb/238U e as correlações de erro (rho) fornecidas pelo "
                   "laboratório foram processadas no programa {sw}, cujos cálculos reproduzem os do IsoplotR "
                   "(Vermeesch, 2018a).").format(sw=sw))
    elif razoes:
        f.append(t("As razões isotópicas 238U/206Pb e 207Pb/206Pb e as correlações de erro (rho) fornecidas pelo "
                   "laboratório foram processadas no programa {sw}, cujos cálculos reproduzem os do IsoplotR "
                   "(Vermeesch, 2018a).").format(sw=sw))
    else:
        f.append(t("As idades por grão fornecidas pelo laboratório foram processadas no programa {sw}, cujos "
                   "cálculos reproduzem os do IsoplotR (Vermeesch, 2018a).").format(sw=sw))
    f.append(t("Os erros foram convertidos para 1σ absoluto antes dos cálculos."))
    if razoes:
        f.append(t("As idades foram calculadas com as constantes de decaimento de Jaffey et al. (1971) e a razão "
                   "238U/235U = {razao} de Hiess et al. (2012).").format(razao=_fmt(137.818, 3, cod)))
    if tipo == "wetherill-204" and op.get("pb_comum", "nenhuma") != "nenhuma":
        if op["pb_comum"] == "stacey_kramers":
            citacoes += ["Stacey e Kramers (1975)", "Williams (1998)"]
            f.append(t("O Pb comum foi corrigido pelo 204Pb, com a composição do modelo de Stacey e Kramers (1975) "
                       "na idade de cada grão, calculada de forma iterativa (Williams, 1998)."))
        else:
            citacoes += ["Tatsumoto et al. (1973)", "Williams (1998)"]
            f.append(t("O Pb comum foi corrigido pelo 204Pb com a composição fixa de Canyon Diablo "
                       "(Tatsumoto et al., 1973; Williams, 1998)."))
    if razoes or "t76" in resultado.graos:
        citacoes += ["Gehrels (2014)", "Spencer et al. (2016)"]
        f.append(t("Como idade de cada grão foi usada a idade 206Pb/238U para grãos mais jovens que {corte} Ma e a "
                   "idade 207Pb/206Pb para os mais antigos (Gehrels, 2014).").format(corte=corte))
        f.append(t("A discordância foi calculada como 100 × (1 − t206/238 / t207/206)."))
        if op["usar_discordantes"]:
            f.append(t("Grãos com discordância acima de {disc} % foram mantidos nos cálculos de idade da amostra "
                       "(Spencer et al., 2016).").format(disc=disc))
        else:
            f.append(t("Grãos com discordância acima de {disc} % foram excluídos dos cálculos de idade da amostra "
                       "(Spencer et al., 2016).").format(disc=disc))
    if any(r["Cálculo"].startswith("Média ponderada") for r in resultado.conjunto):
        citacoes.append("Wendt e Carl (1991)")
        f.append(t("A idade da amostra foi calculada como média ponderada pelo inverso da variância, com o MSWD e o "
                   "valor-p do teste qui-quadrado como medidas de homogeneidade (Wendt e Carl, 1991)."))
        if op["efeitos_aleatorios"]:
            f.append(t("Foi usado o modelo de efeitos aleatórios, que estima a dispersão geológica além da "
                       "incerteza analítica (Vermeesch, 2018a)."))
        if op["rejeitar_outliers"]:
            f.append(t("Outliers foram rejeitados pelo critério de Chauvenet generalizado (Vermeesch, 2018a)."))
    if any(r["Cálculo"] == "Idade concórdia" for r in resultado.conjunto):
        citacoes.append("Ludwig (1998)")
        f.append(t("A idade concórdia foi calculada pelo método de Ludwig (1998)."))
    if any(r["Cálculo"].startswith("Discórdia") for r in resultado.conjunto):
        citacoes.append("York et al. (2004)")
        f.append(t("Os interceptos da discórdia foram obtidos por regressão linear com erros correlacionados "
                   "(York et al., 2004) no diagrama de Wetherill."))
    g = resultado.graos
    if "ativo" in g and not g["ativo"].all():
        f.append(t("{n} de {total} análises foram deixadas fora dos cálculos por escolha do pesquisador.").format(
            n=int((~g["ativo"].astype(bool)).sum()), total=len(g)))
    if op.get("calcular_por") == "conjunto":
        f.append(t("As idades foram calculadas separadamente para cada conjunto de análises ({conjuntos}).").format(
            conjuntos=", ".join(dict.fromkeys(nome_conjunto(r["Conjunto"], t) for r in resultado.conjunto
                                              if r.get("Conjunto")))))
    if op["agrupar"] in ("populacoes", "amostra_populacoes"):
        citacoes.append("Vermeesch (2012)")
        f.append(t("As populações de idade foram separadas pelos mínimos da curva de densidade (KDE) das idades "
                   "(Vermeesch, 2012)."))
    f.append(t("As incertezas das idades da amostra são apresentadas em 2σ e incluem só a incerteza analítica, sem "
               "a das constantes de decaimento e da calibração (nível x ± y de Horstwood et al., 2016)."))
    return f, citacoes


def _frases_isocrona(cod, resultado):
    t = lambda s: idiomas.em(cod, s)  # noqa: E731
    sw = CITA_SOFTWARE.format(v=__version__)
    r = resultado.conjunto[0]
    idade = (f"{_fmt(r['Idade (Ma)'], 2, cod)} ± {_fmt(r['± 2σ (Ma)'], 2, cod)} Ma (2σ), "
             f"MSWD = {_fmt(r['MSWD'], 2, cod)}, n = {r['n']}")
    if resultado.isocrona["tipo"] == "th-pb":
        f = t("As razões 232Th/204Pb e 208Pb/204Pb foram regredidas por mínimos quadrados com erros correlacionados "
              "(York et al., 2004) no programa {sw}. A idade foi obtida da inclinação da isócrona com a constante de "
              "decaimento do 232Th de Le Roux e Glendenin (1963): {idade}.").format(sw=sw, idade=idade)
        cits = ["York et al. (2004)", "Le Roux e Glendenin (1963)", "Vermeesch (2018a)"]
    else:
        f = t("As razões 206Pb/204Pb e 207Pb/204Pb foram regredidas numa isócrona inversa (204Pb/206Pb x "
              "207Pb/206Pb) com erros correlacionados (York et al., 2004) no programa {sw}, como no IsoplotR "
              "(Vermeesch, 2018a). A idade Pb-Pb foi obtida da razão 207Pb/206Pb radiogênica (intercepto), com as "
              "constantes de Jaffey et al. (1971) e 238U/235U = {razao} (Hiess et al., 2012): {idade}."
              ).format(sw=sw, idade=idade, razao=_fmt(137.818, 3, cod))
        cits = ["York et al. (2004)", "Vermeesch (2018a)", "Jaffey et al. (1971)", "Hiess et al. (2012)"]
    return [f], cits


def gerar(projeto, resultado, opcoes, arquivo_referencias=None):
    """Texto em Markdown no idioma do programa, depois em inglês, depois as referências ABNT."""
    isocrona = projeto.tipo in ("pb-pb", "th-pb")
    escolhido = idiomas.atual()
    cods = [escolhido] + ([] if escolhido == "en" else ["en"])
    tr = idiomas.tr
    partes = [tr("# Metodologia: {nome}").format(nome=projeto.nome), "",
              "*" + tr("Texto gerado pelo Zircon {versao} em {data}. Revise antes de usar.").format(
                  versao=__version__, data=f"{date.today():%d/%m/%Y}") + "*", ""]
    citacoes = []
    for cod in cods:
        if isocrona:
            frases, citacoes = _frases_isocrona(cod, resultado)
        else:
            frases, citacoes = _frases(cod, projeto, resultado, opcoes)
        partes += [f"## {idiomas.IDIOMAS[cod]}", "", " ".join(frases), ""]
        if resultado.conjunto and not isocrona:
            partes += [idiomas.em(cod, "Resultados:"), "", _resultados(resultado.conjunto, cod), ""]
    if arquivo_referencias:
        refs = referencias_abnt(citacoes, arquivo_referencias)
        partes += ["## " + tr("Referências (ABNT NBR 6023)"), ""] + [f"{r}\n" for r in refs]
    return "\n".join(partes)
