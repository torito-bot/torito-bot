from app.parsers.meta_ads_real import fetch_meta_ads_by_geo
from app.database.db import (
    save_meta_ads_raw,
    save_meta_ads_products,
    update_meta_ads_cache_state,
)
from app.utils.margins import calculate_margin_percent
from app.utils.product_score import (
    get_competition_level,
    get_potential_level,
    get_recommendation,
)
from app.utils.torito_score import calculate_torito_score, get_score_label


def normalize_meta_ads_to_products(raw_ads, geo_code: str):
    products = []

    for idx, ad in enumerate(raw_ads, start=1):
        product_name = ad.get("product_name") or f"Meta Product {idx}"
        ads_count = ad.get("ads_count", 1)
        advertisers_count = ad.get("advertisers_count", 1)
        avg_days = ad.get("active_days", 0)
        avg_price = ad.get("avg_price", 0)
        est_cost = ad.get("est_cost", 0)

        margin = calculate_margin_percent(avg_price, est_cost) if est_cost else 0
        score = calculate_torito_score(margin, advertisers_count, avg_days)

        products.append({
            "product_key": f"{geo_code}:{product_name.lower()}",
            "product_name": product_name,
            "geo": geo_code.lower(),
            "source": "Meta Ads",
            "advertisers_count": advertisers_count,
            "ads_count": ads_count,
            "avg_days": avg_days,
            "avg_price": avg_price,
            "est_cost": est_cost,
            "margin_percent": margin,
            "competition": get_competition_level(advertisers_count),
            "potential": get_potential_level(margin, advertisers_count, avg_days),
            "recommendation": get_recommendation(margin, advertisers_count, avg_days),
            "torito_score": score,
            "score_label": get_score_label(score),
        })

    return products


def run_meta_ads_ingest(geo_code: str):
    update_meta_ads_cache_state(geo_code, "running", "Meta ingest started")

    raw_ads = fetch_meta_ads_by_geo(geo_code)
    save_meta_ads_raw(raw_ads)

    products = normalize_meta_ads_to_products(raw_ads, geo_code)
    save_meta_ads_products(products)

    update_meta_ads_cache_state(
        geo_code,
        "success",
        f"Ingest complete. Raw ads: {len(raw_ads)}, products: {len(products)}"
    )

    return {
        "geo": geo_code.lower(),
        "raw_ads_count": len(raw_ads),
        "products_count": len(products),
    }
