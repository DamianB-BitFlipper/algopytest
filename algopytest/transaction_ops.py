from functools import wraps
from typing import Any, Callable, List, Optional, Tuple, Union

from algosdk import account
from algosdk.future import transaction

from .client_ops import pending_transaction_info, process_transactions, suggested_params
from .entities import AlgoUser, NullUser


def transaction_boilerplate(
    no_log: bool = False,
    no_params: bool = False,
    no_send: bool = False,
    no_sign: bool = False,
    format_finish: Optional[Callable] = None,
    return_fn: Optional[Callable] = None,
) -> Callable:
    """A decorator to handle all of the transaction boilerplate."""

    def decorator(func: Callable) -> Callable:
        """The actual decorator since it takes the arguments above."""

        @wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            # Filter all decorator arguments identified by `__` at the
            # start and remove them from the `kwargs`
            decorator_args = {k: v for k, v in kwargs.items() if k.startswith("__")}
            for decorator_key in decorator_args:
                del kwargs[decorator_key]

            # Pre-process the `decorator_args` and `kwargs` as necessary
            log: Callable[..., None] = print
            if decorator_args.get("__no_log", no_log):
                # Disable logging
                def ignore(*args: Any) -> None:
                    return None

                log = ignore

            # If `params` was not supplied, insert the suggested
            # parameters unless disabled by `no_params`
            if kwargs.get("params", None) is None and not decorator_args.get(
                "__no_params", no_params
            ):
                kwargs["params"] = suggested_params(flat_fee=True, fee=1000)

            log(f"Running {func.__name__}")

            # Create unsigned transaction
            signer, txn = func(*args, **kwargs)

            # Return the `signer` and `txn` if no sending was requested
            if decorator_args.get("__no_send", no_send):
                return signer, txn

            if decorator_args.get("__no_sign", no_sign):
                # Send the `txn` as is
                output_to_send = txn
            else:
                # Sign the `txn`
                output_to_send = txn.sign(signer.private_key)

            # If the `output_to_send` is not a list, wrap it
            # in one as a singular transaction to be sent
            if type(output_to_send) is not list:
                output_to_send = [output_to_send]

            # Send the transaction and await for confirmation
            tx_id = process_transactions(output_to_send)

            # Display results
            transaction_response = pending_transaction_info(tx_id)

            if format_finish is not None:
                log(
                    f"Finished {func.__name__} with: ",
                    format_finish(transaction_response),
                )
            else:
                log(f"Finished {func.__name__}")

            if return_fn is not None:
                return return_fn(transaction_response)
            else:
                return None

        return wrapped

    return decorator


# The return type is `int` modified by `return_fn`
@transaction_boilerplate(
    format_finish=lambda txninfo: f'app-id={txninfo["application-index"]}',
    return_fn=lambda txninfo: txninfo["application-index"],
)
def create_app(
    owner: AlgoUser,
    approval_compiled: bytes,
    clear_compiled: bytes,
    global_schema: transaction.StateSchema,
    local_schema: transaction.StateSchema,
    *,
    params: Optional[transaction.SuggestedParams],
    app_args: Optional[List[Union[str, int]]] = None,
    accounts: Optional[List[str]] = None,
    foreign_apps: Optional[List[int]] = None,
    foreign_assets: Optional[List[int]] = None,
    note: str = "",
    lease: str = "",
    rekey_to: str = "",
    extra_pages: int = 0,
) -> Tuple[AlgoUser, transaction.Transaction]:
    """Deploy a smart contract from the supplied details.

    Parameters
    ----------
    owner
        The user who will be the creator and owner of the smart contract.
    approval_compiled
        The TEAL compiled binary code of the approval program.
    clear_compiled
        The TEAL compiled binary code of the clear program.
    global_schema
        The global state schema details.
    local_schema
        The local state schema details.
    params
        Transaction parameters to use when sending the ``ApplicationCreateTxn`` into the Algorand network.
    app_args
        Any additional arguments to the application.
    accounts
        Any additional accounts to supply to the application.
    foreign_apps
        Any other apps used by the application, identified by app index.
    foreign_assets
        List of assets involved in call.
    note
        A note to attach to the application creation transaction.
    lease
        A unique lease where no other transaction from the same sender and same lease
        can be confirmed during the transactions valid rounds.
    rekey_to
        An Algorand address to rekey the sender to.
    extra_pages
        Provides extra program size.

    Returns
    -------
    int
        The application ID of the deployed smart contract.
    """
    # Materialize all of the optional arguments
    app_args = app_args or []
    accounts = accounts or []
    foreign_apps = foreign_apps or []
    foreign_assets = foreign_assets or []

    # Declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    # Create unsigned transaction
    txn = transaction.ApplicationCreateTxn(
        owner.address,
        params,
        on_complete,
        approval_compiled,
        clear_compiled,
        global_schema,
        local_schema,
        app_args=app_args,
        accounts=accounts,
        foreign_apps=foreign_apps,
        foreign_assets=foreign_assets,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to,
        extra_pages=extra_pages,
    )

    return owner, txn


