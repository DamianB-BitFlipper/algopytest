# The MIT License (MIT)
# Copyright (c) 2022 Damian Barabonkov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

# Important: Update this when making new releases!
# Be sure to update `version` in 'setup.py' as well
__version__ = "1.0.0"
__author__ = "Damian Barabonkov"

from .client_ops import application_global_state, compile_program
from .program_store import initialize
from .transaction_ops import (
    call_app,
    clear_app,
    close_out_app,
    create_app,
    create_custom_app,
    delete_app,
    opt_in_app,
    payment_transaction,
    update_app,
)

# The functions to expose for sphinx documentation
__all__ = [
    "initialize",
    "application_global_state",
    "compile_program",
    "create_app",
    "create_custom_app",
    "delete_app",
    "update_app",
    "opt_in_app",
    "close_out_app",
    "clear_app",
    "call_app",
    "payment_transaction",
]
