function xenv() {
    export XENV_UPDATE="$(mktemp --dry-run --suffix XENV_UPDATE)"

    python -m xenv "$@"

    local ret_code=$?

    [ -f "$XENV_UPDATE" ] && [ "$?" -eq 0 ] && {
        # echo "Updating env with $XENV_UPDATE"
        source "$XENV_UPDATE"

        rm "$XENV_UPDATE"
    }

    unset XENV_UPDATE

    return $ret_code
}

export PS1

if [ -n "$XENV_AUTOLOAD" ]; then
    # TODO Change this flag to autoload and change in plugins
    xenv load "$XENV_AUTOLOAD" -F quick

    unset XENV_AUTOLOAD
fi
