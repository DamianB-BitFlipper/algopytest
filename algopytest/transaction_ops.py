import logging
from functools import wraps
from types import TracebackType
from typing import Any, Callable, List, Optional, Tuple, Union

from algosdk.future import transaction as algosdk_transaction

from .client_ops import pending_transaction_info, process_transactions, suggested_params
from .entities import AlgoUser, MultisigAccount, _NullUser
from .type_stubs import P, TransactionT

# Global variable switches controlled by context managers for the `transaction_boilerplate` decorator
_no_log: Optional[bool] = None
_no_params: Optional[bool] = None
_no_send: Optional[bool] = None
_no_sign: Optional[bool] = None
_with_txn_id: Optional[bool] = None


class TxnElemsContext:
    def __enter__(self) -> None:
        global _no_send, _no_log

        # Globally disable sending and logging
        _no_send = True
        _no_log = True

    def __exit__(
        self,
        etype: Optional[type[BaseException]],
        evalue: Optional[BaseException],
        etraceback: Optional[TracebackType],
    ) -> None:
        global _no_send, _no_log

        # Disable any global modifiers
        _no_send = None
        _no_log = None


class TxnIDContext:
    def __enter__(self) -> None:
        global _with_txn_id

        # Globally enable `_with_txn_id`
        _with_txn_id = True

    def __exit__(
        self,
        etype: Optional[type[BaseException]],
        evalue: Optional[BaseException],
        etraceback: Optional[TracebackType],
    ) -> None:
        global _with_txn_id

        # Disable any global modifiers
        _with_txn_id = None


