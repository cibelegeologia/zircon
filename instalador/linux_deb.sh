#!/bin/sh
# Monta o pacote .deb (Ubuntu, Debian, Mint) e o .tar.gz a partir de dist/Zircon.
# Uso: sh instalador/linux_deb.sh 0.1.0
set -e
VERSAO="$1"
RAIZ=$(cd "$(dirname "$0")/.." && pwd)
PKG="$RAIZ/build/deb/zircon_${VERSAO}_amd64"
rm -rf "$PKG"
mkdir -p "$PKG/DEBIAN" "$PKG/opt" "$PKG/usr/bin" "$PKG/usr/share/applications" "$PKG/usr/share/mime/packages" \
         "$PKG/usr/share/doc/zircon"
cp -r "$RAIZ/dist/Zircon" "$PKG/opt/zircon"
ln -s /opt/zircon/Zircon "$PKG/usr/bin/zircon"
cp "$RAIZ/instalador/linux/zircon.desktop" "$PKG/usr/share/applications/"
cp "$RAIZ/instalador/linux/zircon-mime.xml" "$PKG/usr/share/mime/packages/zircon.xml"
cp "$RAIZ/instalador/licenca_instalador.txt" "$PKG/usr/share/doc/zircon/copyright"
cp "$RAIZ/docs/referencias_abnt.md" "$PKG/usr/share/doc/zircon/"
TAM=$(du -sk "$PKG" | cut -f1)
sed -e "s/@VERSAO@/$VERSAO/" -e "s/@TAMANHO@/$TAM/" "$RAIZ/instalador/linux/control" > "$PKG/DEBIAN/control"
cp "$RAIZ/instalador/linux/postinst" "$PKG/DEBIAN/postinst"
chmod 755 "$PKG/DEBIAN/postinst"
dpkg-deb --root-owner-group --build "$PKG" "$RAIZ/dist/Zircon-${VERSAO}-linux-amd64.deb"
tar -C "$RAIZ/dist" -czf "$RAIZ/dist/Zircon-${VERSAO}-linux-amd64.tar.gz" Zircon
