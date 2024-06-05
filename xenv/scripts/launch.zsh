function xenv() {
    export XENV_UPDATE="$(mktemp --dry-run --suffix XENV_UPDATE)"

    python -m xenv "$@"

    [ -f "$XENV_UPDATE" ] && [ "$?" -eq 0 ] && {
        # echo "Updating env with $XENV_UPDATE"
        source "$XENV_UPDATE"

        rm "$XENV_UPDATE"
    }

    unset XENV_UPDATE
}
