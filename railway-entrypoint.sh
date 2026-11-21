#!/bin/sh
# Railway gives a service one volume. Mount it at /config and keep the library and the
# ingest folder inside it, linked back to the paths CWA expects.
set -e

# Railway sets PORT; CWA reads CWA_PORT_OVERRIDE (default 8083).
if [ -n "${PORT:-}" ] && [ -z "${CWA_PORT_OVERRIDE:-}" ]; then
  export CWA_PORT_OVERRIDE="$PORT"
fi

mkdir -p /config/calibre-library /config/cwa-book-ingest
for pair in /calibre-library:/config/calibre-library /cwa-book-ingest:/config/cwa-book-ingest; do
  link="${pair%%:*}"
  target="${pair#*:}"
  [ -L "$link" ] && continue
  if mountpoint -q "$link" 2>/dev/null; then
    echo "[railway] $link is a separate mount; leaving it as it is"
    continue
  fi
  if [ -d "$link" ]; then
    cp -an "$link"/. "$target"/ 2>/dev/null || true
    rm -r "$link"
  fi
  ln -s "$target" "$link"
  echo "[railway] $link -> $target"
done

exec /init "$@"
