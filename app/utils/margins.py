def calculate_margin_percent(price: float, cost: float) -> int:
    if cost <= 0:
        return 0
    return round(((price - cost) / cost) * 100)
