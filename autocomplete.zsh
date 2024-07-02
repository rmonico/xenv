#compdef xenv

_xenv() {
    case "${words[@]:0:-1}" in
        "xenv")
            local -a commands=(
                'launch-zsh:Print the launch script for ZSH'
                'load:Load a environment'
                'unload:Unload the environment'
                'list:List environments'
                'create:Create a environment'
                'config:Configuration management'
            )

            _describe 'command' commands
            ;;

        "xenv load")
            local environments="$(xenv list --raw)"

            _arguments "2:environments:($environments)"

            # TODO Fazer do jeito abaixo, tem que adaptar o comando list pra devolver a descrição dos ambientes
            # _describe 'environments' ($(xenv list --raw))
            ;;
    esac
}

compdef _xenv xenv