def transaction_boilerplate(
    no_log: bool = False,
    no_params: bool = False,
    no_send: bool = False,
    no_sign: bool = False,
    with_txn_id: bool = False,
    format_finish: Optional[Callable] = None,
    return_fn: Optional[Callable] = None,
) -> Callable[[Callable[P, Tuple[AlgoUser, TransactionT]]], Callable[P, Any]]:
    """A decorator to handle all of the transaction boilerplate."""

    def decorator(func: Callable[P, Tuple[AlgoUser, TransactionT]]) -> Callable[P, Any]:
        """The actual decorator since it takes the arguments above."""

        @wraps(func)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> Any:
            # Apply the global modifiers if any are set
            f_no_log = no_log if _no_log is None else _no_log
            f_no_params = no_params if _no_params is None else _no_params
            f_no_send = no_send if _no_send is None else _no_send
            f_no_sign = no_sign if _no_sign is None else _no_sign
            f_with_txn_id = with_txn_id if _with_txn_id is None else _with_txn_id

            logger = logging.getLogger("algopytest")
            logger.setLevel(logging.INFO)

            log: Callable[..., None] = logger.info
            if f_no_log:
                # Disable logging
                def ignore(*args: Any) -> None:
                    return None

                log = ignore

            # If `params` was not supplied, insert the suggested
            # parameters unless disabled by `no_params`
            if kwargs.get("params") is None and not f_no_params:
                kwargs["params"] = suggested_params(flat_fee=True, fee=1000)

            log(f"Running {func.__name__}")

            # Create unsigned transaction
            signer, txn = func(*args, **kwargs)

            # Return the `signer` and `txn` if no sending was requested
            if f_no_send:
                return signer, txn

            if f_no_sign:
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
            txn_id = process_transactions(output_to_send)

            # Display results
            transaction_response = pending_transaction_info(txn_id)

            if format_finish is not None:
                log(
                    f"Finished {func.__name__} with: {format_finish(transaction_response)}"
                )
            else:
                log(f"Finished {func.__name__}")

            ret = return_fn(transaction_response) if return_fn is not None else None

            # Return the `txn_id` if requested
            if f_with_txn_id:
                return txn_id, ret
            else:
                return ret

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
    global_schema: algosdk_transaction.StateSchema,
    local_schema: algosdk_transaction.StateSchema,
    *,
    params: Optional[algosdk_transaction.SuggestedParams] = None,
    app_args: Optional[List[Union[str, int]]] = None,
    accounts: Optional[List[AlgoUser]] = None,
    foreign_apps: Optional[List[int]] = None,
    foreign_assets: Optional[List[int]] = None,
    note: str = "",
    lease: str = "",
    rekey_to: Optional[AlgoUser] = None,
    extra_pages: int = 0,
) -> Tuple[AlgoUser, algosdk_transaction.Transaction]:
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
    rekey_to = rekey_to or _NullUser

    # Declare on_complete as NoOp
    on_complete = algosdk_transaction.OnComplete.NoOpOC.real

    # Create unsigned transaction
    txn = algosdk_transaction.ApplicationCreateTxn(
        owner.address,
        params,
        on_complete,
        approval_compiled,
        clear_compiled,
        global_schema,
        local_schema,
        app_args=app_args,
        accounts=[account.address for account in accounts],
        foreign_apps=foreign_apps,
        foreign_assets=foreign_assets,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to.address,
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
    params: Optional[algosdk_transaction.SuggestedParams] = None,
    app_args: Optional[List[Union[str, int]]] = None,
    accounts: Optional[List[AlgoUser]] = None,
    foreign_apps: Optional[List[int]] = None,
    foreign_assets: Optional[List[int]] = None,
    note: str = "",
    lease: str = "",
    rekey_to: Optional[AlgoUser] = None,
) -> Tuple[AlgoUser, algosdk_transaction.Transaction]:
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
    rekey_to = rekey_to or _NullUser

    txn = algosdk_transaction.ApplicationDeleteTxn(
        owner.address,
        params,
        app_id,
        app_args=app_args,
        accounts=[account.address for account in accounts],
        foreign_apps=foreign_apps,
        foreign_assets=foreign_assets,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to.address,
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
    params: Optional[algosdk_transaction.SuggestedParams] = None,
    app_args: Optional[List[Union[str, int]]] = None,
    accounts: Optional[List[AlgoUser]] = None,
    foreign_apps: Optional[List[int]] = None,
    foreign_assets: Optional[List[int]] = None,
    note: str = "",
    lease: str = "",
    rekey_to: Optional[AlgoUser] = None,
) -> Tuple[AlgoUser, algosdk_transaction.Transaction]:
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
    rekey_to = rekey_to or _NullUser

    txn = algosdk_transaction.ApplicationUpdateTxn(
        owner.address,
        params,
        app_id,
        approval_compiled,
        clear_compiled,
        app_args=app_args,
        accounts=[account.address for account in accounts],
        foreign_apps=foreign_apps,
        foreign_assets=foreign_assets,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to.address,
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
    params: Optional[algosdk_transaction.SuggestedParams] = None,
    app_args: Optional[List[Union[str, int]]] = None,
    accounts: Optional[List[AlgoUser]] = None,
    foreign_apps: Optional[List[int]] = None,
    foreign_assets: Optional[List[int]] = None,
    note: str = "",
    lease: str = "",
    rekey_to: Optional[AlgoUser] = None,
) -> Tuple[AlgoUser, algosdk_transaction.Transaction]:
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
    rekey_to = rekey_to or _NullUser

    txn = algosdk_transaction.ApplicationOptInTxn(
        sender.address,
        params,
        app_id,
        app_args=app_args,
        accounts=[account.address for account in accounts],
        foreign_apps=foreign_apps,
        foreign_assets=foreign_assets,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to.address,
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
    params: Optional[algosdk_transaction.SuggestedParams] = None,
    app_args: Optional[List[Union[str, int]]] = None,
    accounts: Optional[List[AlgoUser]] = None,
    foreign_apps: Optional[List[int]] = None,
    foreign_assets: Optional[List[int]] = None,
    note: str = "",
    lease: str = "",
    rekey_to: Optional[AlgoUser] = None,
) -> Tuple[AlgoUser, algosdk_transaction.Transaction]:
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
    rekey_to = rekey_to or _NullUser

    txn = algosdk_transaction.ApplicationCloseOutTxn(
        sender.address,
        params,
        app_id,
        app_args=app_args,
        accounts=[account.address for account in accounts],
        foreign_apps=foreign_apps,
        foreign_assets=foreign_assets,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to.address,
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
    params: Optional[algosdk_transaction.SuggestedParams] = None,
    app_args: Optional[List[Union[str, int]]] = None,
    accounts: Optional[List[AlgoUser]] = None,
    foreign_apps: Optional[List[int]] = None,
    foreign_assets: Optional[List[int]] = None,
    note: str = "",
    lease: str = "",
    rekey_to: Optional[AlgoUser] = None,
) -> Tuple[AlgoUser, algosdk_transaction.Transaction]:
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
    rekey_to = rekey_to or _NullUser

    txn = algosdk_transaction.ApplicationClearStateTxn(
        sender.address,
        params,
        app_id,
        app_args=app_args,
        accounts=[account.address for account in accounts],
        foreign_apps=foreign_apps,
        foreign_assets=foreign_assets,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to.address,
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
    params: Optional[algosdk_transaction.SuggestedParams] = None,
    app_args: Optional[List[Union[str, int]]] = None,
    accounts: Optional[List[AlgoUser]] = None,
    foreign_apps: Optional[List[int]] = None,
    foreign_assets: Optional[List[int]] = None,
    note: str = "",
    lease: str = "",
    rekey_to: Optional[AlgoUser] = None,
) -> Tuple[AlgoUser, algosdk_transaction.Transaction]:
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
    rekey_to = rekey_to or _NullUser

    txn = algosdk_transaction.ApplicationNoOpTxn(
        sender.address,
        params,
        app_id,
        app_args=app_args,
        accounts=[account.address for account in accounts],
        foreign_apps=foreign_apps,
        foreign_assets=foreign_assets,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to.address,
    )
    return sender, txn


