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

export PS1

if [ -n "$XENV_AUTOLOAD" ]; then
    xenv load "$XENV_AUTOLOAD"

    unset XENV_AUTOLOAD
fi
