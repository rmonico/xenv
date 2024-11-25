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

            _describe 'Command' commands
            ;;

        "xenv load")
            local -a environments=()

            local IFS=$'\n'

            for env in $(xenv list --columns name,description | tail -n +2 | sed 's/ \+$//' | sed 's/ \+/:/'); do
              environments+=("$env")
            done

            _describe 'Environment' environments
            ;;
    esac
}

compdef _xenv xenv
