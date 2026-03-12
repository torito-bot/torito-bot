from app.database.db import get_usage_today, track_usage, get_user_limits


def check_limit(user_id: int):
    usage = get_usage_today(user_id)
    limits = get_user_limits(user_id)
    total_limit = limits["total_limit"]

    if usage >= total_limit:
        return False, usage, total_limit

    track_usage(user_id)
    return True, usage + 1, total_limit
