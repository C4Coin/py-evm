from typing import Type  # noqa: F401
from eth.rlp.blocks import BaseBlock  # noqa: F401
from eth.vm.state import BaseState  # noqa: F401


from eth.constants import (
    BLOCK_REWARD,
    UNCLE_DEPTH_PENALTY_FACTOR,
)
from eth.vm.base import VM
from eth.rlp.receipts import (
    Receipt,
)
from eth.rlp.logs import (
    Log,
)

from .blocks import FheBlock
from .state import FheState
from .headers import (
    create_fhe_header_from_parent,
    compute_fhe_difficulty,
    configure_fhe_header,
)
from .validation import validate_fhe_transaction_against_header


def make_fhe_receipt(base_header, transaction, computation, state):
    # Reusable for other forks

    logs = [
        Log(address, topics, data)
        for address, topics, data
        in computation.get_log_entries()
    ]

    gas_remaining = computation.get_gas_remaining()
    gas_refund = computation.get_gas_refund()
    tx_gas_used = (
        transaction.gas - gas_remaining
    ) - min(
        gas_refund,
        (transaction.gas - gas_remaining) // 2,
    )
    gas_used = base_header.gas_used + tx_gas_used

    receipt = Receipt(
        state_root=state.state_root,
        gas_used=gas_used,
        logs=logs,
    )

    return receipt


class FheVM(VM):
    # fork name
    fork = 'fhe'  # type: str

    # classes
    block_class = FheBlock  # type: Type[BaseBlock]
    _state_class = FheState  # type: Type[BaseState]

    # methods
    create_header_from_parent = staticmethod(create_fhe_header_from_parent)
    compute_difficulty = staticmethod(compute_fhe_difficulty)
    configure_header = configure_fhe_header
    make_receipt = staticmethod(make_fhe_receipt)
    validate_transaction_against_header = validate_fhe_transaction_against_header

    @staticmethod
    def get_block_reward():
        return BLOCK_REWARD

    @staticmethod
    def get_uncle_reward(block_number, uncle):
        return BLOCK_REWARD * (
            UNCLE_DEPTH_PENALTY_FACTOR + uncle.block_number - block_number
        ) // UNCLE_DEPTH_PENALTY_FACTOR

    @classmethod
    def get_nephew_reward(cls):
        return cls.get_block_reward() // 32
