Demos Using AlgoPytest
======================

These demo projects give examples of how a real-world project may use `AlgoPytest` for its testing. They provide greater context for how to integrate `AlgoPytest` into your project. 

Relevant Test Demo Code
-----------------------
This is where you should look in the demo repositories to find the relevant `AlgoPytest` code used to write unit tests.

Inside the ``./tests`` directory:
   * ``conftest.py``: Mainly contains Pytest fixtures of smart contracts, smart signatures, and users commonly used throughout the tests.
   * Files prefixed with ``test_``: Contains all of the tests utilizing the `AlgoPytest` helpers and fixtures.

Demos Repositories
------------------

* `Algo-Diploma <https://github.com/DamianB-BitFlipper/algo-diploma>`_: A Smart Contract to issue college graduates their diplomas on the Algorand blockchain.
* `Algo-WizCoin <https://github.com/DamianB-BitFlipper/algo-wizcoin>`_: An Algorand ASA token and a Smart Contract that issues this WizCoin ASA token symbolizing membership to the WizCoin group.
* `Algo-Recurring-Payments <https://github.com/DamianB-BitFlipper/algo-recurring-payments>`_: A Smart Signature program which implements recurring payments on a predefined monotonic schedule.
* `Algo-Quizzer <https://github.com/DamianB-BitFlipper/algo-quizzer>`_: Multiple Smart Contracts interacting with one another to implement a teacher-student quiz.
