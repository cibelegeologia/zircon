"""Camada de compatibilidade Qt.

Usa PySide6 (Qt 6) quando existe e PySide2 (Qt 5) na montagem compatível
com sistemas antigos (Windows 7, macOS 10.13, Linux de 2014).
"""
import os

try:
    from PySide6.QtCore import *  # noqa: F401,F403
    from PySide6.QtGui import *  # noqa: F401,F403
    from PySide6.QtWidgets import *  # noqa: F401,F403
    QT_API = "pyside6"
except ImportError:
    from PySide2.QtCore import *  # noqa: F401,F403
    from PySide2.QtGui import *  # noqa: F401,F403
    from PySide2.QtWidgets import *  # noqa: F401,F403
    from PySide2.QtWidgets import QAction, QApplication, QDialog, QMenu, QMessageBox  # noqa: F401
    QT_API = "pyside2"
    # Qt 5 chama exec_(); o resto do código usa exec(), como no Qt 6
    for _classe in (QApplication, QDialog, QMenu, QMessageBox):
        if not hasattr(_classe, "exec"):
            _classe.exec = _classe.exec_
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

os.environ.setdefault("QT_API", QT_API)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT  # noqa: E402,F401