# Returns `None` because of the `transaction_boilerplate` decorator
@transaction_boilerplate(
    format_finish=lambda txninfo: f'app-id={txninfo["txn"]["txn"]["apid"]}',
)
def delete_app(
    owner: AlgoUser,
    app_id: int,
    *,
    params: Optional[transaction.SuggestedParams],
    app_args: Optional[List[Union[str, int]]] = None,
    accounts: Optional[List[str]] = None,
    foreign_apps: Optional[List[int]] = None,
    foreign_assets: Optional[List[int]] = None,
    note: str = "",
    lease: str = "",
    rekey_to: str = "",
) -> Tuple[AlgoUser, transaction.Transaction]:
    """Delete a deployed smart contract.

    Parameters
    ----------
    owner
        The creator of the smart contract
    app_id
        The application ID of the deployed smart contract.
    params
        Transaction parameters to use when sending the ``ApplicationDeleteTxn`` into the Algorand network.
    app_args
        Any additional arguments to the application.
    accounts
        Any additional accounts to supply to the application.
    foreign_apps
        Any other apps used by the application, identified by app index.
    foreign_assets
        List of assets involved in call.
    note
        A note to attach to the application creation transaction.
    lease
        A unique lease where no other transaction from the same sender and same lease
        can be confirmed during the transactions valid rounds.
    rekey_to
        An Algorand address to rekey the sender to.

    Returns
    -------
    None
    """
    # Materialize all of the optional arguments
    app_args = app_args or []
    accounts = accounts or []
    foreign_apps = foreign_apps or []
    foreign_assets = foreign_assets or []

    txn = transaction.ApplicationDeleteTxn(
        owner.address,
        params,
        app_id,
        app_args=app_args,
        accounts=accounts,
        foreign_apps=foreign_apps,
        foreign_assets=foreign_assets,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to,
    )
    return owner, txn


# Returns `None` because of the `transaction_boilerplate` decorator
@transaction_boilerplate(
    format_finish=lambda txninfo: f'app-id={txninfo["txn"]["txn"]["apid"]}',
)
def update_app(
    owner: AlgoUser,
    app_id: int,
    approval_compiled: bytes,
    clear_compiled: bytes,
    *,
    params: Optional[transaction.SuggestedParams],
    app_args: Optional[List[Union[str, int]]] = None,
    accounts: Optional[List[str]] = None,
    foreign_apps: Optional[List[int]] = None,
    foreign_assets: Optional[List[int]] = None,
    note: str = "",
    lease: str = "",
    rekey_to: str = "",
) -> Tuple[AlgoUser, transaction.Transaction]:
    """Update a deployed smart contract.

    Parameters
    ----------
    owner
        The creator of the smart contract
    app_id
        The application ID of the deployed smart contract.
    approval_compiled
        The TEAL compiled binary code of the approval program.
    clear_compiled
        The TEAL compiled binary code of the clear program.
    params
        Transaction parameters to use when sending the ``ApplicationUpdateTxn`` into the Algorand network.
    app_args
        Any additional arguments to the application.
    accounts
        Any additional accounts to supply to the application.
    foreign_apps
        Any other apps used by the application, identified by app index.
    foreign_assets
        List of assets involved in call.
    note
        A note to attach to the application creation transaction.
    lease
        A unique lease where no other transaction from the same sender and same lease
        can be confirmed during the transactions valid rounds.
    rekey_to
        An Algorand address to rekey the sender to.

    Returns
    -------
    None
    """
    # Materialize all of the optional arguments
    app_args = app_args or []
    accounts = accounts or []
    foreign_apps = foreign_apps or []
    foreign_assets = foreign_assets or []

    txn = transaction.ApplicationUpdateTxn(
        owner.address,
        params,
        app_id,
        approval_compiled,
        clear_compiled,
        app_args=app_args,
        accounts=accounts,
        foreign_apps=foreign_apps,
        foreign_assets=foreign_assets,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to,
    )

    return owner, txn


