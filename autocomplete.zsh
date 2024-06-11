_xenv() {
    local -a subcommands=()
    _arguments '1: :(launch-zsh load unload list create config)'

    case "$words[2]" in
        load)
            _arguments "2: :($(xenv list))"
            ;;
    esac
}

compdef _xenv xenv
