"""Junta importação, idades por grão, cálculos de conjunto e grupos."""
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from ..idiomas import N_, num, tr
from . import estatistica, grupos, idades, pbcomum

OPCOES_PADRAO = {
    "corte_76": 1000.0,          # Ma: acima disso a melhor idade é 207Pb/206Pb
    "limite_discordancia": 10.0,  # %
    "media_de": "melhor",         # "68", "76" ou "melhor"
    "efeitos_aleatorios": True,
    "rejeitar_outliers": True,
    "usar_discordantes": False,
    "agrupar": "classe",          # "classe", "populacoes" ou "manual"
    "minimo_por_populacao": 3,
    "pb_comum": "stacey_kramers",  # "nenhuma", "fixo" ou "stacey_kramers" (só com 204Pb)
    "calcular_por": "juntos",     # "juntos" (todos os grãos ligados) ou "conjunto" (cada conjunto à parte)
}


COR_FORA = "#B0B0B0"  # grãos fora do cálculo


@dataclass
class Resultado:
    graos: pd.DataFrame
    conjunto: list = field(default_factory=list)   # dicionários para a tabela de resultados
    avisos: list = field(default_factory=list)
    isocrona: dict = None
    discordias: list = field(default_factory=list)  # uma por conjunto calculado, para o diagrama

    def medias(self):
        """Linhas de média ponderada (uma por conjunto quando o cálculo é por conjunto)."""
        return [r for r in self.conjunto if r["Cálculo"].startswith("Média ponderada")]


def _linha(nome, r, chave="media", erro="erro", n=None):
    return {"Cálculo": nome, "Idade (Ma)": r.get(chave), "± 1σ (Ma)": r.get(erro),
            "± 2σ (Ma)": None if r.get(erro) is None else 2 * r[erro],
            "MSWD": r.get("mswd"), "p": r.get("p"), "n": n or r.get("n"),
            "Referência": r.get("referencia", "")}


def idades_por_grao(dados, tipo, opcoes):
    g = dados[["amostra", "analise"]].copy()
    if tipo == "wetherill-204":
        if opcoes["pb_comum"] == "nenhuma":
            pass
        else:
            r75, s75, r68, s68, rho = pbcomum.corrigir_204(dados, opcoes["pb_comum"])
            dados = dados.assign(r75=r75, s75=s75, r68=r68, s68=s68, rho=rho)
        tipo = "wetherill"
    if tipo == "tera-wasserburg":
        r75, s75, r68, s68, rho = idades.tw_para_wetherill(dados.r86, dados.s86, dados.r76, dados.s76, dados.rho)
        g["r75"], g["s75"], g["r68"], g["s68"], g["rho"] = r75, s75, r68, s68, rho
        g["r76"], g["s76"] = dados.r76, dados.s76
    elif tipo == "wetherill":
        for c in ("r75", "s75", "r68", "s68", "rho"):
            g[c] = dados[c]
        _, _, r76, s76, _ = idades.wetherill_para_tw(dados.r75, dados.s75, dados.r68, dados.s68, dados.rho)
        g["r76"], g["s76"] = r76, s76
    if tipo in ("wetherill", "tera-wasserburg"):
        g["t75"], g["s_t75"] = idades.idade_75(g.r75, g.s75)
        g["t68"], g["s_t68"] = idades.idade_68(g.r68, g.s68)
        g["t76"], g["s_t76"] = idades.idade_76(g.r76, g.s76)
    else:
        for t, s in (("t75", "s75"), ("t68", "s68"), ("t76", "s76")):
            if t in dados:
                g[t] = dados[t]
                g["s_" + t] = dados.get(s, np.nan)
        if "idade" in dados:
            g["melhor"] = dados["idade"]
            g["s_melhor"] = dados.get("s_idade", np.nan)
    if "t68" in g and "t76" in g:
        g["discordancia"] = idades.discordancia(g.t68, g.t76)
        g["melhor"], g["s_melhor"] = idades.melhor_idade(g.t68, g.s_t68, g.t76, g.s_t76, opcoes["corte_76"])
    elif "melhor" not in g and "t68" in g:
        g["melhor"], g["s_melhor"] = g.t68, g.s_t68
    if "discordancia" not in g:
        g["discordancia"] = 0.0
    return g


def _isocrona(dados, tipo, ativo):
    g = dados[["amostra", "analise"]].copy()
    d = dados[ativo]
    if tipo == "pb-pb":
        r = estatistica.isocrona_pbpb(d.r64, d.s64, d.r74, d.s74, d.rho)
        nome = N_("Isócrona Pb-Pb")
        for c in ("r64", "s64", "r74", "s74", "rho"):
            g[c] = dados[c]
    else:
        r = estatistica.isocrona_thpb(d.r24, d.s24, d.r84, d.s84, d.rho)
        nome = N_("Isócrona Th-Pb")
        for c in ("r24", "s24", "r84", "s84", "rho"):
            g[c] = dados[c]
    res = Resultado(g, [_linha(nome, r, "idade")])
    res.isocrona = {"tipo": tipo, **r}
    g["discordancia"] = np.nan
    g["valido"] = True
    g["classe"] = "concordante"
    g["grupo"] = 1
    g["conjunto"] = "concordante"
    g["ativo"] = ativo
    if r["p"] < 0.05:
        res.avisos.append(tr("Isócrona com p < 0,05: os pontos espalham mais do que os erros explicam"))
    return res


