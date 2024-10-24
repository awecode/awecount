from decimal import Decimal
from enum import Enum

import pytest


class FeeType(str, Enum):
    FIXED = "fixed"
    PERCENTAGE = "percentage"
    SLAB_BASED = "slab_based"
    SLIDING_SCALE = "sliding_scale"
    TIME_BASED = "time_based"  # Not implemented yet


class TransactionFeeConfig:
    def __init__(self, fee_config: dict):
        self.fee_config = fee_config
        self.validate()

    def _validate_slabs(self):
        slabs = self.fee_config["slabs"]
        if not isinstance(slabs, list):
            raise ValueError("Slabs must be a list")

        prev_max = Decimal("0")
        for slab in slabs:
            if not all(key in slab for key in ["min_amount", "rate"]):
                raise ValueError("Each slab must specify min_amount and rate")

            current_min = Decimal(str(slab["min_amount"]))
            if current_min != prev_max:
                raise ValueError("Slabs must be continuous without gaps")

            if "max_amount" in slab:
                prev_max = Decimal(str(slab["max_amount"]))
            else:
                # Last slab can have no max_amount
                if slab != slabs[-1]:
                    raise ValueError("Only the last slab can have no maximum amount")
                prev_max = Decimal("infinity")

    def validate(self):
        if not isinstance(self.fee_config, dict):
            raise ValueError("Fee config must be a dictionary")

        if "type" not in self.fee_config:
            raise ValueError("Fee type must be specified")

        fee_type = self.fee_config["type"]

        if fee_type not in FeeType.__members__.values():
            raise ValueError(f"Invalid fee type: {fee_type}")

        if fee_type == FeeType.SLAB_BASED:
            if "slabs" not in self.fee_config:
                raise ValueError("Slabs must be specified")
            try:
                self._validate_slabs()
            except Exception as e:
                raise e

        if fee_type == FeeType.SLIDING_SCALE:
            if "slabs" not in self.fee_config:
                raise ValueError("Slabs must be specified")
            for slab in self.fee_config["slabs"]:
                if not all(key in slab for key in ["min_amount", "rate"]):
                    raise ValueError("Each slab must specify min_amount and rate")

        if "min_fee" in self.fee_config and "max_fee" in self.fee_config:
            min_fee = Decimal(str(self.fee_config["min_fee"]))
            max_fee = Decimal(str(self.fee_config["max_fee"]))
            if min_fee > max_fee:
                raise ValueError("Minimum fee cannot be greater than maximum fee")

    def _apply_fee_limits(self, fee: Decimal) -> Decimal:
        if "min_fee" in self.fee_config:
            fee = max(fee, Decimal(str(self.fee_config["min_fee"])))

        if "max_fee" in self.fee_config:
            fee = min(fee, Decimal(str(self.fee_config["max_fee"])))

        if "extra_fee" in self.fee_config:
            fee += Decimal(str(self.fee_config["extra_fee"]))

        return fee

    def _calculate_slab_based_fee(self, amount: Decimal, slabs: list[dict]) -> Decimal:
        total_fee = Decimal("0")
        remaining_amount = amount

        for slab in slabs:
            min_amount = Decimal(str(slab["min_amount"]))
            max_amount = Decimal(str(slab.get("max_amount", float("inf"))))
            rate = Decimal(str(slab["rate"]))

            # Calculate the amount that falls in this slab
            if remaining_amount <= 0:
                break

            slab_amount = min(remaining_amount, max_amount - min_amount)
            slab_fee = slab_amount * rate / 100
            total_fee += slab_fee

            remaining_amount -= slab_amount

        return total_fee

    def calculate_fee(self, amount: Decimal) -> Decimal:
        fee_type = self.fee_config["type"]

        # Calculate base fee
        fee = Decimal("0")

        if fee_type == FeeType.FIXED:
            fee = Decimal(str(self.fee_config["amount"]))

        elif fee_type == FeeType.PERCENTAGE:
            fee = amount * Decimal(str(self.fee_config["percentage"])) / 100

        elif fee_type == FeeType.SLAB_BASED:
            fee = self._calculate_slab_based_fee(amount, self.fee_config["slabs"])

        elif fee_type == FeeType.SLIDING_SCALE:
            _fee = Decimal("0")
            for slab in self.fee_config["slabs"]:
                if amount >= Decimal(str(slab["min_amount"])):
                    _fee = amount * Decimal(str(slab["rate"])) / 100
                else:
                    break
            fee = _fee

        return self._apply_fee_limits(fee)


# Test configurations
FIXED_FEE = {"type": "fixed", "amount": "10.00", "min_fee": "5.00", "max_fee": "15.00"}

PERCENTAGE_FEE = {
    "type": "percentage",
    "percentage": "2.5",
    "min_fee": "5.00",
    "max_fee": "100.00",
}

SLAB_BASED_FEE = {
    "type": "slab_based",
    "slabs": [
        {"min_amount": "0", "max_amount": "1000", "rate": "2.0"},
        {"min_amount": "1000", "max_amount": "5000", "rate": "1.5"},
        {"min_amount": "5000", "rate": "1.0"},
    ],
    "min_fee": "5.00",
    "max_fee": "200.00",
}

SLIDING_SCALE_FEE = {
    "type": "sliding_scale",
    "slabs": [
        {"min_amount": "0", "rate": "2.0"},
        {"min_amount": "1000", "rate": "1.5"},
        {"min_amount": "5000", "rate": "1.0"},
    ],
    "min_fee": "5.00",
    "max_fee": "200.00",
}


