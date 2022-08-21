#!/bin/bash

# Spellchecker docs: https://github.com/myint/scspell
scspell $@ --use-builtin-base-dict --override-dictionary ./algopytest/.dict --relative-to $(pwd) --report-only
