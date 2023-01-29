AlgoPytest API Reference
========================

Account Entities
----------------

Module containing class abstractions for the various possible entities in Algorand.

.. automodule:: algopytest.entities
   :members: AlgoUser, MultisigAccount, SmartContractAccount
   :undoc-members:
   :show-inheritance:

      
Transaction Operations
----------------------

Module containing the transaction operations used to interact with Smart Contracts and Signatures.

.. automodule:: algopytest.transaction_ops

Transaction Operations Context Managers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: algopytest.transaction_ops
   :members: TxnElemsContext, TxnIDContext
   :undoc-members:
   :show-inheritance:

Transaction Operations
~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: algopytest.transaction_ops
   :members: call_app, clear_app, close_out_app, close_out_asset, create_app,
             create_compiled_app, create_asset, delete_app, destroy_asset,
             freeze_asset, opt_in_app, opt_in_asset, payment_transaction,
             transfer_asset, update_app, update_asset
   :undoc-members:
   :show-inheritance:
      
Advanced Transaction Operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: algopytest.transaction_ops
   :members: group_transaction, multisig_transaction, smart_signature_transaction
   :undoc-members:
   :show-inheritance:
      
      
Algorand Client Functions
-------------------------

Module containing helper functions for accessing the Algorand blockchain.

.. automodule:: algopytest.client_ops
   :members:
   :undoc-members:
   :show-inheritance:
