from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def ad_links_keyboard(ad_library_url=None, creative_preview_url=None, ad_snapshot_url=None):
    rows = []

    if ad_library_url:
        rows.append([InlineKeyboardButton(text="🔗 Відкрити рекламу", url=ad_library_url)])

    preview_url = creative_preview_url or ad_snapshot_url
    if preview_url:
        rows.append([InlineKeyboardButton(text="🖼 Подивитись крео", url=preview_url)])

    if not rows:
        return None

    return InlineKeyboardMarkup(inline_keyboard=rows)
