"""Lista as frases a traduzir e confere os arquivos de tradução.

Uso: python -m zircon.idiomas.extrair
Procura no código as chamadas tr("..."), N_("..."), F("..."), figura("...")
t("...") e em(idioma, "...") e mostra, para cada idioma, as frases que ainda faltam.
"""
import ast
import json
from pathlib import Path

PASTA = Path(__file__).resolve().parent
FUNCOES = {"tr", "N_", "F", "figura", "t", "em_ingles"}


def frases():
    achadas = []
    for arq in sorted(PASTA.parent.rglob("*.py")):
        for no in ast.walk(ast.parse(arq.read_text(encoding="utf-8"))):
            if not isinstance(no, ast.Call):
                continue
            nome = no.func.id if isinstance(no.func, ast.Name) else getattr(no.func, "attr", "")
            args = no.args[1:] if nome == "em" else no.args  # em(idioma, "frase")
            if (nome in FUNCOES or nome == "em") and args and isinstance(args[0], ast.Constant) \
                    and isinstance(args[0].value, str) and args[0].value not in achadas:
                achadas.append(args[0].value)
    return achadas


def main():
    from . import IDIOMAS
    todas = frases()
    (PASTA / "frases.json").write_text(json.dumps(todas, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(todas)} frases")
    for cod in IDIOMAS:
        if cod == "pt_BR":
            continue
        arq = PASTA / f"{cod}.json"
        tab = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {}
        faltam = [f for f in todas if f not in tab]
        sobram = [f for f in tab if f not in todas]
        print(f"{cod}: faltam {len(faltam)}, sobram {len(sobram)}")


if __name__ == "__main__":
    main()
