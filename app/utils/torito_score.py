def calculate_torito_score(margin: int, ads: int, days: int) -> int:
    score = 0

    if margin >= 250:
        score += 40
    elif margin >= 180:
        score += 30
    elif margin >= 120:
        score += 20
    else:
        score += 10

    if 7 <= days <= 14:
        score += 30
    elif days > 14:
        score += 20
    else:
        score += 10

    if ads <= 15:
        score += 30
    elif ads <= 25:
        score += 20
    else:
        score += 10

    return min(score, 100)


def get_score_label(score: int) -> str:
    if score >= 80:
        return "🚀 сильний"
    if score >= 60:
        return "⚡ хороший"
    if score >= 40:
        return "⚠️ середній"
    return "❌ слабкий"
