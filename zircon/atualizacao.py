"""Verificar atualizações: o único ponto do Zircon que usa a internet.

Só roda quando a pessoa clica em Ajuda > Verificar atualizações. Faz uma
única pergunta ao GitHub (qual é a versão mais recente publicada) e não envia
nenhum dado do usuário: o pedido leva só o nome "Zircon", sem versão, sistema
ou identificação. Nada é baixado nem instalado; a página de download abre no
navegador para a pessoa decidir.
"""
import json
import platform
import ssl
import sys
import urllib.request

from . import __version__

URL_API = "https://api.github.com/repos/cibelegeologia/zircon/releases/latest"
URL_RELEASES = "https://github.com/cibelegeologia/zircon/releases/latest"


def _contexto_ssl():
    """Certificados para conferir que a resposta vem mesmo do GitHub (nunca desligado)."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def numero(versao):
    """'v0.6.1' -> (0, 6, 1); partes não numéricas viram 0."""
    partes = []
    for p in versao.lstrip("vV").split("-")[0].split("."):
        partes.append(int(p) if p.isdigit() else 0)
    return tuple(partes)


def ultima_versao(tempo_limite=10):
    """Retorna (versão, página da release, novidades). Levanta OSError se não houver conexão."""
    pedido = urllib.request.Request(URL_API, headers={"User-Agent": "Zircon",
                                                      "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(pedido, timeout=tempo_limite, context=_contexto_ssl()) as r:
        dados = json.loads(r.read().decode("utf-8"))
    return dados["tag_name"].lstrip("vV"), dados.get("html_url") or URL_RELEASES, dados.get("body") or ""


def ha_versao_nova(ultima, atual=__version__):
    return numero(ultima) > numero(atual)


def arquivo_do_sistema(versao):
    """Nome do instalador certo para este computador."""
    maquina = platform.machine().lower()
    if sys.platform.startswith("win"):
        arq = "x64" if sys.maxsize > 2 ** 32 else "x86"
        return f"Zircon-{versao}-instalador-windows-{arq}.exe"
    if sys.platform == "darwin":
        arq = "arm64" if maquina in ("arm64", "aarch64") else "x86_64"
        return f"Zircon-{versao}-macos-{arq}.dmg"
    return f"Zircon-{versao}-linux-amd64.deb"
