"""Leitura de planilhas de laboratório (.xlsx, .xls, .ods, .csv, .txt).

Detecta codificação, separador de colunas, separador decimal, linhas de
título e cabeçalho em várias linhas, e reconhece as colunas pelo nome.
Cada decisão tomada fica registrada em `log` para o usuário conferir.
"""
import csv
import io
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

# Nome interno -> padrões reconhecidos no cabeçalho (sem acento, minúsculo)
COLUNAS = {
    "amostra": [r"^amostra", r"^sample"],
    "analise": [r"^analise", r"^analysis", r"^spot", r"^grao", r"^grain", r"^ponto", r"^id$", r"^nome"],
    "r75": [r"207\s*pb\s*/\s*235\s*u", r"pb\s*207\s*/\s*u\s*235", r"7\s*/\s*35"],
    "r68": [r"206\s*pb\s*/\s*238\s*u", r"pb\s*206\s*/\s*u\s*238", r"6\s*/\s*38"],
    "r86": [r"238\s*u\s*/\s*206\s*pb", r"u\s*238\s*/\s*pb\s*206", r"38\s*/\s*6"],
    "r76": [r"207\s*pb\s*/\s*206\s*pb", r"pb\s*207\s*/\s*pb\s*206", r"7\s*/\s*6"],
    "r48": [r"204\s*pb\s*/\s*238\s*u"],
    "r64": [r"206\s*pb\s*/\s*204\s*pb"],
    "r74": [r"207\s*pb\s*/\s*204\s*pb"],
    "r24": [r"232\s*th\s*/\s*204\s*pb"],
    "r84": [r"208\s*pb\s*/\s*204\s*pb"],
    "rho": [r"^rho", r"^corr", r"^error\s*corr", r"^erro\s*corr"],
}
COLUNAS_IDADE = {
    "t75": [r"207\s*pb\s*/\s*235\s*u", r"7\s*/\s*35"],
    "t68": [r"206\s*pb\s*/\s*238\s*u(?!.*207)", r"6\s*/\s*38"],
    "t76": [r"^.*(?<!ou )207\s*pb\s*/\s*206\s*pb", r"7\s*/\s*6"],
    "tconc": [r"concord"],
    "idade": [r"idade", r"age", r"melhor", r"best"],
}
PADRAO_ERRO = re.compile(r"(^|\W)(erro|err|error|sigma|σ|±|\+/-|1s|2s|se|sd)(\W|$)")
PADRAO_IDADE = re.compile(r"(idade|age)|\(ma\)|\bma\b")
SEM_DADO = re.compile(r"^\s*(<|>|bdl|lod|nd|n\.d\.|na|nan|-+|—)", re.I)


def _normaliza(texto):
    t = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    if "±" in str(texto):
        t = "± " + t
    if "σ" in str(texto):
        t = t + " sigma"
    return re.sub(r"\s+", " ", t.strip().lower())


@dataclass
class Importacao:
    dados: pd.DataFrame
    tipo: str  # wetherill, wetherill-204, tera-wasserburg, pb-pb, th-pb, idades ou desconhecido
    mapa: dict                 # nome interno -> coluna original
    log: list = field(default_factory=list)
    original: pd.DataFrame = None


def _le_texto(caminho, log):
    bruto = Path(caminho).read_bytes()
    for cod in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            texto = bruto.decode(cod)
            break
        except UnicodeDecodeError:
            continue
    log.append(f"Codificação: {cod}")
    linhas = [l for l in texto.splitlines()]
    amostra = "\n".join(l for l in linhas if l.strip())[:20000]
    contagens = {sep: sum(l.count(sep) for l in amostra.splitlines()) for sep in ("\t", ";", ",")}
    if contagens["\t"] > 0:
        sep = "\t"
    elif contagens[";"] > 0:
        sep = ";"
    else:
        sep = ","
    log.append("Separador de colunas: " + {"\t": "tabulação", ";": "ponto e vírgula", ",": "vírgula"}[sep])
    tabela = list(csv.reader(io.StringIO(texto), delimiter=sep))
    largura = max(len(l) for l in tabela)
    tabela = [l + [""] * (largura - len(l)) for l in tabela]
    return pd.DataFrame(tabela, dtype=object), sep


