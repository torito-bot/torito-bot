from urllib.parse import quote


def build_alibaba_search_link(product_name: str) -> str:
    query = quote(product_name)
    return f"https://www.alibaba.com/trade/search?SearchText={query}"


def build_1688_search_link(product_name: str) -> str:
    query = quote(product_name)
    return f"https://s.1688.com/selloffer/offer_search.htm?keywords={query}"
