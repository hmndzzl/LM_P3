#!/bin/sh
cd "$(dirname "$0")" || exit 1
exec sh ./abrir_interfaz.sh "$@"
