#!/bin/bash

# Spellchecker docs: https://github.com/myint/scspell
if [ $1 == "interactive" ]; then
    scspell $@ --use-builtin-base-dict --override-dictionary ./.dict --relative-to $(pwd) --report-only
else
    scspell $2 --use-builtin-base-dict --override-dictionary ./.dict --relative-to $(pwd)
fi