def _le_planilha(caminho, log):
    ext = Path(caminho).suffix.lower()
    motor = {".ods": "odf", ".xls": "xlrd"}.get(ext, "openpyxl")
    df = pd.read_excel(caminho, header=None, dtype=object, engine=motor)
    log.append(f"Planilha lida da primeira aba ({ext})")
    return df


def _e_numero(v, decimal):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return False
    if isinstance(v, (int, float, np.number)):
        return True
    s = str(v).strip()
    if decimal == ",":
        s = s.replace(".", "").replace(",", ".") if re.search(r",\d", s) else s
    try:
        float(s)
        return True
    except ValueError:
        return False


def _detecta_decimal(df, sep):
    texto = " ".join(str(v) for v in df.values.ravel() if isinstance(v, str))
    com_virgula = len(re.findall(r"(?<![\d.])\d+,\d+(?![\d,])", texto))
    com_ponto = len(re.findall(r"(?<![\d,])\d+\.\d+(?![\d.])", texto))
    if sep == "," :
        return "."
    return "," if com_virgula > com_ponto else "."


def _para_numero(v, decimal):
    if v is None:
        return np.nan
    if isinstance(v, (int, float, np.number)):
        return float(v)
    s = str(v).strip()
    if not s or SEM_DADO.match(s):
        return np.nan
    if decimal == ",":
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return np.nan


def _acha_cabecalho(df, decimal, log):
    """Primeira linha de dados = primeira com maioria de células numéricas.

    O cabeçalho é a linha logo acima; linhas acima dela que estejam alinhadas
    às mesmas colunas são juntadas ao nome (cabeçalho em várias linhas).
    """
    numericas = df.apply(lambda l: sum(_e_numero(v, decimal) for v in l), axis=1)
    preenchidas = df.apply(lambda l: sum(str(v).strip() not in ("", "nan", "None") for v in l), axis=1)
    inicio = next(i for i in range(len(df)) if preenchidas[i] > 1 and numericas[i] >= max(2, preenchidas[i] / 2))
    cab = inicio - 1
    nomes = [str(v).strip() if str(v).strip() not in ("nan", "None") else "" for v in df.iloc[cab]]
    acima = cab - 1
    if acima >= 0 and preenchidas[acima] >= 2 and numericas[acima] == 0:
        topo = [str(v).strip() if str(v).strip() not in ("nan", "None") else "" for v in df.iloc[acima]]
        log.append(f"Cabeçalho em duas linhas (linhas {acima + 1} e {cab + 1})")
        acima -= 1
    if acima >= 0:
        log.append(f"Ignoradas {acima + 1} linha(s) de título no topo")
    log.append(f"Dados a partir da linha {inicio + 1}")
    return nomes, inicio


def _casa(nome, padroes):
    return any(re.search(p, nome) for p in padroes)


