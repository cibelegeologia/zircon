"""Modelo de planilha e regras de cabeçalho que o Guia ensina (dados inventados)."""
import pandas as pd
import pytest

from zircon.nucleo.calculo import calcular
from zircon.nucleo.importacao import importar
from zircon.nucleo.modelo import salvar_modelo


def test_modelo_e_lido_como_wetherill(tmp_path):
    arq = tmp_path / "modelo.xlsx"
    salvar_modelo(arq)
    imp = importar(arq)
    assert imp.tipo == "wetherill"
    assert len(imp.dados) == 5
    assert {"r75", "s75", "r68", "s68", "rho"} <= set(imp.dados)
    conc = [c for c in calcular(imp.dados, imp.tipo).conjunto if c["Cálculo"] == "Idade concórdia"][0]
    assert conc["Idade (Ma)"] == pytest.approx(600.8, abs=1)


def test_2sigma_com_unidade_e_relativo(tmp_path):
    arq = tmp_path / "rel.xlsx"
    pd.DataFrame({"Amostra": ["A"] * 2, "Análise": ["1", "2"], "207Pb/235U": [0.8, 0.81], "± 2σ (%)": [2, 2],
                  "206Pb/238U": [0.097, 0.098], "± 1σ (%)": [1, 1], "rho": [0.5, 0.5]}).to_excel(arq, index=False)
    d = importar(arq).dados
    assert d.s75[0] == pytest.approx(0.008)
    assert d.s68[0] == pytest.approx(0.00097)
    arq = tmp_path / "idades.xlsx"
    pd.DataFrame({"Amostra": ["A"] * 2, "Análise": ["1", "2"], "Idade (Ma)": [600, 610],
                  "± 2σ (Ma)": [10, 12]}).to_excel(arq, index=False)
    imp = importar(arq)
    assert imp.tipo == "idades"
    assert imp.dados.s_idade.tolist() == [5, 6]


def test_idades_do_laboratorio_a_direita_nao_viram_razao(tmp_path):
    arq = tmp_path / "extras.xlsx"
    pd.DataFrame({"Amostra": ["A"] * 2, "Análise": ["1", "2"], "207Pb/235U": [0.8, 0.81], "± 2σ": [0.02, 0.02],
                  "206Pb/238U": [0.097, 0.098], "± 2σ ": [0.002, 0.002], "rho": [0.5, 0.5],
                  "Idade 207Pb/206Pb (Ma)": [610, 620], "2s": [30, 30]}).to_excel(arq, index=False)
    imp = importar(arq)
    assert "r76" not in imp.mapa and "s76" not in imp.mapa
