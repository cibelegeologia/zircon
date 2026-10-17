"""Arquivo de projeto .zircon: um zip com os dados, as opções e o arquivo original.

Cada projeto guarda uma sessão de trabalho com uma planilha, e pode ser
aberto de novo sem internet e sem o arquivo original.
"""
import io
import json
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import pandas as pd

VERSAO_FORMATO = 1
EXTENSAO = ".zircon"


@dataclass
class Projeto:
    nome: str = "Projeto sem título"
    tipo: str = ""
    dados: pd.DataFrame = None
    mapa: dict = field(default_factory=dict)
    log: list = field(default_factory=list)
    opcoes: dict = field(default_factory=dict)
    grupo_manual: list = None
    notas: str = ""
    arquivo_original: str = ""
    bytes_original: bytes = b""
    criado: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    caminho: str = ""

    def salvar(self, caminho):
        caminho = Path(caminho)
        if caminho.suffix != EXTENSAO:
            caminho = caminho.with_suffix(EXTENSAO)
        meta = {
            "versao_formato": VERSAO_FORMATO, "nome": self.nome, "tipo": self.tipo,
            "mapa": self.mapa, "log": self.log, "opcoes": self.opcoes,
            "grupo_manual": self.grupo_manual, "notas": self.notas,
            "arquivo_original": self.arquivo_original, "criado": self.criado,
            "salvo": datetime.now().isoformat(timespec="seconds"),
        }
        with zipfile.ZipFile(caminho, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("projeto.json", json.dumps(meta, ensure_ascii=False, indent=2))
            if self.dados is not None:
                z.writestr("dados.csv", self.dados.to_csv(index=False))
            if self.bytes_original:
                z.writestr("original/" + Path(self.arquivo_original).name, self.bytes_original)
        self.caminho = str(caminho)
        return caminho

    @classmethod
    def abrir(cls, caminho):
        with zipfile.ZipFile(caminho) as z:
            meta = json.loads(z.read("projeto.json"))
            dados = pd.read_csv(io.BytesIO(z.read("dados.csv")), dtype={"amostra": str, "analise": str}) \
                if "dados.csv" in z.namelist() else None
            originais = [n for n in z.namelist() if n.startswith("original/")]
            bruto = z.read(originais[0]) if originais else b""
        p = cls(nome=meta["nome"], tipo=meta["tipo"], dados=dados, mapa=meta["mapa"], log=meta["log"],
                opcoes=meta["opcoes"], grupo_manual=meta.get("grupo_manual"), notas=meta.get("notas", ""),
                arquivo_original=meta.get("arquivo_original", ""), bytes_original=bruto,
                criado=meta.get("criado", ""))
        p.caminho = str(caminho)
        return p
