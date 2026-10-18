"""Ligar e desligar conjuntos, calcular cada conjunto à parte e agrupar por amostra (dados inventados)."""
import numpy as np
import pandas as pd
import pytest

from zircon.nucleo import grupos
from zircon.nucleo.calculo import calcular
from zircon.nucleo.constantes import LAMBDA_235, LAMBDA_238


def _grao(t, perda=0.0, erro=0.01):
    """Razões de um grão de idade t (Ma); perda: fração de Pb perdida hoje (desloca para a origem)."""
    r75, r68 = np.expm1(LAMBDA_235 * t) * (1 - perda), np.expm1(LAMBDA_238 * t) * (1 - perda)
    return r75, r75 * erro, r68, r68 * erro * 0.8, 0.6


def _dados():
    """Duas populações concordantes (600 e 1000 Ma) e grãos de 2000 Ma com perda de Pb em duas amostras."""
    linhas = []
    for i, t in enumerate([598, 601, 603, 600, 599]):
        linhas.append(("A", f"A-{i}", *_grao(t)))
    for i, t in enumerate([998, 1001, 1003, 1000]):
        linhas.append(("A", f"B-{i}", *_grao(t)))
    for i, perda in enumerate([0.2, 0.35, 0.5, 0.6]):
        linhas.append(("B", f"C-{i}", *_grao(2000, perda)))
    return pd.DataFrame(linhas, columns=["amostra", "analise", "r75", "s75", "r68", "s68", "rho"])


def _linhas(res, calculo, conjunto=None):
    return [r for r in res.conjunto if r["Cálculo"] == calculo and r.get("Conjunto") == conjunto]


def test_todos_juntos_continua_como_antes():
    res = calcular(_dados(), "wetherill")
    assert all(r["Conjunto"] is None for r in res.conjunto)
    assert res.graos["ativo"].all()
    assert len(res.discordias) == 1


def test_desligar_concordantes_e_calcular_os_discordantes():
    op = {"calcular_por": "conjunto"}
    res = calcular(_dados(), "wetherill", op, desligados={"conjuntos": ["concordante"]})
    g = res.graos
    assert not g.loc[g.analise.str.startswith("A"), "ativo"].any()
    assert {r["Conjunto"] for r in res.conjunto} == {"discordante"}
    sup = _linhas(res, "Discórdia: intercepto superior", "discordante")[0]
    assert sup["Idade (Ma)"] == pytest.approx(2000, abs=5)
    assert sup["n"] == 4
    # grãos fora do cálculo ficam cinza
    assert set(g.loc[~g.ativo, "cor"]) == {"#B0B0B0"}


def test_uma_concordia_por_populacao():
    op = {"calcular_por": "conjunto", "agrupar": "manual"}
    manual = [1] * 5 + [2] * 4 + [3] * 4
    res = calcular(_dados(), "wetherill", op, manual, desligados={"conjuntos": ["g3"]})
    assert _linhas(res, "Idade concórdia", "g1")[0]["Idade (Ma)"] == pytest.approx(600, abs=2)
    assert _linhas(res, "Idade concórdia", "g2")[0]["Idade (Ma)"] == pytest.approx(1000, abs=3)
    assert not _linhas(res, "Idade concórdia", "g3")


def test_agrupar_por_amostra():
    res = calcular(_dados(), "wetherill", {"agrupar": "amostra", "calcular_por": "conjunto"})
    assert set(res.graos.conjunto) == {"a1:A", "a2:B"}
    assert {r["Conjunto"] for r in res.conjunto} == {"a1:A", "a2:B"}


def test_desligar_um_grao():
    d = _dados()
    res = calcular(d, "wetherill", desligados={"graos": ["0"]})
    assert not res.graos.at[0, "ativo"] and res.graos["ativo"].sum() == len(d) - 1
    media = res.medias()[0]
    assert media["n"] == calcular(d, "wetherill").medias()[0]["n"] - 1


def test_populacoes_dentro_de_cada_amostra():
    d = _dados()
    d = d[~d.analise.str.startswith("C")]  # duas populações (600 e 1000 Ma) em cada amostra
    d = pd.concat([d, d.assign(amostra="B")], ignore_index=True)
    op = {"agrupar": "amostra_populacoes", "calcular_por": "conjunto", "minimo_por_populacao": 3}
    res = calcular(d, "wetherill", op)
    nomes = {grupos.nome_conjunto(k) for k in res.graos.conjunto}
    assert "A, população 1" in nomes and "B, população 2" in nomes
    conc = {r["Conjunto"]: r["Idade (Ma)"] for r in res.conjunto if r["Cálculo"] == "Idade concórdia"}
    assert sorted(round(v, -2) for v in conc.values()) == [600, 600, 1000, 1000]


def test_juntar_amostras_numa_unidade():
    d = _dados()
    d = d[~d.analise.str.startswith("C")].copy()
    d["amostra"] = ["P1", "P2", "P3", "P1", "P2"] + ["Q"] * 4  # três amostras da mesma camada e uma outra
    op = {"agrupar": "amostra", "calcular_por": "conjunto"}
    res = calcular(d, "wetherill", op, unidades={"P1": "Camada X", "P2": "Camada X", "P3": "Camada X"})
    assert {grupos.nome_conjunto(k) for k in res.graos.conjunto} == {"Camada X", "Q"}
    conc = {grupos.nome_conjunto(r["Conjunto"]): r for r in res.conjunto if r["Cálculo"] == "Idade concórdia"}
    assert conc["Camada X"]["n"] == 5 and conc["Camada X"]["Idade (Ma)"] == pytest.approx(600, abs=2)
    assert list(res.graos.amostra[:3]) == ["P1", "P2", "P3"]  # as amostras continuam identificadas
