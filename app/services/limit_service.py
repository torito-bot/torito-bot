from app.database.db import get_usage_today, track_usage, get_user_limits


def check_limit(user_id):

    usage = get_usage_today(user_id)
    limits = get_user_limits(user_id)

    if usage >= limits["total_limit"]:
        return False, usage, limits["total_limit"]

    track_usage(user_id)

    return True, usage + 1, limits["total_limit"]