# Returns `None` because of the `transaction_boilerplate` decorator
@transaction_boilerplate()
def payment_transaction(
    sender: AlgoUser,
    receiver: AlgoUser,
    amount: int,
    *,
    params: Optional[algosdk_transaction.SuggestedParams] = None,
    close_remainder_to: Optional[AlgoUser] = None,
    note: str = "",
    lease: str = "",
    rekey_to: Optional[AlgoUser] = None,
) -> Tuple[AlgoUser, algosdk_transaction.Transaction]:
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
    # Materialize all of the optional arguments
    close_remainder_to = close_remainder_to or _NullUser
    rekey_to = rekey_to or _NullUser

    txn = algosdk_transaction.PaymentTxn(
        sender.address,
        params,
        receiver.address,
        amount,
        close_remainder_to=close_remainder_to.address,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to.address,
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
    params: Optional[algosdk_transaction.SuggestedParams] = None,
    url: str = "",
    metadata_hash: str = "",
    note: str = "",
    lease: str = "",
    rekey_to: Optional[AlgoUser] = None,
) -> Tuple[AlgoUser, algosdk_transaction.Transaction]:
    """Create an Algorand asset.

    TODO: write docs!

    Returns
    -------
    None
    """
    # Materialize all of the optional arguments
    rekey_to = rekey_to or _NullUser

    txn = algosdk_transaction.AssetCreateTxn(
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
        rekey_to=rekey_to.address,
    )
    return sender, txn


@transaction_boilerplate(
    format_finish=lambda txninfo: f'asset-id={txninfo["txn"]["txn"]["caid"]}',
)
def destroy_asset(
    sender: AlgoUser,
    asset_id: int,
    *,
    params: Optional[algosdk_transaction.SuggestedParams] = None,
    note: str = "",
    lease: str = "",
    rekey_to: Optional[AlgoUser] = None,
) -> Tuple[AlgoUser, algosdk_transaction.Transaction]:
    """Destroy an Algorand asset.

    TODO: write docs!

    Returns
    -------
    None
    """
    # Materialize all of the optional arguments
    rekey_to = rekey_to or _NullUser

    txn = algosdk_transaction.AssetDestroyTxn(
        sender.address,
        params,
        index=asset_id,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to.address,
    )
    return sender, txn


