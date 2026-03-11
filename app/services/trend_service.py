from app.database.db import get_products_by_type
from app.utils.margins import calculate_margin_percent
from app.utils.product_score import (
    get_competition_level,
    get_potential_level,
    get_recommendation,
)


def get_trending_products():
    source_products = get_products_by_type("trending")
    result = []

    for p in source_products:
        margin = calculate_margin_percent(p["price"], p["cost"])

        result.append({
            "name": p["name"],
            "ads": p["ads"],
            "days": p["days"],
            "price": p["price"],
            "cost": p["cost"],
            "margin": margin,
            "competition": get_competition_level(p["ads"]),
            "potential": get_potential_level(margin, p["ads"], p["days"]),
            "recommendation": get_recommendation(margin, p["ads"], p["days"]),
        })

    return result
