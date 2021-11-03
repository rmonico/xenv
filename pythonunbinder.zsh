# vim: filetype=bash

if [[ which initial_command_not_found_handler > /dev/null ]]; then {
    rename_function initial_command_not_found_handler command_not_found_handler
}

unset -f rename_function
unset XENV_COMMANDS

