from app.parsers.meta_ads import load_meta_ads_mock
from app.utils.margins import calculate_margin_percent
from app.utils.product_score import (
    get_competition_level,
    get_potential_level,
    get_recommendation,
)
from app.utils.torito_score import calculate_torito_score, get_score_label


def get_top_score_products():
    source_products = load_meta_ads_mock()
    result = []

    for p in source_products:
        margin = calculate_margin_percent(p["price"], p["cost"])
        score = calculate_torito_score(margin, p["ads"], p["days"])

        result.append({
            "name": p["name"],
            "ads": p["ads"],
            "days": p["days"],
            "price": p["price"],
            "cost": p["cost"],
            "source": p["source"],
            "margin": margin,
            "competition": get_competition_level(p["ads"]),
            "potential": get_potential_level(margin, p["ads"], p["days"]),
            "recommendation": get_recommendation(margin, p["ads"], p["days"]),
            "score": score,
            "score_label": get_score_label(score),
        })

    result.sort(key=lambda item: (item["score"], item["margin"], item["days"]), reverse=True)
    return result