# Returns `None` because of the `transaction_boilerplate` decorator
@transaction_boilerplate(
    format_finish=lambda txninfo: f'app-id={txninfo["txn"]["txn"]["apid"]}',
)
def opt_in_app(
    sender: AlgoUser,
    app_id: int,
    *,
    params: Optional[transaction.SuggestedParams],
    app_args: Optional[List[Union[str, int]]] = None,
    accounts: Optional[List[str]] = None,
    foreign_apps: Optional[List[int]] = None,
    foreign_assets: Optional[List[int]] = None,
    note: str = "",
    lease: str = "",
    rekey_to: str = "",
) -> Tuple[AlgoUser, transaction.Transaction]:
    """Opt-in to a deployed smart contract.

    Parameters
    ----------
    sender
        The account to opt-in to the smart contract.
    app_id
        The application ID of the deployed smart contract.
    params
        Transaction parameters to use when sending the ``ApplicationOptInTxn`` into the Algorand network.
    app_args
        Any additional arguments to the application.
    accounts
        Any additional accounts to supply to the application.
    foreign_apps
        Any other apps used by the application, identified by app index.
    foreign_assets
        List of assets involved in call.
    note
        A note to attach to the application creation transaction.
    lease
        A unique lease where no other transaction from the same sender and same lease
        can be confirmed during the transactions valid rounds.
    rekey_to
        An Algorand address to rekey the sender to.

    Returns
    -------
    None
    """
    # Materialize all of the optional arguments
    app_args = app_args or []
    accounts = accounts or []
    foreign_apps = foreign_apps or []
    foreign_assets = foreign_assets or []

    txn = transaction.ApplicationOptInTxn(
        sender.address,
        params,
        app_id,
        app_args=app_args,
        accounts=accounts,
        foreign_apps=foreign_apps,
        foreign_assets=foreign_assets,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to,
    )
    return sender, txn


# Returns `None` because of the `transaction_boilerplate` decorator
@transaction_boilerplate(
    format_finish=lambda txninfo: f'app-id={txninfo["txn"]["txn"]["apid"]}',
)
def close_out_app(
    sender: AlgoUser,
    app_id: int,
    *,
    params: Optional[transaction.SuggestedParams],
    app_args: Optional[List[Union[str, int]]] = None,
    accounts: Optional[List[str]] = None,
    foreign_apps: Optional[List[int]] = None,
    foreign_assets: Optional[List[int]] = None,
    note: str = "",
    lease: str = "",
    rekey_to: str = "",
) -> Tuple[AlgoUser, transaction.Transaction]:
    """Close-out from a deployed smart contract.

    Parameters
    ----------
    sender
        The account to close-out from the smart contract.
    app_id
        The application ID of the deployed smart contract.
    params
        Transaction parameters to use when sending the ``ApplicationCloseOutTxn`` into the Algorand network.
    app_args
        Any additional arguments to the application.
    accounts
        Any additional accounts to supply to the application.
    foreign_apps
        Any other apps used by the application, identified by app index.
    foreign_assets
        List of assets involved in call.
    note
        A note to attach to the application creation transaction.
    lease
        A unique lease where no other transaction from the same sender and same lease
        can be confirmed during the transactions valid rounds.
    rekey_to
        An Algorand address to rekey the sender to.

    Returns
    -------
    None
    """
    # Materialize all of the optional arguments
    app_args = app_args or []
    accounts = accounts or []
    foreign_apps = foreign_apps or []
    foreign_assets = foreign_assets or []

    txn = transaction.ApplicationCloseOutTxn(
        sender.address,
        params,
        app_id,
        app_args=app_args,
        accounts=accounts,
        foreign_apps=foreign_apps,
        foreign_assets=foreign_assets,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to,
    )
    return sender, txn


