from app.parsers.niche_parser import load_niche_products
from app.utils.margins import calculate_margin_percent
from app.utils.product_score import (
    get_competition_level,
    get_potential_level,
    get_recommendation,
)
from app.utils.torito_score import calculate_torito_score, get_score_label


def search_products_by_niche(query: str):
    query = query.strip().lower()
    source_products = load_niche_products()
    result = []

    for p in source_products:
        niches = [n.lower() for n in p.get("niches", [])]

        if query in niches or any(query in niche for niche in niches):
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

    result.sort(key=lambda item: (item["score"], item["days"], item["margin"]), reverse=True)
    return result