@pytest.mark.parametrize(
    "config,amount,expected",
    [
        # Fixed fee tests
        (FIXED_FEE, Decimal("100.00"), Decimal("10.00")),
        (FIXED_FEE, Decimal("1000.00"), Decimal("10.00")),
        # Percentage fee tests
        (PERCENTAGE_FEE, Decimal("100.00"), Decimal("5.00")),  # Min fee applied
        (PERCENTAGE_FEE, Decimal("1000.00"), Decimal("25.00")),
        (PERCENTAGE_FEE, Decimal("5000.00"), Decimal("100.00")),  # Max fee applied
        # Slab based tests
        (SLAB_BASED_FEE, Decimal("500.00"), Decimal("10.00")),  # Within first slab
        (SLAB_BASED_FEE, Decimal("2000.00"), Decimal("35.00")),  # Spans two slabs
        (SLAB_BASED_FEE, Decimal("6000.00"), Decimal("90.00")),  # Spans all slabs
        # Sliding scale tests
        (SLIDING_SCALE_FEE, Decimal("500.00"), Decimal("10.00")),  # First rate
        (SLIDING_SCALE_FEE, Decimal("2000.00"), Decimal("30.00")),  # Second rate
        (SLIDING_SCALE_FEE, Decimal("6000.00"), Decimal("60.00")),  # Third rate
    ],
)
def test_fee_calculation(config, amount, expected):
    fee_config = TransactionFeeConfig(config)
    calculated_fee = fee_config.calculate_fee(amount)
    assert calculated_fee == expected


def test_invalid_fee_type():
    with pytest.raises(ValueError, match="Invalid fee type"):
        TransactionFeeConfig({"type": "invalid"})


@pytest.mark.parametrize(
    "config,error_message",
    [
        (
            {
                "type": "slab_based",
                "slabs": [
                    {"min_amount": "0", "max_amount": "1000", "rate": "2.0"},
                    {"min_amount": "2000", "max_amount": "5000", "rate": "1.5"},
                ],
            },
            "Slabs must be continuous without gaps",
        ),
        (
            {
                "type": "slab_based",
                "slabs": [
                    {"min_amount": "0", "rate": "2.0"},
                    {"min_amount": "1000", "rate": "1.5"},
                ],
            },
            "Only the last slab can have no maximum amount",
        ),
        (
            {"type": "sliding_scale", "slabs": [{"min_amount": "0"}]},
            "Each slab must specify min_amount and rate",
        ),
    ],
)
def test_invalid_configurations(config, error_message):
    with pytest.raises(ValueError, match=error_message):
        TransactionFeeConfig(config)


def test_extra_fee():
    config = {"type": "fixed", "amount": "10.00", "extra_fee": "5.00"}
    fee_config = TransactionFeeConfig(config)
    calculated_fee = fee_config.calculate_fee(Decimal("100.00"))
    assert calculated_fee == Decimal("15.00")


def test_slab_based_edge_cases():
    config = {
        "type": "slab_based",
        "slabs": [
            {"min_amount": "0", "max_amount": "1000", "rate": "2.0"},
            {"min_amount": "1000", "max_amount": "5000", "rate": "1.5"},
            {"min_amount": "5000", "rate": "1.0"},
        ],
    }
    fee_config = TransactionFeeConfig(config)

    # Test exact slab boundaries
    assert fee_config.calculate_fee(Decimal("1000.00")) == Decimal("20.00")
    assert fee_config.calculate_fee(Decimal("5000.00")) == Decimal("80.00")

    # Test zero amount
    assert fee_config.calculate_fee(Decimal("0")) == Decimal("0")


def test_sliding_scale_edge_cases():
    config = {
        "type": "sliding_scale",
        "slabs": [
            {"min_amount": "0", "rate": "2.0"},
            {"min_amount": "1000", "rate": "1.5"},
            {"min_amount": "5000", "rate": "1.0"},
        ],
    }
    fee_config = TransactionFeeConfig(config)

    # Test exact threshold amounts
    assert fee_config.calculate_fee(Decimal("1000.00")) == Decimal("15.00")
    assert fee_config.calculate_fee(Decimal("5000.00")) == Decimal("50.00")

    # Test zero amount
    assert fee_config.calculate_fee(Decimal("0")) == Decimal("0")


def test_min_max_fee_validation():
    with pytest.raises(
        ValueError, match="Minimum fee cannot be greater than maximum fee"
    ):
        TransactionFeeConfig(
            {"type": "fixed", "amount": "10.00", "min_fee": "20.00", "max_fee": "15.00"}
        )


@pytest.mark.parametrize(
    "amount,min_fee,max_fee,expected",
    [
        ("10.00", "15.00", "30.00", "15.00"),  # Min fee applied
        ("100.00", "5.00", "20.00", "20.00"),  # Max fee applied
        ("50.00", "10.00", "100.00", "25.00"),  # Within limits
    ],
)
def test_fee_limits(amount, min_fee, max_fee, expected):
    config = {
        "type": "percentage",
        "percentage": "50.00",  # 50% fee
        "min_fee": min_fee,
        "max_fee": max_fee,
    }
    fee_config = TransactionFeeConfig(config)
    calculated_fee = fee_config.calculate_fee(Decimal(amount))
    assert calculated_fee == Decimal(expected)
