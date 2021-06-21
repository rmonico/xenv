# Requires: zsh, XENV_ACTIVE_ENVIRONMENT

case "$1" in
    "load")
        # TODO Save previous precmd, if any
        precmd() {
            echo
            echo "XENV: ${XENV_ACTIVE_ENVIRONMENT}"
        }

    ;;

    "unload")
        unset -f precmd
    ;;
esac
