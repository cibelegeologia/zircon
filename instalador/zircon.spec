# Receita do PyInstaller: gera a pasta dist/Zircon com o Zircon.exe.
# Uso: pyinstaller instalador/zircon.spec
from pathlib import Path

raiz = Path(SPECPATH).parent

a = Analysis(
    [str(raiz / "iniciar_zircon.py")],
    pathex=[str(raiz)],
    datas=[
        (str(raiz / "testes" / "modulo2" / "entrada" / "UPb1.xlsx"), "exemplos"),
        (str(raiz / "testes" / "modulo2" / "entrada" / "UPb2.xlsx"), "exemplos"),
        (str(raiz / "testes" / "modulo2" / "entrada" / "DZ_detritico_so_idades.xlsx"), "exemplos"),
        (str(raiz / "testes" / "modulo2" / "entrada" / "UPb1_estilo_laboratorio_latin1.csv"), "exemplos"),
    ],
    hiddenimports=["odf", "openpyxl", "xlrd"],
    excludes=["tkinter", "IPython", "pytest"],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="Zircon", console=False,
          icon=str(raiz / "instalador" / "zircon.ico") if (raiz / "instalador" / "zircon.ico").exists() else None)
coll = COLLECT(exe, a.binaries, a.datas, name="Zircon")
