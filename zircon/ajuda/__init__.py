"""Guia do Zircon: explica cada recurso.

Cada tópico diz para que serve o recurso e em que casos usar, onde ler mais
(o artigo original, da lista ABNT do programa) e como usar no Zircon. O
texto fica em <idioma>.json nesta pasta; tópico sem tradução aparece em
inglês e, se também faltar, em português do Brasil.
"""
import html
import json
import re
import sys
from pathlib import Path

from .. import idiomas
from ..idiomas import N_, tr

_PASTA = Path(__file__).resolve().parent
if hasattr(sys, "_MEIPASS"):  # programa instalado: textos em <programa>/ajuda
    _PASTA = Path(sys._MEIPASS) / "ajuda"

# Opção do painel -> tópico que a explica
TOPICO_DA_OPCAO = {
    "media_de": "media_ponderada", "corte_76": "melhor_idade", "limite_discordancia": "discordancia",
    "rejeitar_outliers": "outliers", "efeitos_aleatorios": "efeitos_aleatorios", "agrupar": "cores_grupos",
    "pb_comum": "pb_comum", "diagrama": "diagramas", "usar_discordantes": "discordancia",
    "minimo_por_populacao": "populacoes", "paleta": "acessibilidade", "calcular_por": "conjuntos",
}
_cache = {}


def _carrega(cod):
    if cod not in _cache:
        try:
            dados = json.loads((_PASTA / f"{cod}.json").read_text(encoding="utf-8"))
            _cache[cod] = {t["id"]: t for t in dados["topicos"]}
        except (OSError, ValueError, KeyError):
            _cache[cod] = {}
    return _cache[cod]


def topicos():
    """Lista de (id, título) na ordem do guia, no idioma atual."""
    base = _carrega("pt_BR")
    return [(i, obter(i)["titulo"]) for i in base]


def obter(id_):
    for cod in (idiomas.atual(), "en", "pt_BR"):
        t = _carrega(cod).get(id_)
        if t:
            return t
    return None


def _abnt_html(texto):
    texto = html.escape(texto)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto)


def html_do_topico(id_, arquivo_referencias=None):
    t = obter(id_)
    if not t:
        return ""
    from ..nucleo.exportacao import referencias_abnt
    partes = [f"<h2>{html.escape(t['titulo'])}</h2>",
              f"<p><b>{html.escape(tr(N_('Para que serve')))}:</b> {html.escape(t['serve'])}</p>"]
    if t.get("explicacao"):
        partes.append(f"<p>{html.escape(t['explicacao'])}</p>")
    if t.get("referencias"):
        cits = ", ".join(html.escape(r) for r in t["referencias"])
        partes.append(f"<p><b>{html.escape(tr(N_('Para saber mais, consulte')))}:</b> {cits}</p>")
        if arquivo_referencias:
            refs = referencias_abnt(t["referencias"], arquivo_referencias)
            if refs:
                partes.append("<ul>" + "".join(f"<li><small>{_abnt_html(r)}</small></li>" for r in refs) + "</ul>")
    if t.get("como_usar"):
        partes.append(f"<p><b>{html.escape(tr(N_('Como usar no Zircon')))}:</b></p><ol>"
                      + "".join(f"<li>{html.escape(p)}</li>" for p in t["como_usar"]) + "</ol>")
    return "\n".join(partes)


def busca(texto):
    """Ids dos tópicos que contêm o texto (sem diferenciar maiúsculas)."""
    texto = texto.strip().lower()
    achados = []
    for id_, _ in topicos():
        t = obter(id_)
        conteudo = " ".join([t["titulo"], t["serve"], t.get("explicacao", "")] + t.get("como_usar", [])
                            + t.get("referencias", [])).lower()
        if not texto or texto in conteudo:
            achados.append(id_)
    return achados