@transaction_boilerplate(
    format_finish=lambda txninfo: f'asset-id={txninfo["txn"]["txn"]["caid"]}',
)
def update_asset(
    sender: AlgoUser,
    asset_id: int,
    *,
    manager: Optional[AlgoUser],
    reserve: Optional[AlgoUser],
    freeze: Optional[AlgoUser],
    clawback: Optional[AlgoUser],
    params: Optional[algosdk_transaction.SuggestedParams] = None,
    note: str = "",
    lease: str = "",
    rekey_to: Optional[AlgoUser] = None,
) -> Tuple[AlgoUser, algosdk_transaction.Transaction]:
    """Update an Algorand asset.

    TODO: write docs!

    Returns
    -------
    None
    """
    # When an optional account is `None`, it refers to
    # the `_NullUser` with an "" empty string address
    manager = manager or _NullUser
    reserve = reserve or _NullUser
    freeze = freeze or _NullUser
    clawback = clawback or _NullUser
    rekey_to = rekey_to or _NullUser

    txn = algosdk_transaction.AssetUpdateTxn(
        sender.address,
        params,
        index=asset_id,
        manager=manager.address,
        reserve=reserve.address,
        freeze=freeze.address,
        clawback=clawback.address,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to.address,
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
    params: Optional[algosdk_transaction.SuggestedParams] = None,
    note: str = "",
    lease: str = "",
    rekey_to: Optional[AlgoUser] = None,
) -> Tuple[AlgoUser, algosdk_transaction.Transaction]:
    """Freeze the Algorand assets of a target user.

    TODO: write docs!

    Returns
    -------
    None
    """
    # Materialize all of the optional arguments
    rekey_to = rekey_to or _NullUser

    txn = algosdk_transaction.AssetFreezeTxn(
        sender.address,
        params,
        index=asset_id,
        target=target.address,
        new_freeze_state=new_freeze_state,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to.address,
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
    params: Optional[algosdk_transaction.SuggestedParams] = None,
    close_assets_to: Optional[AlgoUser] = None,
    revocation_target: Optional[AlgoUser] = None,
    note: str = "",
    lease: str = "",
    rekey_to: Optional[AlgoUser] = None,
) -> Tuple[AlgoUser, algosdk_transaction.Transaction]:
    """Transfer Algorand assets to a target recipient.

    TODO: write docs!

    Returns
    -------
    None
    """
    # Materialize all of the optional arguments
    close_assets_to = close_assets_to or _NullUser
    revocation_target = revocation_target or _NullUser
    rekey_to = rekey_to or _NullUser

    txn = algosdk_transaction.AssetTransferTxn(
        sender.address,
        params,
        receiver=receiver.address,
        amt=amount,
        index=asset_id,
        close_assets_to=close_assets_to.address,
        revocation_target=revocation_target.address,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to.address,
    )
    return sender, txn


@transaction_boilerplate(
    format_finish=lambda txninfo: f'asset-id={txninfo["txn"]["txn"]["xaid"]}',
)
def opt_in_asset(
    sender: AlgoUser,
    asset_id: int,
    *,
    params: Optional[algosdk_transaction.SuggestedParams] = None,
    note: str = "",
    lease: str = "",
    rekey_to: Optional[AlgoUser] = None,
) -> Tuple[AlgoUser, algosdk_transaction.Transaction]:
    """Opt-in to an Algorand asset.

    TODO: write docs!

    Returns
    -------
    None
    """
    # Materialize all of the optional arguments
    rekey_to = rekey_to or _NullUser

    txn = algosdk_transaction.AssetOptInTxn(
        sender.address,
        params,
        asset_id,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to.address,
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
    params: Optional[algosdk_transaction.SuggestedParams] = None,
    note: str = "",
    lease: str = "",
    rekey_to: Optional[AlgoUser] = None,
) -> Tuple[AlgoUser, algosdk_transaction.Transaction]:
    """Opt-in to an Algorand asset.

    TODO: write docs!

    Returns
    -------
    None
    """
    # Materialize all of the optional arguments
    rekey_to = rekey_to or _NullUser

    txn = algosdk_transaction.AssetCloseOutTxn(
        sender.address,
        params,
        receiver.address,
        asset_id,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to.address,
    )
    return sender, txn