# Returns `None` because of the `transaction_boilerplate` decorator
@transaction_boilerplate(
    format_finish=lambda txninfo: f'app-id={txninfo["txn"]["txn"]["apid"]}',
)
def clear_app(
    sender: AlgoUser,
    app_id: int,
    *,
    params: Optional[transaction.SuggestedParams],
    app_args: Optional[List[Union[str, int]]] = None,
    accounts: Optional[List[str]] = None,
    foreign_apps: Optional[List[int]] = None,
    foreign_assets: Optional[List[int]] = None,
    note: str = "",
    lease: str = "",
    rekey_to: str = "",
) -> Tuple[AlgoUser, transaction.Transaction]:
    """Clear from a deployed smart contract.

    Parameters
    ----------
    sender
        The account to clear from the smart contract.
    app_id
        The application ID of the deployed smart contract.
    params
        Transaction parameters to use when sending the ``ApplicationClearStateTxn`` into the Algorand network.
    app_args
        Any additional arguments to the application.
    accounts
        Any additional accounts to supply to the application.
    foreign_apps
        Any other apps used by the application, identified by app index.
    foreign_assets
        List of assets involved in call.
    note
        A note to attach to the application creation transaction.
    lease
        A unique lease where no other transaction from the same sender and same lease
        can be confirmed during the transactions valid rounds.
    rekey_to
        An Algorand address to rekey the sender to.

    Returns
    -------
    None
    """
    # Materialize all of the optional arguments
    app_args = app_args or []
    accounts = accounts or []
    foreign_apps = foreign_apps or []
    foreign_assets = foreign_assets or []

    txn = transaction.ApplicationClearStateTxn(
        sender.address,
        params,
        app_id,
        app_args=app_args,
        accounts=accounts,
        foreign_apps=foreign_apps,
        foreign_assets=foreign_assets,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to,
    )
    return sender, txn


# Returns `None` because of the `transaction_boilerplate` decorator
@transaction_boilerplate(
    format_finish=lambda txninfo: f'app-id={txninfo["txn"]["txn"]["apid"]}',
)
def call_app(
    sender: AlgoUser,
    app_id: int,
    *,
    params: Optional[transaction.SuggestedParams],
    app_args: Optional[List[Union[str, int]]] = None,
    accounts: Optional[List[str]] = None,
    foreign_apps: Optional[List[int]] = None,
    foreign_assets: Optional[List[int]] = None,
    note: str = "",
    lease: str = "",
    rekey_to: str = "",
) -> Tuple[AlgoUser, transaction.Transaction]:
    """Perform an application call to a deployed smart contract.

    Parameters
    ----------
    sender
        The account to perform the application call to the smart contract.
    app_id
        The application ID of the deployed smart contract.
    params
        Transaction parameters to use when sending the ``ApplicationNoOpTxn`` into the Algorand network.
    app_args
        Any arguments to pass along with the application call.
    accounts
        Any Algorand account addresses to pass along with the application call.
    foreign_apps
        Any other apps used by the application, identified by app index.
    foreign_assets
        List of assets involved in call.
    note
        A note to attach to the application creation transaction.
    lease
        A unique lease where no other transaction from the same sender and same lease
        can be confirmed during the transactions valid rounds.
    rekey_to
        An Algorand address to rekey the sender to.

    Returns
    -------
    None
    """
    # Materialize all of the optional arguments
    app_args = app_args or []
    accounts = accounts or []
    foreign_apps = foreign_apps or []
    foreign_assets = foreign_assets or []

    txn = transaction.ApplicationNoOpTxn(
        sender.address,
        params,
        app_id,
        app_args=app_args,
        accounts=accounts,
        foreign_apps=foreign_apps,
        foreign_assets=foreign_assets,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to,
    )
    return sender, txn


# Returns `None` because of the `transaction_boilerplate` decorator
@transaction_boilerplate()
def payment_transaction(
    sender: AlgoUser,
    receiver: AlgoUser,
    amount: int,
    *,
    params: Optional[transaction.SuggestedParams],
    close_remainder_to: Optional[AlgoUser] = None,
    note: str = "",
    lease: str = "",
    rekey_to: str = "",
) -> Tuple[AlgoUser, transaction.Transaction]:
    """Perform an Algorand payment transaction.

    Parameters
    ----------
    sender
        The account to send the Algorand transaction payment.
    receiver
        The account to receive the Algorand transaction payment
    amount
        The amount of microAlgos (10e-6 Algos) to transact.
    params
        Transaction parameters to use when sending the ``PaymentTxn`` into the Algorand network.
    close_remainder_to
        An Algorand address to close any remainder to.
    note
        A note to attach to the payment transaction.
    lease
        A unique lease where no other transaction from the same sender and same lease
        can be confirmed during the transactions valid rounds.
    rekey_to
        An Algorand address to rekey the sender to.

    Returns
    -------
    None
    """
    # Materialize the `close_remainder_to` to an `AlgoUser`
    close_remainder_to = close_remainder_to or NullUser

    txn = transaction.PaymentTxn(
        sender.address,
        params,
        receiver.address,
        amount,
        close_remainder_to=close_remainder_to.address,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to,
    )
    return sender, txn


