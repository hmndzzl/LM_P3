#!/bin/sh
# Resuelve la raíz para poder iniciarlo desde cualquier directorio.
cd "$(dirname "$0")/.." || exit 1
exec python3 -B -m lm_p3 "$@"
