if [ -n "$BASH_VERSION" ]; then
    if [ -f "$HOME/.bashrc" ]; then
        . "$HOME/.bashrc"
    fi
fi

# dirty rsync bug workaround https://pastebin.com/5Q6XbQk0
if [ -d "$HOME/bin_" ] ; then
    PATH="$HOME/bin_:$PATH"
fi

export PYTHONPATH="$HOME:$PYTHONPATH"
