#! /bin/bash

set -e

warn() {
  1>&2 echo "$@"
}

err() {
  warn "$@" && exit 1
}

if [ "$DEV_MODE" = 1 ]; then
  uv --no-progress pip install --system --editable .
  uv --no-progress pip install --system --editable "${SALTBOX_SDK_SRC_PATH}"
fi

cmd_run() {
  cmd=(python3 -m adapter.main)
}

cmd_shell() {
  cmd=("${@:2}")
}

wrong_cmd() {
  warn "Unknown command \"${*}\""
  err "Try \"shell ${*}\" for arbitrary command"
}

case $1 in
  run) cmd_run "$@" ;;
  shell) cmd_shell "$@" ;;
  *) wrong_cmd "$@" ;;
esac

echo "$ ${cmd[*]}"
exec "${cmd[@]}"
