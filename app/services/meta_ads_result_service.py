from app.database.db import get_meta_ads_products_by_geo, get_meta_ads_cache_state


def get_meta_ads_top10(geo_code: str):
    products = get_meta_ads_products_by_geo(geo_code, limit=10)
    cache_state = get_meta_ads_cache_state(geo_code)

    return {
        "geo": geo_code.lower(),
        "cache_state": cache_state,
        "products": products,
    }