@transaction_boilerplate(
    format_finish=lambda txninfo: f'asset-id={txninfo["asset-index"]}',
    return_fn=lambda txninfo: txninfo["asset-index"],
)
def create_asset(
    sender: AlgoUser,
    manager: AlgoUser,
    reserve: AlgoUser,
    freeze: AlgoUser,
    clawback: AlgoUser,
    asset_name: str,
    total: int,
    decimals: int,
    unit_name: str,
    default_frozen: bool,
    *,
    params: Optional[transaction.SuggestedParams],
    url: str = "",
    metadata_hash: str = "",
    note: str = "",
    lease: str = "",
    rekey_to: str = "",
) -> Tuple[AlgoUser, transaction.Transaction]:
    """Create an Algorand asset.

    TODO: write docs!

    Returns
    -------
    None
    """
    txn = transaction.AssetCreateTxn(
        sender.address,
        params,
        total=total,
        decimals=decimals,
        default_frozen=default_frozen,
        manager=manager.address,
        reserve=reserve.address,
        freeze=freeze.address,
        clawback=clawback.address,
        unit_name=unit_name,
        asset_name=asset_name,
        url=url,
        metadata_hash=metadata_hash.encode(),
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to,
    )
    return sender, txn


@transaction_boilerplate(
    format_finish=lambda txninfo: f'asset-id={txninfo["txn"]["txn"]["caid"]}',
)
def destroy_asset(
    sender: AlgoUser,
    asset_id: int,
    *,
    params: Optional[transaction.SuggestedParams],
    note: str = "",
    lease: str = "",
    rekey_to: str = "",
) -> Tuple[AlgoUser, transaction.Transaction]:
    """Destroy an Algorand asset.

    TODO: write docs!

    Returns
    -------
    None
    """
    txn = transaction.AssetDestroyTxn(
        sender.address,
        params,
        index=asset_id,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to,
    )
    return sender, txn


@transaction_boilerplate(
    format_finish=lambda txninfo: f'asset-id={txninfo["txn"]["txn"]["caid"]}',
)
def update_asset(
    sender: AlgoUser,
    asset_id: int,
    *,
    params: Optional[transaction.SuggestedParams],
    manager: Optional[AlgoUser],
    reserve: Optional[AlgoUser],
    freeze: Optional[AlgoUser],
    clawback: Optional[AlgoUser],
    note: str = "",
    lease: str = "",
    rekey_to: str = "",
) -> Tuple[AlgoUser, transaction.Transaction]:
    """Update an Algorand asset.

    TODO: write docs!

    Returns
    -------
    None
    """
    # When an optional account is `None`, it refers to
    # the `NullUser` with an "" empty string address
    manager = manager or NullUser
    reserve = reserve or NullUser
    freeze = freeze or NullUser
    clawback = clawback or NullUser

    txn = transaction.AssetUpdateTxn(
        sender.address,
        params,
        index=asset_id,
        manager=manager.address,
        reserve=reserve.address,
        freeze=freeze.address,
        clawback=clawback.address,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to,
    )
    return sender, txn


@transaction_boilerplate(
    format_finish=lambda txninfo: f'account-addr={txninfo["txn"]["txn"]["fadd"]} asset-id={txninfo["txn"]["txn"]["faid"]}',
)
def freeze_asset(
    sender: AlgoUser,
    target: AlgoUser,
    new_freeze_state: bool,
    asset_id: int,
    *,
    params: Optional[transaction.SuggestedParams],
    note: str = "",
    lease: str = "",
    rekey_to: str = "",
) -> Tuple[AlgoUser, transaction.Transaction]:
    """Freeze the Algorand assets of a target user.

    TODO: write docs!

    Returns
    -------
    None
    """
    txn = transaction.AssetFreezeTxn(
        sender.address,
        params,
        index=asset_id,
        target=target.address,
        new_freeze_state=new_freeze_state,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to,
    )
    return sender, txn