def calcular(dados, tipo, opcoes=None, grupo_manual=None, estilos=None, so_paleta=False, destaques=None,
             desligados=None, unidades=None):
    """estilos: {conjunto: {"cor": "#RRGGBB", "simbolo": código, "hachura": código}} escolhidos pelo
    pesquisador; destaques: o mesmo por grão ({linha da planilha: {..., "rotulo": nome na legenda}});
    com so_paleta (modo para daltônicos), cores fora da paleta atual são ignoradas.
    desligados: {"conjuntos": [chaves], "graos": [linhas]} que ficam fora de todos os cálculos.
    unidades: {amostra: unidade}, para juntar várias amostras numa só (ex.: amostras de uma mesma camada)."""
    op = {**OPCOES_PADRAO, **(opcoes or {})}
    desligados = desligados or {}
    fora_graos = {int(i) for i in desligados.get("graos", [])}
    if tipo in ("pb-pb", "th-pb"):
        ativo = ~dados.index.isin(fora_graos)
        res = _isocrona(dados, tipo, ativo)
        _aplica_estilos(res.graos, "classe", estilos, so_paleta, destaques)
        return res
    g = idades_por_grao(dados, tipo, op)
    if unidades:
        g["unidade"] = g["amostra"].astype(str).map(lambda a: unidades.get(a) or a)
    res = Resultado(g)
    if tipo == "wetherill-204":
        nomes = {"nenhuma": N_("sem correção"), "fixo": N_("composição fixa"),
                 "stacey_kramers": N_("Stacey e Kramers (1975)")}
        res.avisos.append(tr("Pb comum corrigido pelo 204Pb: {modelo}").format(modelo=tr(nomes[op["pb_comum"]])))
        tipo = "wetherill"
    disc_ok = np.abs(g["discordancia"].fillna(0)) <= op["limite_discordancia"]

    # os conjuntos existem antes do cálculo, para o pesquisador ligar e desligar cada um
    classe = grupos.classifica(g["discordancia"].fillna(0), np.ones(len(g), bool), op["limite_discordancia"])
    if op["agrupar"] == "populacoes":
        g["grupo"], _cortes = grupos.populacoes(g["melhor"], minimo=op["minimo_por_populacao"])
    elif op["agrupar"] == "manual" and grupo_manual is not None:
        g["grupo"] = grupo_manual
    elif op["agrupar"] == "amostra":
        g["grupo"], _chaves = grupos.chaves_amostras(g.get("unidade", g["amostra"]))
    elif op["agrupar"] == "amostra_populacoes":
        g["grupo"], chaves = grupos.populacoes_por_amostra(g.get("unidade", g["amostra"]), g["melhor"],
                                                            op["minimo_por_populacao"])
    else:
        g["grupo"] = pd.Series(classe, index=g.index).map({"concordante": 1, "discordante": 2})
    if op["agrupar"] == "amostra_populacoes":
        g["conjunto"] = chaves
    else:
        g["conjunto"] = [grupos.chave_conjunto(c, n, op["agrupar"], a)
                         for c, n, a in zip(classe, g["grupo"], g.get("unidade", g["amostra"]))]
    ativo = ~g["conjunto"].isin(desligados.get("conjuntos", [])) & ~g.index.isin(fora_graos)
    g["ativo"] = ativo
    if not ativo.any():
        res.avisos.append(tr("Todos os grãos estão fora do cálculo: ligue algum conjunto ou grão."))

    if op["calcular_por"] == "conjunto":
        chaves = sorted(g.loc[ativo, "conjunto"].unique(), key=grupos.ordem_conjunto)
        partes = [(k, ativo & (g["conjunto"] == k)) for k in chaves]
    else:
        partes = [(None, ativo)]
    valido = np.ones(len(g), bool)
    for k, sel in partes:
        # quando os conjuntos são as próprias classes, o pesquisador já escolheu quais grãos entram
        filtra = k is None or op["agrupar"] != "classe"
        usar = sel & (disc_ok | op["usar_discordantes"]) if filtra else sel
        valido &= _calcula_conjunto(res, g, usar, sel, tipo, op, k)

    g["valido"] = valido
    g["classe"] = grupos.classifica(g["discordancia"].fillna(0), valido, op["limite_discordancia"])
    if op["agrupar"] == "classe":
        g["grupo"] = g["classe"].map({"concordante": 1, "discordante": 2, "rejeitado": 3})
        g["conjunto"] = g["classe"]  # os rejeitados como outliers ganham o estilo deles
    _aplica_estilos(g, op["agrupar"], estilos, so_paleta, destaques)
    return res