@transaction_boilerplate(
    no_sign=True,
)
def smart_signature_transaction(
    smart_signature: bytes,
    transaction: Tuple[AlgoUser, algosdk_transaction.Transaction],
    *,
    params: Optional[algosdk_transaction.SuggestedParams] = None,
) -> Tuple[AlgoUser, algosdk_transaction.LogicSigTransaction]:
    """Write docs here: TODO!"""
    logic_txn = algosdk_transaction.LogicSigTransaction(transaction[1], smart_signature)
    return _NullUser, logic_txn


class _MultisigTxn:
    def __init__(
        self,
        transaction: Tuple[AlgoUser, algosdk_transaction.Transaction],
        signing_accounts: List[AlgoUser],
        multisig_account: MultisigAccount,
    ):
        # Ignore the `AlgoUser` provided with the `transaction`. The signers are in `signing_accounts`
        self.transaction = transaction[1]
        self.signing_accounts = signing_accounts
        self.multisig_account = multisig_account

        # Create the multisig transaction
        self.multisig_transaction = algosdk_transaction.MultisigTransaction(
            self.transaction, self.multisig_account.attributes
        )

    def sign(self, _: Optional[str]) -> List[algosdk_transaction.MultisigTransaction]:
        # Sign the multisig transaction
        for signing_account in self.signing_accounts:
            self.multisig_transaction.sign(signing_account.private_key)

        return self.multisig_transaction


@transaction_boilerplate(
    no_params=True,
)
def multisig_transaction(
    multisig_account: MultisigAccount,
    transaction: Tuple[AlgoUser, algosdk_transaction.Transaction],
    signing_accounts: List[AlgoUser],
) -> Tuple[AlgoUser, _MultisigTxn]:
    """Write docs here: TODO!"""
    # The signers are specified in the `signing_accounts` list and are
    # handled specially by the `_MultisigTxn` class. So return the `_NullUser`
    # as the signer as a placeholder
    return _NullUser, _MultisigTxn(transaction, signing_accounts, multisig_account)


class _GroupTxn:
    _InputTxnType = Union[
        algosdk_transaction.Transaction,
        algosdk_transaction.LogicSigTransaction,
        _MultisigTxn,
    ]
    _SignedTxnType = Union[
        algosdk_transaction.SignedTransaction,
        algosdk_transaction.LogicSigTransaction,
        algosdk_transaction.MultisigTransaction,
    ]

    def __init__(self, transactions: List[Tuple[AlgoUser, _InputTxnType]]):
        # Separate out the `signers` and the `txns`
        self.signers = [signer for signer, _ in transactions]
        self.transactions = [txn for _, txn in transactions]

        # Assign the group ID, flattening out `LogicSigTransaction` and `_MultisigTxn`
        # to get the underlying `Transaction`
        flattened_txns = []
        for txn in self.transactions:
            if isinstance(txn, algosdk_transaction.LogicSigTransaction) or isinstance(
                txn, _MultisigTxn
            ):
                flattened_txns.append(txn.transaction)
            else:
                flattened_txns.append(txn)

        algosdk_transaction.assign_group_id(flattened_txns)

    def sign(self, _: Optional[str]) -> List[_SignedTxnType]:
        # Sign all of the transactions
        signed_txns = []
        for signer, txn in zip(self.signers, self.transactions):
            # Logic signature transactions simply get appended since they are already signed
            if isinstance(txn, algosdk_transaction.LogicSigTransaction):
                signed_txns.append(txn)
            else:
                signed_txns.append(txn.sign(signer.private_key))

        return signed_txns


@transaction_boilerplate(
    no_params=True,
)
def group_transaction(
    *transactions: Tuple[AlgoUser, algosdk_transaction.Transaction],
) -> Tuple[AlgoUser, _GroupTxn]:
    """Write docs here: TODO!"""
    # The signers are already included as the first elements
    # of the tuples in `transactions`, so return the `_NullUser`
    # as the signer of this group transaction
    return _NullUser, _GroupTxn(list(transactions))
