#!/bin/sh
# Copia para dist/Zircon as bibliotecas do X11 (xcb) que o Qt 5 precisa e que
# muitas instalações novas não trazem (Ubuntu 22.04+, Pop!_OS, Mint).
# Sem elas o programa fecha com "could not load the Qt platform plugin xcb".
# Uso: sh instalador/linux_bibliotecas.sh [pasta onde procurar as .so]
set -e
RAIZ=$(cd "$(dirname "$0")/.." && pwd)
DESTINO="$RAIZ/dist/Zircon"
ORIGEM="${1:-}"
for lib in libxcb-icccm.so.4 libxcb-image.so.0 libxcb-util.so.1 libxcb-util.so.0 libxcb-keysyms.so.1 \
           libxcb-render-util.so.0 libxcb-xinerama.so.0 libxcb-xkb.so.1 libxkbcommon-x11.so.0; do
    if [ -n "$ORIGEM" ]; then
        achado=$(find "$ORIGEM" -name "$lib*" | head -1)
    else
        achado=$(ldconfig -p | awk -v l="$lib" '$1 == l && /x86-64/ {print $NF; exit}')
    fi
    if [ -n "$achado" ]; then
        cp -L "$achado" "$DESTINO/$lib"
        echo "incluída: $lib"
    fi
done
# O Debian 10 chama a libxcb-util de .so.0; o Qt do PySide2 procura .so.1 (mesma biblioteca).
if [ ! -f "$DESTINO/libxcb-util.so.1" ] && [ -f "$DESTINO/libxcb-util.so.0" ]; then
    cp "$DESTINO/libxcb-util.so.0" "$DESTINO/libxcb-util.so.1"
    echo "incluída: libxcb-util.so.1 (a partir da .so.0)"
fi
