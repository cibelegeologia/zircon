import json

from zircon import atualizacao


def test_compara_versoes():
    assert atualizacao.numero("v0.10.2") == (0, 10, 2)
    assert atualizacao.ha_versao_nova("0.10.0", "0.9.9")
    assert not atualizacao.ha_versao_nova("0.6.1", "0.6.1")
    assert not atualizacao.ha_versao_nova("0.6.0", "0.7.0")


def test_pedido_nao_leva_dados_do_usuario(monkeypatch):
    enviados = []

    class Resposta:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return json.dumps({"tag_name": "v9.0.0", "html_url": "https://github.com/x", "body": "novidades"}).encode()

    def falso_urlopen(pedido, timeout, context):
        enviados.append(pedido)
        return Resposta()

    monkeypatch.setattr(atualizacao.urllib.request, "urlopen", falso_urlopen)
    assert atualizacao.ultima_versao() == ("9.0.0", "https://github.com/x", "novidades")
    pedido = enviados[0]
    assert pedido.full_url == atualizacao.URL_API
    assert pedido.data is None
    assert {k.lower(): v for k, v in pedido.header_items()} == {"user-agent": "Zircon",
                                                                "accept": "application/vnd.github+json"}
