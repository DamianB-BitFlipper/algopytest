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

from .client_ops import (
    account_balance,
    application_global_state,
    application_local_state,
    asset_balance,
    asset_info,
    compile_program,
    suggested_params,
    transaction_info,
)
from .entities import AlgoUser, MultisigAccount, SmartContractAccount
from .transaction_ops import (
    TxnElemsContext,
    TxnIDContext,
    call_app,
    clear_app,
    close_out_app,
    close_out_asset,
    create_app,
    create_asset,
    create_compiled_app,
    delete_app,
    destroy_asset,
    freeze_asset,
    group_transaction,
    multisig_transaction,
    opt_in_app,
    opt_in_asset,
    payment_transaction,
    smart_signature_transaction,
    transfer_asset,
    update_app,
    update_asset,
)

# The functions to expose for sphinx documentation
__all__ = [
    "AlgoUser",
    "SmartContractAccount",
    "MultisigAccount",
    "account_balance",
    "asset_balance",
    "application_global_state",
    "application_local_state",
    "compile_program",
    "suggested_params",
    "create_app",
    "create_compiled_app",
    "delete_app",
    "update_app",
    "opt_in_app",
    "close_out_app",
    "clear_app",
    "call_app",
    "payment_transaction",
    "create_asset",
    "destroy_asset",
    "update_asset",
    "freeze_asset",
    "transfer_asset",
    "opt_in_asset",
    "close_out_asset",
    "smart_signature_transaction",
    "TxnElemsContext",
    "TxnIDContext",
    "group_transaction",
    "multisig_transaction",
    "transaction_info",
]