@transaction_boilerplate(
    format_finish=lambda txninfo: f'asset-id={txninfo["txn"]["txn"]["xaid"]}',
)
def transfer_asset(
    sender: AlgoUser,
    receiver: AlgoUser,
    amount: int,
    asset_id: int,
    *,
    params: Optional[transaction.SuggestedParams],
    close_assets_to: Optional[AlgoUser] = None,
    revocation_target: Optional[AlgoUser] = None,
    note: str = "",
    lease: str = "",
    rekey_to: str = "",
) -> Tuple[AlgoUser, transaction.Transaction]:
    """Transfer Algorand assets to a target recipient.

    TODO: write docs!

    Returns
    -------
    None
    """
    # Materialize all of the optional arguments
    close_assets_to = close_assets_to or NullUser
    revocation_target = revocation_target or NullUser

    txn = transaction.AssetTransferTxn(
        sender.address,
        params,
        receiver=receiver.address,
        amt=amount,
        index=asset_id,
        close_assets_to=close_assets_to.address,
        revocation_target=revocation_target.address,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to,
    )
    return sender, txn


@transaction_boilerplate(
    format_finish=lambda txninfo: f'asset-id={txninfo["txn"]["txn"]["xaid"]}',
)
def opt_in_asset(
    sender: AlgoUser,
    asset_id: int,
    *,
    params: Optional[transaction.SuggestedParams],
    note: str = "",
    lease: str = "",
    rekey_to: str = "",
) -> Tuple[AlgoUser, transaction.Transaction]:
    """Opt-in to an Algorand asset.

    TODO: write docs!

    Returns
    -------
    None
    """
    txn = transaction.AssetOptInTxn(
        sender.address,
        params,
        asset_id,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to,
    )
    return sender, txn


@transaction_boilerplate(
    format_finish=lambda txninfo: f'asset-id={txninfo["txn"]["txn"]["xaid"]}',
)
def close_out_asset(
    sender: AlgoUser,
    asset_id: int,
    receiver: AlgoUser,
    *,
    params: Optional[transaction.SuggestedParams],
    note: str = "",
    lease: str = "",
    rekey_to: str = "",
) -> Tuple[AlgoUser, transaction.Transaction]:
    """Opt-in to an Algorand asset.

    TODO: write docs!

    Returns
    -------
    None
    """
    txn = transaction.AssetCloseOutTxn(
        sender.address,
        params,
        receiver.address,
        asset_id,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to,
    )
    return sender, txn


@transaction_boilerplate(
    no_sign=True,
)
def smart_signature_transaction(
    smart_signature: bytes,
    txn: transaction.Transaction,
    *,
    params: Optional[transaction.SuggestedParams],
) -> Tuple[AlgoUser, transaction.Transaction]:
    """Write docs here: TODO!"""
    logic_txn = transaction.LogicSigTransaction(txn, smart_signature)
    return NullUser, logic_txn


def group_elem(txn_factory: Callable) -> Callable:
    def no_send_factory(
        *args: Any, **kwargs: Any
    ) -> Tuple[AlgoUser, transaction.Transaction]:
        # Disable signing and logging within the `txn_factory`
        return txn_factory(*args, __no_send=True, __no_log=True, **kwargs)

    return no_send_factory


class _GroupTxn:
    _InputTxnType = Union[transaction.Transaction, transaction.LogicSigTransaction]
    _SignedTxnType = Union[
        transaction.SignedTransaction, transaction.LogicSigTransaction
    ]

    def __init__(self, transactions: List[Tuple[AlgoUser, _InputTxnType]]):
        # Separate out the `signers` and the `txns`
        self.signers = [signer for signer, _ in transactions]
        self.txns = [txn for _, txn in transactions]

        # Assign the group ID, flattening out `LogicSigTransaction` to get the underlying `Transaction`
        flattened_txns = [
            txn.transaction if isinstance(txn, transaction.LogicSigTransaction) else txn
            for txn in self.txns
        ]
        transaction.assign_group_id(flattened_txns)

    def sign(self, _: str) -> List[_SignedTxnType]:
        # Sign all of the transactions
        signed_txns = []
        for signer, txn in zip(self.signers, self.txns):
            # Logic signature transactions simply get appended since they are already signed
            if isinstance(txn, transaction.LogicSigTransaction):
                signed_txns.append(txn)
            else:
                signed_txns.append(txn.sign(signer.private_key))

        return signed_txns


@transaction_boilerplate(
    no_params=True,
)
def group_transaction(
    *transactions: Tuple[AlgoUser, transaction.Transaction],
) -> Tuple[AlgoUser, _GroupTxn]:
    # The signers are already included as the first elements
    # of the tuples in `transactions`, so return the `NullUser`
    # as the signer of this group transaction
    return NullUser, _GroupTxn(list(transactions))
