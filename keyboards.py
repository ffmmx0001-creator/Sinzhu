from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎴 Harem", callback_data="harem_1"),
            InlineKeyboardButton("💰 Balance", callback_data="balance"),
        ],
        [
            InlineKeyboardButton("📦 Daily", callback_data="daily"),
            InlineKeyboardButton("🌟 Welkin", callback_data="welkin"),
        ],
        [
            InlineKeyboardButton("🛒 Shop", callback_data="shop_1"),
            InlineKeyboardButton("💎 Treasure", callback_data="treasure"),
        ],
        [
            InlineKeyboardButton("🏅 Top Collectors", callback_data="top"),
            InlineKeyboardButton("💸 Top Rich", callback_data="tops"),
        ],
        [
            InlineKeyboardButton("🎖️ My Rank", callback_data="rank"),
            InlineKeyboardButton("📜 Waifu Pass", callback_data="wpass"),
        ],
    ])

def harem_keyboard(waifus, page, total_pages, user_id):
    buttons = []
    for w in waifus:
        buttons.append([InlineKeyboardButton(
            f"{w['rarity']} {w['name']} ({w['anime']})",
            callback_data=f"waifu_detail_{w['id']}"
        )])
    
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("◀️ Prev", callback_data=f"harem_{page-1}"))
    nav.append(InlineKeyboardButton(f"📖 {page}/{total_pages}", callback_data="noop"))
    if page < total_pages:
        nav.append(InlineKeyboardButton("Next ▶️", callback_data=f"harem_{page+1}"))
    
    if nav:
        buttons.append(nav)
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)

def waifu_detail_keyboard(uw_id, fav_id=None):
    buttons = [
        [
            InlineKeyboardButton(
                "⭐ Unfav" if fav_id == uw_id else "⭐ Set Fav",
                callback_data=f"fav_{uw_id}"
            ),
            InlineKeyboardButton("💸 Sell", callback_data=f"sell_confirm_{uw_id}"),
        ],
        [
            InlineKeyboardButton("🎁 Gift", callback_data=f"gift_init_{uw_id}"),
            InlineKeyboardButton("🔙 Harem", callback_data="harem_1"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)

def sell_confirm_keyboard(uw_id, sell_price):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"✅ Sell for {sell_price} Onex", callback_data=f"sell_do_{uw_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data=f"waifu_detail_{uw_id}"),
        ]
    ])

def shop_keyboard(waifus, page, total_pages):
    buttons = []
    for w in waifus:
        from waifu_data import RARITY_TIERS
        price = RARITY_TIERS.get(w['rarity'], {}).get('buy_price', 1000)
        buttons.append([InlineKeyboardButton(
            f"{w['rarity']} {w['name']} — {price} Onex",
            callback_data=f"buy_confirm_{w['id']}"
        )])
    
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("◀️ Prev", callback_data=f"shop_{page-1}"))
    nav.append(InlineKeyboardButton(f"🛒 {page}/{total_pages}", callback_data="noop"))
    if page < total_pages:
        nav.append(InlineKeyboardButton("Next ▶️", callback_data=f"shop_{page+1}"))
    
    if nav:
        buttons.append(nav)
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)

def buy_confirm_keyboard(waifu_id, price):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"✅ Buy for {price} Onex", callback_data=f"buy_do_{waifu_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data=f"shop_1"),
        ]
    ])

def admin_panel_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add Waifu", callback_data="admin_add_waifu"),
            InlineKeyboardButton("🗑️ Del Waifu", callback_data="admin_del_waifu_list_1"),
        ],
        [
            InlineKeyboardButton("📊 Bot Stats", callback_data="admin_stats"),
            InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
        ],
        [
            InlineKeyboardButton("💰 Give Onex", callback_data="admin_give_onex"),
            InlineKeyboardButton("🌟 Give Waifu", callback_data="admin_give_waifu"),
        ],
        [
            InlineKeyboardButton("🔧 Set Spawn Rate", callback_data="admin_spawn_rate"),
            InlineKeyboardButton("📋 All Waifus", callback_data="admin_list_waifus_1"),
        ],
        [InlineKeyboardButton("🔙 Close", callback_data="close_menu")],
    ])

def top_keyboard(top_type="collectors"):
    other = "tops" if top_type == "collectors" else "top"
    other_label = "💸 Top Rich" if top_type == "collectors" else "🏅 Top Collectors"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(other_label, callback_data=other)],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")],
    ])

def rank_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏅 Top List", callback_data="top"),
            InlineKeyboardButton("📜 Waifu Pass", callback_data="wpass"),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")],
    ])
                
            
        