def _calcula_conjunto(res, g, usar, todos, tipo, op, chave=None):
    """Média ponderada, idade concórdia e discórdia de um conjunto de grãos (chave None: todos juntos).

    usar: grãos que entram na média e na concórdia; todos: grãos da discórdia. Devolve quais grãos
    não foram rejeitados como outliers."""
    prefixo = "" if chave is None else grupos.nome_conjunto(chave) + ": "
    linhas = []
    valido = np.ones(len(g), bool)
    coluna = {"68": "t68", "76": "t76", "melhor": "melhor"}[op["media_de"]]
    if coluna in g and g[coluna].notna().any():
        x = g[coluna].where(usar).to_numpy(float)
        s = g.get("s_" + coluna, pd.Series(np.nan, index=g.index)).to_numpy(float)
        if not np.isfinite(x).any():
            if usar.sum() < todos.sum():
                res.avisos.append(prefixo + tr("Nenhum grão passou no limite de discordância de {limite} %: média "
                                               "ponderada não calculada. Aumente o limite, marque 'Incluir "
                                               "discordantes' ou use a discórdia."
                                               ).format(limite=num(op["limite_discordancia"], 1)))
        elif np.isfinite(s).any():
            r = estatistica.media_ponderada(x, s, op["efeitos_aleatorios"], op["rejeitar_outliers"])
            valido = r["valido"] | ~np.isfinite(x)
            nome = {"t68": N_("Média ponderada (206Pb/238U)"), "t76": N_("Média ponderada (207Pb/206Pb)"),
                    "melhor": N_("Média ponderada (melhor idade)")}[coluna]
            linhas.append(_linha(nome, r))
            if r["dispersao"]:
                res.avisos.append(prefixo + tr("Dispersão geológica além do erro analítico: {d} Ma").format(
                    d=num(r["dispersao"], 3 if r["dispersao"] < 1 else 2)))
        else:
            res.avisos.append(prefixo + tr("Sem erros por grão: média ponderada não calculada"))

    if tipo in ("wetherill", "tera-wasserburg"):
        sel = usar.to_numpy() & valido
        if sel.sum() >= 2:
            c = estatistica.idade_concordia(g.r75[sel], g.s75[sel], g.r68[sel], g.s68[sel], g.rho[sel])
            linhas.append(_linha(N_("Idade concórdia"), c, "idade"))
            if c["p"] < 0.05:
                res.avisos.append(prefixo + tr("Idade concórdia com p < 0,05: os grãos não são concordantes e "
                                               "equivalentes; prefira a discórdia ou a média ponderada"))
        t = todos.to_numpy()
        if t.sum() >= 3:
            d = estatistica.discordia(g.r75[t], g.s75[t], g.r68[t], g.s68[t], g.rho[t])
            res.discordias.append({"conjunto": chave, **d})
            if "superior" in d:
                linhas.append(_linha(N_("Discórdia: intercepto superior"), d, "superior", "erro_superior"))
            if "inferior" in d:
                linhas.append(_linha(N_("Discórdia: intercepto inferior"), d, "inferior", "erro_inferior"))
    for linha in linhas:
        linha["Conjunto"] = chave
    res.conjunto += linhas
    return valido


def _aplica_estilos(g, agrupar, estilos, so_paleta=False, destaques=None):
    """Cor, símbolo e padrão de cada grão: os da paleta, trocados pelos que o pesquisador escolheu."""
    chaves = list(g["conjunto"]) if "conjunto" in g else \
        [grupos.chave_conjunto(c, n, agrupar) for c, n in zip(g["classe"], g["grupo"])]
    estilos = estilos or {}
    padrao = {k: grupos.estilo_padrao(k) for k in set(chaves)}
    seguras = {c.upper() for c in grupos.cores_seguras()}

    def cor(k):
        c = estilos.get(k, {}).get("cor")
        return c if c and (not so_paleta or c.upper() in seguras) else padrao[k][0]
    g["cor"] = [cor(k) for k in chaves]
    g["simbolo"] = [estilos.get(k, {}).get("simbolo") or padrao[k][1] for k in chaves]
    g["hachura"] = [estilos.get(k, {}).get("hachura", padrao[k][2]) for k in chaves]
    # grãos destacados um a um (núcleo, borda, forma curiosa): por cima do estilo do conjunto
    g["destaque"] = ""
    for linha, e in (destaques or {}).items():
        i = int(linha)
        if i not in g.index:
            continue
        c = e.get("cor")
        if c and (not so_paleta or c.upper() in seguras):
            g.at[i, "cor"] = c
        for campo in ("simbolo", "hachura"):
            if campo in e:
                g.at[i, campo] = e[campo]
        g.at[i, "destaque"] = e.get("rotulo") or str(g.at[i, "analise"])
    # grãos fora do cálculo ficam em cinza e sem padrão, com o símbolo do conjunto
    if "ativo" in g:
        fora = ~g["ativo"].to_numpy(bool)
        g.loc[fora, "cor"] = COR_FORA
        g.loc[fora, "hachura"] = ""
