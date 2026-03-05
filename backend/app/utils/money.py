from decimal import Decimal, ROUND_HALF_UP


TWOPLACES = Decimal("0.01")


def quantize_money(amount: Decimal) -> Decimal:
    return amount.quantize(TWOPLACES, rounding=ROUND_HALF_UP)
