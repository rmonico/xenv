def load():
    pass

def unload():
    pass

# case "$1" in
#     "load")
#         local _XENV_ENVIRONMENT_FOLDER="$XENV_HOME/environments/${XENV_ACTIVE_ENVIRONMENT}"
#         local _command_handler="${_XENV_ENVIRONMENT_FOLDER}/command_handler.py"
# 
#         [ ! -f "$_command_handler" ] && {
#             echo "python_command_handler: command_handler.py file not found in '$_XENV_ENVIRONMENT_FOLDER', not loading plugin"
#             return 0
#         }
# 
#         export XENV_PYTHON_COMMAND_HANDLER="$_command_handler"
# 
#         # TODO Save old command_not_found_handler, if any
#         command_not_found_handler() {
#             python "$XENV_PYTHON_COMMAND_HANDLER" $@
#         }
#     ;;
# 
#     "unload")
#         unset -f command_not_found_handler &> /dev/null
#     ;;
# esac


