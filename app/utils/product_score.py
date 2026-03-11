def get_competition_level(ads: int) -> str:
    if ads >= 30:
        return "висока"
    if ads >= 15:
        return "середня"
    return "низька"


def get_potential_level(margin: int, ads: int, days: int) -> str:
    if margin >= 200 and ads <= 25 and days <= 14:
        return "високий"
    if margin >= 120:
        return "середній"
    return "низький"


def get_recommendation(margin: int, ads: int, days: int) -> str:
    if margin >= 200 and ads <= 25 and days <= 14:
        return "можна тестувати"
    if margin >= 120 and ads <= 35:
        return "потрібен обережний тест"
    return "ризиковано"