def _mapeia(nomes, log):
    norm = [_normaliza(n) for n in nomes]
    so_idades = sum(bool(PADRAO_IDADE.search(n)) for n in norm) >= 1 and not any(
        _casa(n, COLUNAS["r68"] + COLUNAS["r86"]) and not PADRAO_IDADE.search(n) for n in norm)
    tabela = COLUNAS_IDADE if so_idades else COLUNAS
    mapa, escala = {}, {}
    ultimo = None
    for i, n in enumerate(norm):
        if not n:
            continue
        if PADRAO_ERRO.search(n) and ultimo is not None and not n.startswith("rho"):
            alvo = "s" + ultimo[1:] if ultimo[0] in "rt" else "s_" + ultimo
            if alvo not in mapa:
                mapa[alvo] = i
                fator_2s = bool(re.search(r"2\s*(s|sigma|se|sd)\b|2σ", n))
                rel = "%" in n
                escala[alvo] = (2.0 if fator_2s else 1.0, rel)
            continue
        achou = None
        for chave in ("amostra", "analise"):
            if chave not in mapa and _casa(n, COLUNAS[chave]):
                achou = chave
        if achou is None:
            for chave, padroes in tabela.items():
                if chave not in mapa and _casa(n, padroes):
                    achou = chave
                    break
        if achou is None and _casa(n, COLUNAS["rho"]):
            sufixo = re.search(r"\b(xz|yz)\b", n)
            achou = "rho_" + sufixo.group(1) if sufixo else ("rho" if "rho" not in mapa else None)
        if achou:
            mapa[achou] = i
            ultimo = achou if achou not in ("amostra", "analise") and not achou.startswith("rho") else None
    for chave, i in mapa.items():
        extra = ""
        if chave in escala:
            f, rel = escala[chave]
            extra = f" ({'2' if f == 2 else '1'}σ, {'%' if rel else 'absoluto'})"
        log.append(f"Coluna '{nomes[i]}' → {chave}{extra}")
    return mapa, escala, so_idades


def importar(caminho):
    """Lê o arquivo e devolve uma Importacao com colunas padronizadas."""
    log = []
    ext = Path(caminho).suffix.lower()
    if ext in (".csv", ".txt", ".tsv", ".dat"):
        bruto, sep = _le_texto(caminho, log)
    else:
        bruto, sep = _le_planilha(caminho, log), None
    decimal = _detecta_decimal(bruto, sep or ";")
    log.append("Separador decimal: " + ("vírgula" if decimal == "," else "ponto"))
    nomes, inicio = _acha_cabecalho(bruto, decimal, log)
    corpo = bruto.iloc[inicio:].reset_index(drop=True)
    corpo = corpo[corpo.apply(lambda l: any(str(v).strip() not in ("", "nan", "None") for v in l), axis=1)]
    original = corpo.copy()
    original.columns = [n or f"coluna {i + 1}" for i, n in enumerate(nomes)]
    mapa, escala, so_idades = _mapeia(nomes, log)

    dados = pd.DataFrame(index=corpo.index)
    for chave, i in mapa.items():
        col = corpo.iloc[:, i]
        if chave in ("amostra", "analise"):
            dados[chave] = col.astype(str).str.strip()
        else:
            dados[chave] = [_para_numero(v, decimal) for v in col]
    for alvo, (fator, rel) in escala.items():
        base = "r" + alvo[1:] if not so_idades else "t" + alvo[1:]
        if alvo == "s_idade":
            base = "idade"
        v = dados[alvo] / fator
        if rel and base in dados:
            v = v / 100 * dados[base].abs()
        dados[alvo] = v
    if "analise" not in dados:
        dados["analise"] = [str(i + 1) for i in range(len(dados))]
    if "amostra" not in dados:
        dados["amostra"] = Path(caminho).stem
        log.append("Sem coluna de amostra: usado o nome do arquivo")

    if so_idades:
        tipo = "idades"
    elif {"r75", "r68", "r48"} <= set(dados):
        tipo = "wetherill-204"
    elif {"r64", "r74"} <= set(dados):
        tipo = "pb-pb"
    elif {"r24", "r84"} <= set(dados):
        tipo = "th-pb"
    elif {"r75", "r68"} <= set(dados):
        tipo = "wetherill"
    elif {"r86", "r76"} <= set(dados):
        tipo = "tera-wasserburg"
    else:
        tipo = "desconhecido"
        log.append("Atenção: não reconheci razões U-Pb nem idades; confira o mapeamento")
    if tipo != "idades" and tipo != "desconhecido" and "rho" not in dados:
        dados["rho"] = 0.0
        log.append("Atenção: sem coluna de correlação (rho); usado rho = 0")
    log.append(f"Tipo de dado: {tipo}; {len(dados)} análises")
    return Importacao(dados.reset_index(drop=True), tipo, {k: nomes[i] for k, i in mapa.items()}, log,
                      original.reset_index(drop=True))
