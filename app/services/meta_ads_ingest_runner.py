from app.database.db import save_meta_ads_products, update_meta_ads_cache_state
from app.utils.margins import calculate_margin_percent
from app.utils.product_score import (
    get_competition_level,
    get_potential_level,
    get_recommendation,
)
from app.utils.torito_score import calculate_torito_score, get_score_label


def ingest_seed_products_for_geo(geo_code: str):
    geo_code = geo_code.lower()

    seed = [
        {
            "product_name": "Portable Vacuum Cleaner",
            "advertisers_count": 25,
            "ads_count": 33,
            "avg_days": 14,
            "avg_price": 49,
            "est_cost": 15,
        },
        {
            "product_name": "Neck Massager",
            "advertisers_count": 18,
            "ads_count": 24,
            "avg_days": 7,
            "avg_price": 42,
            "est_cost": 14,
        },
        {
            "product_name": "Magnetic Phone Holder",
            "advertisers_count": 27,
            "ads_count": 31,
            "avg_days": 11,
            "avg_price": 24,
            "est_cost": 6,
        },
    ]

    result = []

    for item in seed:
        margin = calculate_margin_percent(item["avg_price"], item["est_cost"])
        score = calculate_torito_score(margin, item["advertisers_count"], item["avg_days"])

        result.append({
            "product_key": f"{geo_code}:{item['product_name'].lower()}",
            "product_name": item["product_name"],
            "geo": geo_code,
            "source": "Meta Ads",
            "advertisers_count": item["advertisers_count"],
            "ads_count": item["ads_count"],
            "avg_days": item["avg_days"],
            "avg_price": item["avg_price"],
            "est_cost": item["est_cost"],
            "margin_percent": margin,
            "competition": get_competition_level(item["advertisers_count"]),
            "potential": get_potential_level(margin, item["advertisers_count"], item["avg_days"]),
            "recommendation": get_recommendation(margin, item["advertisers_count"], item["avg_days"]),
            "torito_score": score,
            "score_label": get_score_label(score),
        })

    save_meta_ads_products(result)
    update_meta_ads_cache_state(geo_code, "success", f"Seeded {len(result)} products")

    return len(result)
