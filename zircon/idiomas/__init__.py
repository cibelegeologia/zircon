"""Idiomas do programa e das exportações.

O texto-fonte é o português do Brasil: cada frase do código passa por tr()
e é trocada pela tradução do arquivo <código>.json desta pasta. Frase sem
tradução aparece em português, então nada some se faltar uma tradução.
"""
import json
from pathlib import Path

IDIOMAS = {
    "pt_BR": "Português (Brasil)",
    "pt_PT": "Português (Portugal)",
    "es": "Español",
    "en": "English",
    "fr": "Français",
    "de": "Deutsch",
    "zh": "中文（简体）",
    "hi": "हिन्दी",
    "ar": "العربية",
}
# Idiomas em que a vírgula é o separador decimal
_DECIMAL_VIRGULA = {"pt_BR", "pt_PT", "es", "fr", "de"}
# O matplotlib não monta corretamente a escrita do hindi e do árabe (letras
# ligadas e direção); nos gráficos em imagem esses idiomas usam inglês.
_FIGURA_EM_INGLES = {"hi", "ar"}

_PASTA = Path(__file__).resolve().parent
_atual = "pt_BR"
_tabela = {}
_tabela_en = {}


def _carrega(cod):
    if cod == "pt_BR":
        return {}
    try:
        return json.loads((_PASTA / f"{cod}.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def definir(cod):
    """Troca o idioma atual. Código desconhecido volta ao português do Brasil."""
    global _atual, _tabela, _tabela_en
    _atual = cod if cod in IDIOMAS else "pt_BR"
    _tabela = _carrega(_atual)
    if not _tabela_en:
        _tabela_en = _carrega("en")


def atual():
    return _atual


def tr(texto):
    """Tradução da frase no idioma atual."""
    return _tabela.get(texto) or texto


def em_ingles(texto):
    return _tabela_en.get(texto) or texto


def em(cod, texto):
    """Tradução da frase num idioma escolhido, sem mudar o idioma atual."""
    if cod == _atual:
        return tr(texto)
    if cod == "en":
        return em_ingles(texto)
    return _carrega(cod).get(texto) or texto


def N_(texto):
    """Marca a frase para tradução sem traduzir agora (usada em constantes)."""
    return texto


def figura(texto):
    """Tradução para gráficos em imagem (inglês no hindi e no árabe)."""
    return em_ingles(texto) if _atual in _FIGURA_EM_INGLES else tr(texto)


def figura_em_ingles():
    return _atual in _FIGURA_EM_INGLES


def decimal():
    return "," if _atual in _DECIMAL_VIRGULA else "."


def num(v, casas=2):
    """Número formatado com o separador decimal do idioma."""
    s = f"{v:.{casas}f}"
    return s.replace(".", ",") if decimal() == "," else s


def direita_para_esquerda():
    return _atual == "ar"


def codigo_do_sistema(nome_qt):
    """Escolhe o idioma pelo do sistema (ex.: 'pt_PT', 'es_AR', 'zh_CN')."""
    if nome_qt in IDIOMAS:
        return nome_qt
    base = nome_qt.split("_")[0]
    if base == "pt":
        return "pt_BR"
    return base if base in IDIOMAS else "en"
