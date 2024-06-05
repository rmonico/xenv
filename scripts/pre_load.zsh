# ZSH only

unset -f xenv

# before command hook
# TODO Save previous preexec function
preexec() {
    # last param
    local cmd_line="${@[#]}"

    local space_idx=`expr index "$cmd_line" ' '`

    [ $space_idx -eq 0 ] && local space_idx=$((${#cmd_line}+1))

    local cmd=${cmd_line:0:$space_idx-1}

    # echo Binary: .$cmd.
    # echo "$(realpath "$(which "$cmd")")"

    local cmd="$(realpath "$(which "$cmd")" 2> /dev/null)"

    if [ -n "$cmd" ]; then
        [ "$(dirname "$cmd")" = "$XENV_ENVIRONMENT_PATH/bin" ] && export XENV_UPDATE="$(mktemp --dry-run --suffix XENV_UPDATE)"
    fi
}

# ZSH only
# after command hook
# TODO Save previous precmd function
precmd() {
    [ -f "$XENV_UPDATE" ] && {
        # echo "Updating env with $XENV_UPDATE"
        source "$XENV_UPDATE"

        rm "$XENV_UPDATE"

        unset XENV_UPDATE
    }
}
