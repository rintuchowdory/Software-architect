def money(value: float) -> str:
    # German-style formatting: thousands dot, symbol after the number.
    formatted = f"{value:,.0f}".replace(",", ".")
    return f"{formatted} €"
