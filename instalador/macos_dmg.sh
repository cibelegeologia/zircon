#!/bin/sh
# Monta o .dmg (arrastar para Aplicativos) a partir de dist/Zircon.app.
# Uso: sh instalador/macos_dmg.sh 0.1.0
set -e
VERSAO="$1"
RAIZ=$(cd "$(dirname "$0")/.." && pwd)
PASTA="$RAIZ/build/dmg"
rm -rf "$PASTA"
mkdir -p "$PASTA"
cp -R "$RAIZ/dist/Zircon.app" "$PASTA/"
ln -s /Applications "$PASTA/Aplicativos"
cp "$RAIZ/instalador/licenca_instalador.txt" "$PASTA/Leia-me.txt"
ARQ=$(uname -m)
hdiutil create -volname "Zircon $VERSAO" -srcfolder "$PASTA" -ov -format UDZO \
  "$RAIZ/dist/Zircon-${VERSAO}-macos-${ARQ}.dmg"
