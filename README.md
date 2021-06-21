# XENV

A environment manager, as simple it can be. For now its just compatible with zsh.

## Installing

- Clone this repository to `$HOME/.config/xenv` folder
- Add `source $HOME/.config/xenv/xenv_loader` to `.zshrc`

### Testing instalation

- Open a new shell window
- The command `echo $XENV_HOME` should be `<your home>/.config/xenv`


## Creating your first environment

- Create a folder with the name of new environment (lets say `myproject`) with the same contents of `$HOME/.config/env/environments/minimal`

- Export your functions/variables at `$HOME/.config/env/environments/myproject\load`, dont forget to unset them on `unload` script!

- The plugin `python_command_handler` is very useful, but is still in development (like everything here). Look at `teste` environment for instruction to use.

