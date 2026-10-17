"""Confere os cálculos contra os resultados de referência do IsoplotR 7.1."""
from pathlib import Path

import pandas as pd
import pytest

from zircon.nucleo import estatistica, idades
from zircon.nucleo.calculo import calcular
from zircon.nucleo.importacao import importar
from zircon.nucleo.projeto import Projeto

PASTA = Path(__file__).resolve().parents[1] / "modulo2"
ENTRADA = PASTA / "entrada"
REF = pd.read_csv(PASTA / "referencia" / "resultados_referencia_IsoplotR.csv")


def ref(conjunto, calculo, opcoes):
    linha = REF[(REF.conjunto == conjunto) & (REF.calculo == calculo) & REF.opcoes.str.startswith(opcoes)].iloc[0]
    return linha.valor_Ma, linha.erro_1s_Ma, linha.MSWD


def wetherill(nome):
    imp = importar(ENTRADA / nome)
    d = imp.dados
    if imp.tipo == "tera-wasserburg":
        return idades.tw_para_wetherill(d.r86, d.s86, d.r76, d.s76, d.rho)
    return d.r75, d.s75, d.r68, d.s68, d.rho


def perto(a, b, rel=2e-4):
    return a == pytest.approx(b, rel=rel)


@pytest.mark.parametrize("conjunto", ["UPb1", "UPb2"])
def test_concordia_e_discordia(conjunto):
    dados = wetherill(f"{conjunto}_virgula-ponto.csv")
    c = estatistica.idade_concordia(*dados)
    t, s, m = ref(conjunto, "Idade concórdia (Ludwig 1998)", "sem")
    assert perto(c["idade"], t) and perto(c["erro"], s, 1e-3) and perto(c["mswd"], m, 1e-3)
    d = estatistica.discordia(*dados)
    t, s, m = ref(conjunto, "Discórdia: intercepto superior", "modelo")
    assert perto(d["superior"], t) and perto(d["erro_superior"], s, 2e-3) and perto(d["mswd"], m, 1e-3)
    t, s, _ = ref(conjunto, "Discórdia: intercepto inferior", "modelo")
    assert d["inferior"] == pytest.approx(t, abs=0.01) and perto(d["erro_inferior"], s, 2e-3)


@pytest.mark.parametrize("conjunto", ["UPb1", "UPb2"])
@pytest.mark.parametrize("razao", ["206Pb/238U", "207Pb/206Pb"])
@pytest.mark.parametrize("opcoes", ["sem outliers", "Chauvenet"])
def test_media_ponderada(conjunto, razao, opcoes):
    r75, s75, r68, s68, rho = wetherill(f"{conjunto}_virgula-ponto.csv")
    if razao == "206Pb/238U":
        t, st = idades.idade_68(r68, s68)
    else:
        _, _, r76, s76, _ = idades.wetherill_para_tw(r75, s75, r68, s68, rho)
        t, st = idades.idade_76(r76, s76)
    completo = opcoes == "Chauvenet"
    r = estatistica.media_ponderada(t, st, completo, completo)
    v, s, m = ref(conjunto, f"Média ponderada {razao}", opcoes)
    assert perto(r["media"], v, 1e-5) and perto(r["erro"], s, 1e-3) and perto(r["mswd"], m, 1e-3)


@pytest.mark.parametrize("arquivo", sorted(p.name for p in ENTRADA.glob("UPb1*")))
def test_importacao_upb1_em_todos_os_formatos(arquivo):
    imp = importar(ENTRADA / arquivo)
    res = calcular(imp.dados, imp.tipo)
    media = res.conjunto[0]
    assert len(imp.dados) == 10
    assert perto(media["Idade (Ma)"], 251.26454, 1e-5)


def test_projeto_salva_e_abre(tmp_path):
    imp = importar(ENTRADA / "UPb1_pontoevirgula-virgula.csv")
    p = Projeto(nome="teste", tipo=imp.tipo, dados=imp.dados, log=imp.log, opcoes={"corte_76": 900.0},
                arquivo_original="UPb1.csv", bytes_original=b"abc")
    caminho = p.salvar(tmp_path / "teste")
    q = Projeto.abrir(caminho)
    assert q.tipo == "wetherill" and q.opcoes["corte_76"] == 900.0 and q.bytes_original == b"abc"
    pd.testing.assert_frame_equal(q.dados, imp.dados, check_dtype=False)


def test_populacoes_detriticas():
    imp = importar(ENTRADA / "DZ_detritico_so_idades.xlsx")
    d = imp.dados[imp.dados.amostra == "N1"].reset_index(drop=True)
    res = calcular(d, imp.tipo, {"agrupar": "populacoes"})
    assert res.graos.grupo.nunique() >= 2
    assert res.graos.melhor.min() == pytest.approx(128.9)
