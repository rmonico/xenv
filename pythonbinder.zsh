# vim: filetype=bash

rename_function command_not_found_handler initial_command_not_found_handler

XENV_COMMANDS=()

command_not_found_handler() {
    # TODO Set this on environment load
    local environment_dir="$XENV_HOME/environments/$XENV_ACTIVE_ENVIRONMENT"

    for command in "$XENV_COMMANDS[@]"
    do
        if [ "$1" == "$command" ]; then
            local source_files_dir="$(mktemp -d)"

            python "${environment_dir}/${command}.py" --source-files-dir "$source_files_dir" "${@:2}"

            local retcode=$?

            for file in $(find "$source_files_dir" -maxdepth 1 -type f); do
               source "$file"
            done

            rm -rf "$source_files_dir" 2> /dev/null

            return $retcode
        fi
    done

    if [[ which initial_command_not_found_handler > /dev/null ]]; then {
        initial_command_not_found_handler "$@"
    }
}

