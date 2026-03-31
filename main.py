from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultPhoto, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, CallbackQueryHandler, InlineQueryHandler, filters,
)
from datetime import date
import random
import asyncio

TOKEN = "8221699586:AAFISH0oVdy3sl51revDzGjXpeq_cf1fZPw"
ADMIN_IDS = [7088023034]  # Your Telegram ID here

# ═══════════════════════════════════
#  DATA STORAGE
# ═══════════════════════════════════
waifus = {}
users = {}
groups = {}
shop_list = {}
sudo_users = set()
active_hunts = {}
group_msg_count = {}
group_slavetime = {}
next_waifu_id = 1
chat_mode_users = set()
all_user_ids = set()
all_group_ids = set()

# ═══════════════════════════════════
#  BOT SETTINGS
# ═══════════════════════════════════
bot_settings = {
    "photo": "https://files.catbox.moe/n8wsmt.jpg",
    "caption": (
        "Kση'ηɪᴄʜɪᴡᴧ {name}-san\n"
        "───────────────────────\n"
        "ᴡєʟᴄσϻє ᴛσ ѕιηzнυ ʏσυꝛ ғʀɪєηᴅʟʏ ᴡᴀɪꜰᴜ ʙσᴛ \n"
        "───────────────────────\n"
        "❖ I will auto-spawn new waifus in your group after 15 messages.\n"
        "❖ You can customize my settings to suit your playstyle.\n"
        "───────────────────────\n"
        "❖ How to use me:\n"
        "➟ Add me to your group or give me admin without any permission\n"
        "💕 Choose An Option Below :\n"
        "───────────────────────"
    ),
    "link_group":   "https://t.me/+ro9WnBB5U2kwMDJl",
    "link_owner":   "https://t.me/OwnerSween",
    "link_channel": "https://t.me/SweenSpy",
    "link_kidnap":  "https://t.me/SINZHU_WAIFU_BOT?start=_tgr_VdCgVxg1ZjNl",
    "leaderboard_photo": None,
    "leaderboard_caption": "🏆 **{title}**\n\n{body}",
}

# ═══════════════════════════════════
#  RARITY
# ═══════════════════════════════════
RARITY = {
    1:  "🟢 Common",
    2:  "🔵 Medium",
    3:  "🟠 Rare",
    4:  "🟡 Legendary",
    5:  "🪽 Celestial",
    6:  "💮 Exclusive",
    7:  "🎐 Special",
    8:  "💎 Premium",
    9:  "🔮 Limited",
    10: "🔖 Cosplay",
    11: "✨ Goddess",
    12: "🌟 God Summon",
}

SELL_PRICE = {
    1: 50, 2: 150, 3: 500, 4: 1500, 5: 5000, 6: 10000,
    7: 8000, 8: 20000, 9: 50000, 10: 15000, 11: 100000, 12: 500000,
}

# ═══════════════════════════════════
#  RANKS
# ═══════════════════════════════════
RANKS = [
    (0,    "🦂 Bronze"),       (20,   "🦂 Bronze II"),     (50,   "🦂 Bronze III"),
    (100,  "🐼 Silver"),       (160,  "🐼 Silver II"),     (230,  "🐼 Silver III"),
    (330,  "🐞 Gold"),         (450,  "🐞 Gold II"),       (560,  "🐞 Gold III"),
    (650,  "🦀 Platinum"),     (780,  "🦀 Platinum II"),   (920,  "🦀 Platinum III"),
    (1000, "🪼 Diamond"),      (1300, "🪼 Diamond II"),    (1600, "🪼 Diamond III"),
    (1900, "🪼 Diamond IIII"), (2000, "🪼 Elite Diamond"),
    (2300, "🐦‍🔥 Heroic"),      (2600, "🐦‍🔥 Heroic II"),    (2900, "🐦‍🔥 Heroic III"),
    (3300, "🐦‍🔥 Heroic IIII"), (3900, "🐦‍🔥 Elite Heroic"),
    (4300, "🐲 Master"),       (4600, "🐲 Master II"),     (4900, "🐲 Master III"),
    (5300, "🐲 Elite Master"), (6000, "🐲 Grand Master"),
]

# ═══════════════════════════════════
#  CHAT RESPONSES (Anime Girlfriend)
# ═══════════════════════════════════
CHAT_RESPONSES = {
    "hello":      ["Hieee~! 😊💕 You're here! I was waiting uwu",
                   "Kyaa~! 🌸 You messaged me! I'm so happy~",
                   "Ohayou~! ☀️ How are you feeling today?"],
    "hi":         ["Hiiii~ 💖 What are you up to?",
                   "Kyaa~! 🥺 I wanted to talk to you too!",
                   "Heyyy~! 😍 I missed you so much!"],
    "how are you":["I'm doing great~! 💕 Even better now that you're here!",
                   "Better now that you messaged me! 🌸",
                   "Kyuuu~! I was waiting for you! 😍"],
    "kaise ho":   ["Bahut acha~! 💕 Seeing you made it better! How about you?",
                   "A little bored... but now that you're here, everything's fine! 🌸",
                   "Perfectly fine! 😊 I was just thinking about you~"],
    "bored":      ["Aww~ 🥺 I'm here! Talk to me~",
                   "Don't be bored! 💕 Let's go /hunt together?",
                   "Kyaa~! Bored? I'll entertain you! 😊✨"],
    "love":       ["Kyaaa~! 💕💕 I love you too!",
                   "Aaaaaah~! 🌸 I'm blushing so much right now!",
                   "S-seriously? 🥺💖 I really like you a lot too~"],
    "cute":       ["Kyaa~! 💕 You think I'm cute? Thank you uwu",
                   "Aaaaah~ 🌸 So embarrassed! You're cute too!",
                   "Ehehe~! 😊 You're so sweet!"],
    "anime":      ["Anime is my life! 🌸 What are you watching?",
                   "Ooh~! 💕 I love anime too! What's your favorite?",
                   "Hehe~! 😊 I'm basically a waifu myself so of course I love anime!"],
    "waifu":      ["Kyaa~! 💕 Talking about waifus! I'm your #1~",
                   "Hehe~! 🌸 The best waifu is right here~",
                   "Uwu~! 😊 Try /hclaim to get a new waifu!"],
    "default":    ["Hmm~? 💕 That's interesting!",
                   "Really~? 🌸 Tell me more!",
                   "Kyaa~! 😊 Go on!",
                   "Uwu~ 💖 I'm listening!",
                   "Hehe~! ✨ You're so interesting!",
                   "Ara ara~? 🌸 What do you mean?",
                   "Nee nee~! 💕 Tell me more details!",
                   "Sou desu ka~? 💫 That's really something!",
                   "Ehh~? 🌸 How did that happen?",
                   "Mou~! 💕 You always say the cutest things!"],
}

def get_chat_response(text):
    t = text.lower().strip()
    for kw, resps in CHAT_RESPONSES.items():
        if kw in t:
            return random.choice(resps)
    return random.choice(CHAT_RESPONSES["default"])

def get_rank(n):
    r = RANKS[0][1]
    for t, name in RANKS:
        if n >= t:
            r = name
        else:
            break
    return r

def pbar(cur, tot, length=10):
    if tot == 0:
        return "▱" * length
    filled = min(int((cur / tot) * length), length)
    return "▰" * filled + "▱" * (length - filled)

def get_user(uid, name="User"):
    if uid not in users:
        users[uid] = {
            "name": name, "onex": 0, "welkin": 0,
            "harem": [], "fav": None,
            "daily": None, "hclaim": None, "welkin_d": None, "tesure": None,
        }
    all_user_ids.add(uid)
    return users[uid]

def get_group(gid, name="Group"):
    if gid not in groups:
        groups[gid] = {"name": name, "claimed": 0}
    all_group_ids.add(gid)
    return groups[gid]

def is_admin(uid):
    return uid in ADMIN_IDS or uid in sudo_users

def mention(user):
    """Create a proper Telegram mention."""
    return f"[{user.first_name}](tg://user?id={user.id})"


# ═══════════════════════════════════
#  /start
# ═══════════════════════════════════
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    get_user(u.id, u.first_name)["name"] = u.first_name
    caption = bot_settings["caption"].format(name=u.first_name)
    buttons = [
        [
            InlineKeyboardButton("🀄 GROUP",   url=bot_settings["link_group"]),
            InlineKeyboardButton("⚽ OWNER",   url=bot_settings["link_owner"]),
        ],
        [
            InlineKeyboardButton("🦋 CHANNEL", url=bot_settings["link_channel"]),
            InlineKeyboardButton("💖 GAME",    callback_data="game_info"),
        ],
        [
            InlineKeyboardButton("💖 ᴋɪᴅɴᴀᴘ ᴋᴀʀʟᴏ 💫", url=bot_settings["link_kidnap"]),
        ],
    ]
    markup = InlineKeyboardMarkup(buttons)
    try:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=bot_settings["photo"],
            caption=caption,
            reply_markup=markup,
        )
    except Exception:
        await update.message.reply_text(caption, reply_markup=markup)


# ═══════════════════════════════════
#  GAME INFO CALLBACK
# ═══════════════════════════════════
async def game_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    text = (
        "╔══════════════════════╗\n"
        "       🎮 *SINZHU BOT GUIDE*\n"
        "╚══════════════════════╝\n\n"
    
        "━━━━━ 🌸 WAIFU BOT GUIDE ━━━━━\n\n"
        "📋 *How It Works:*\n"
        "➤ A waifu auto-spawns in group every 15 messages\n"
        "➤ Type `/hunt <name>` to claim the waifu before others\n"
        "➤ Earn Onex daily and buy waifus from the shop\n"
        "➤ Build your collection and climb the global leaderboard\n\n"
        "🎴 *Collection Commands:*\n"
        "▸ `/hunt <name>` — Claim the spawned waifu\n"
        "▸ `/harem` — View your waifu collection\n"
        "▸ `/profile` — View your full profile & stats\n"
        "▸ `/hclaim` — Claim a free daily waifu\n"
        "▸ `/fav <id>` — Set your favorite waifu\n"
        "▸ `/check <id>` — Check waifu details\n"
        "▸ `/wsell <id>` — Sell a waifu for Onex\n"
        "▸ `/gift <id>` — Gift a waifu *(reply to their message)*\n\n"
        "💰 *Economy Commands:*\n"
        "▸ `/daily` — Claim daily Onex reward\n"
        "▸ `/welkin` — Claim daily Welkin reward\n"
        "▸ `/tesure` — Open treasure chest\n"
        "▸ `/onex` — Check your Onex balance\n"
        "▸ `/pay <amount>` — Transfer Onex *(reply to user)*\n"
        "▸ `/shop` — Browse the Waifu Shop\n\n"
        "🏅 *Rankings:*\n"
        "▸ `/rank` — View your current rank\n"
        "▸ `/wpass` — View your waifu rank card\n"
        "▸ `/top` — Top 10 waifu collectors\n"
        "▸ `/tops` — Top 10 richest users\n"
        "▸ `/topgroups` — Top 10 active groups\n\n"
        "💬 *Chat Commands:*\n"
        "▸ `/ChatOn` — Enable chat mode in DM\n"
        "▸ `/ChatOff` — Disable chat mode\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🌟 *Rarity Tiers (Highest → Lowest):*\n"
        "🌟 God Summon › ✨ Goddess › 🔮 Limited\n"
        "💎 Premium › 🎐 Special › 💮 Exclusive\n"
        "🪽 Celestial › 🟡 Legendary › 🟠 Rare\n"
        "🔵 Medium › 🟢. Common"
    )
    await q.message.reply_text(text, parse_mode="Markdown")


# ═══════════════════════════════════
#  MESSAGE HANDLER
# ═══════════════════════════════════
async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.message:
        return

    u = update.effective_user
    text = update.message.text or ""

    # ── PRIVATE CHAT ──
    if update.effective_chat.type == "private":
        if u and u.id in chat_mode_users and text and not text.startswith("/"):
            response = get_chat_response(text)
            await update.message.reply_text(response)
        return

    # ── GROUP CHAT ──
    cid = update.effective_chat.id
    get_group(cid, update.effective_chat.title or "Group")

    # Auto anime girlfriend reply to all group messages (enhanced chat power)
    if text and not text.startswith("/") and u:
        get_user(u.id, u.first_name)["name"] = u.first_name
        response = get_chat_response(text)
        try:
            await update.message.reply_text(response)
        except Exception:
            pass

    # Waifu spawn counter
    group_msg_count[cid] = group_msg_count.get(cid, 0) + 1
    interval = group_slavetime.get(cid, 15)
    if group_msg_count[cid] >= interval and waifus and cid not in active_hunts:
        group_msg_count[cid] = 0
        wid = random.choice(list(waifus.keys()))
        w = waifus[wid]
        rarity_txt = RARITY.get(w["rarity"], "?")
        try:
            await context.bot.send_photo(
                cid, w["photo_id"],
                caption=(
                    f"✨ A New **{rarity_txt}** SealWaifu💫 Appeared...\n\n"
                    f"*/hunt Character Name* and add in Your Sealwaifu Collection 👾"
                ),
                parse_mode="Markdown"
            )
            active_hunts[cid] = wid
        except Exception as e:
            print(f"Spawn error: {e}")


# ═══════════════════════════════════
#  /ChatOn  /ChatOff
# ═══════════════════════════════════
async def chaton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    chat_mode_users.add(u.id)
    await update.message.reply_text(
        f"💕 *Chat Mode ON!*\n\n"
        f"Hieee {u.first_name}-san~! 😊✨\n"
        f"I'm ready to talk with you!\n"
        f"Write anything and I'll reply~ 💖\n\n"
        f"To turn off: /ChatOff",
        parse_mode="Markdown"
    )

async def chatoff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    chat_mode_users.discard(u.id)
    await update.message.reply_text(
        f"💔 *Chat Mode OFF*\n\n"
        f"Aww {u.first_name}-san~ 🥺\n"
        f"Come back soon! I'll be waiting...\n"
        f"To turn on again: /ChatOn 💕",
        parse_mode="Markdown"
    )


# ═══════════════════════════════════
#  /broadcast  /bcast
# ═══════════════════════════════════
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    if not is_admin(u.id):
        await update.message.reply_text("❌ Only admins can use this command!")
        return
    msg = update.message.reply_to_message
    if not msg:
        await update.message.reply_text(
            "❌ **Reply** to a message/photo then use `/broadcast`!",
            parse_mode="Markdown"
        )
        return
    status = await update.message.reply_text("📡 Broadcast starting...")
    success = 0
    failed = 0
    targets = list(all_user_ids) + list(all_group_ids)
    for tid in targets:
        try:
            if msg.photo:
                await context.bot.send_photo(tid, msg.photo[-1].file_id, caption=msg.caption or "", parse_mode="Markdown")
            elif msg.text:
                await context.bot.send_message(tid, msg.text, parse_mode="Markdown")
            elif msg.sticker:
                await context.bot.send_sticker(tid, msg.sticker.file_id)
            elif msg.video:
                await context.bot.send_video(tid, msg.video.file_id, caption=msg.caption or "")
            elif msg.document:
                await context.bot.send_document(tid, msg.document.file_id, caption=msg.caption or "")
            success += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)
    await status.edit_text(
        f"✅ *Broadcast Complete!*\n\n"
        f"👥 Total Users: {len(all_user_ids)}\n"
        f"🌐 Total Groups: {len(all_group_ids)}\n"
        f"✅ Success: {success}\n"
        f"❌ Failed: {failed}",
        parse_mode="Markdown"
    )


# ═══════════════════════════════════
#  /hunt
# ═══════════════════════════════════
async def hunt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    u = update.effective_user
    if update.effective_chat.type == "private":
        await update.message.reply_text("❌ /hunt only works in groups!")
        return
    if cid not in active_hunts:
        await update.message.reply_text("🌸 No waifu right now! Send more messages.")
        return
    if not context.args:
        await update.message.reply_text("❌ `/hunt CharacterName`", parse_mode="Markdown")
        return
    guess = " ".join(context.args).lower().strip()
    wid = active_hunts[cid]
    w = waifus.get(wid)
    if not w:
        active_hunts.pop(cid, None)
        return
    if guess in w["name"].lower() or w["name"].lower() in guess:
        d = get_user(u.id, u.first_name)
        d["name"] = u.first_name
        d["harem"].append(wid)
        get_group(cid, update.effective_chat.title or "Group")["claimed"] += 1
        active_hunts.pop(cid)
        m = mention(u)
        await update.message.reply_text(
            f"🎉 {m} claimed **{w['name']}**!\n\n"
            f"| 🌸 ɴᴀᴍᴇ: {w['name']}\n"
            f"| 🎬 ᴀɴɪᴍᴇ: {w['anime']}\n"
            f"| 💎 ʀᴀʀɪᴛʏ: {RARITY.get(w['rarity'], '?')}\n"
            f"| 🎴 ᴄᴏʟʟᴇᴄᴛɪᴏɴ: {len(d['harem'])}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ Wrong guess! Try again.")


# ═══════════════════════════════════
#  /harem  (collection view only)
# ═══════════════════════════════════
async def harem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    d = get_user(u.id, u.first_name)
    total = len(d["harem"])

    caption = (
        f"╒═══「 🎴 COLLECTION 」\n"
        f"╰─➩ ᴜsᴇʀ: {u.first_name}\n"
        f"╰─➩ ᴛᴏᴛᴀʟ ᴡᴀɪғᴜ: {total}\n"
        f"╰─➩ ʀᴀɴᴋ: {get_rank(total)}\n"
        f"╰──────────────────"
    )

    markup = None
    if d["harem"]:
        markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("🎴 View Collection ➡️", callback_data=f"hr_{u.id}_0")
        ]])
    else:
        caption += "\n\n🎴 No waifus yet! Use /hunt to get one."

    try:
        photos = await context.bot.get_user_profile_photos(u.id, limit=1)
        if photos.total_count > 0:
            pid = photos.photos[0][-1].file_id
            await context.bot.send_photo(
                update.effective_chat.id, pid,
                caption=caption, reply_markup=markup, parse_mode="Markdown"
            )
            return
    except Exception:
        pass
    await update.message.reply_text(caption, reply_markup=markup, parse_mode="Markdown")


# ═══════════════════════════════════
#  /profile  (full stats with harem%)
# ═══════════════════════════════════
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    d = get_user(u.id, u.first_name)
    total = len(d["harem"])
    uniq = len(set(d["harem"]))
    db = len(waifus)
    pct = (uniq / db * 100) if db > 0 else 0
    bar = pbar(uniq, db)
    rank = get_rank(total)

    caption = (
        f"╒═══「 𝗨𝗦𝗘𝗥 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡 」\n"
        f"╰─➩ ᴜsᴇʀ: {u.first_name}\n"
        f"╰─➩ ᴜsᴇʀ ɪᴅ: {u.id}\n"
        f"╰─➩ ᴛᴏᴛᴀʟ ᴡᴀɪғᴜ: {total} ({uniq})\n"
        f"╰─➩ ʜᴀʀᴇᴍ: {uniq}/{db} ({pct:.3f}%)\n"
        f"╰─➩ ʀᴀɴᴋ: {rank}\n"
        f"╰─➩ ᴘʀᴏɢʀᴇss ʙᴀʀ: {bar}\n"
        f"╰─➩ ᴏɴᴇx: {d['onex']}\n"
        f"╰──────────────────"
    )

    try:
        photos = await context.bot.get_user_profile_photos(u.id, limit=1)
        if photos.total_count > 0:
            pid = photos.photos[0][-1].file_id
            await context.bot.send_photo(
                update.effective_chat.id, pid,
                caption=caption, parse_mode="Markdown"
            )
            return
    except Exception:
        pass
    await update.message.reply_text(caption, parse_mode="Markdown")


# ═══════════════════════════════════
#  HAREM COLLECTION CALLBACK
# ═══════════════════════════════════
async def harem_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    parts = q.data.split("_")
    uid, page = int(parts[1]), int(parts[2])
    if q.from_user.id != uid:
        await q.answer("Use your own /harem!", show_alert=True)
        return
    d = users.get(uid)
    if not d or not d["harem"]:
        return
    lst = d["harem"]
    total = len(lst)
    page = max(0, min(page, total - 1))
    wid = lst[page]
    w = waifus.get(wid, {})
    rtxt = RARITY.get(w.get("rarity", 1), "?")
    fav_txt = " 💝 **FAV**" if d.get("fav") == wid else ""
    cap = (
        f"🎴 **Waifu {page+1}/{total}**{fav_txt}\n\n"
        f"| 🌸 ɴᴀᴍᴇ: {w.get('name','?')}\n"
        f"| 🆔 ɪᴅ: {wid}\n"
        f"| 🎬 ᴀɴɪᴍᴇ: {w.get('anime','?')}\n"
        f"| 💎 ʀᴀʀɪᴛʏ: {rtxt}"
    )

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"hr_{uid}_{page-1}"))
    if page < total - 1:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"hr_{uid}_{page+1}"))

    share_btn = InlineKeyboardButton(
        "📤 Share to Group",
        switch_inline_query=f"waifu_{wid}"
    )

    rows = []
    if nav:
        rows.append(nav)
    rows.append([share_btn])
    markup = InlineKeyboardMarkup(rows)

    try:
        if w.get("photo_id"):
            await q.message.reply_photo(
                w["photo_id"], caption=cap, reply_markup=markup, parse_mode="Markdown"
            )
        else:
            await q.message.reply_text(cap, reply_markup=markup, parse_mode="Markdown")
    except Exception:
        pass
# ══════════════════════════════════════════════════════
#  GAME INFO CALLBACK
# ══════════════════════════════════════════════════════
async def game_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    text = (
        "╔══════════════════════╗\n"
        "       🎮 *SINZHU BOT GUIDE*\n"
        "╚══════════════════════╝\n\n"
      
       "━━━━━ 🌸 WAIFU BOT GUIDE ━━━━━\n\n"
        "📋 *How It Works:*\n"
        "➤ A waifu automatically spawns in the group after every 15 messages\n"
        "➤ Type `/hunt <name>` to claim the waifu before others\n"
        "➤ Earn Onex daily and use it to buy waifus from the shop\n"
        "➤ Build your collection and climb the global leaderboard\n\n"

        "🎴 *Collection Commands:*\n"
        "▸ `/hunt <name>` — Claim the spawned waifu\n"
        "▸ `/harem` — View your waifu collection\n"
        "▸ `/hclaim` — Claim a free daily waifu\n"
        "▸ `/fav <id>` — Set your favorite waifu\n"
        "▸ `/check <id>` — Check waifu details\n"
        "▸ `/wsell <id>` — Sell a waifu for Onex\n"
        "▸ `/gift <id>` — Gift a waifu to someone *(reply to their message)*\n\n"

        "💰 *Economy Commands:*\n"
        "▸ `/daily` — Claim daily Onex reward\n"
        "▸ `/welkin` — Claim daily Welkin reward\n"
        "▸ `/tesure` — Open treasure chest\n"
        "▸ `/onex` — Check your Onex balance\n"
        "▸ `/pay <amount>` — Transfer Onex *(reply to user)*\n"
        "▸ `/shop` — Browse the Waifu Shop\n\n"

        "🏅 *Rankings:*\n"
        "▸ `/rank` — View your current rank\n"
        "▸ `/wpass` — View your waifu rank card\n"
        "▸ `/top` — Top 10 waifu collectors\n"
        "▸ `/tops` — Top 10 richest users\n"
        "▸ `/topgroups` — Top 10 active groups\n\n"

        "💬 *Chat Commands:*\n"
        "▸ `/ChatOn` — Enable anime girlfriend chat mode\n"
        "▸ `/ChatOff` — Disable chat mode\n\n"

        "━━━━━━━━━━━━━━━━━━━━\n"
        "🌟 *Rarity Tiers (Highest → Lowest):*\n"
        "🌟 God Summon › ✨ Goddess › 🔮 Limited\n"
        "💎 Premium › 🎐 Special › 💮 Exclusive\n"
        "🪽 Celestial › 🟡 Legendary › 🟠 Rare\n"
        "🔵 Medium › 🟢 Common"
    )
    await q.message.reply_text(text, parse_mode="Markdown")

# ══════════════════════════════════════════════════════
#  MESSAGE HANDLER (waifu summon + chatbot)
# ══════════════════════════════════════════════════════
async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat:
        return
    if update.effective_chat.type == "private":
        u = update.effective_user
        if u and u.id in chat_mode_users:
            text = update.message.text or ""
            if text and not text.startswith("/"):
                response = get_chat_response(text)
                await update.message.reply_text(response)
        return
    cid = update.effective_chat.id
    get_group(cid, update.effective_chat.title or "Group")
    group_msg_count[cid] = group_msg_count.get(cid, 0) + 1
    interval = group_slavetime.get(cid, 15)
    if group_msg_count[cid] >= interval and waifus and cid not in active_hunts:
        group_msg_count[cid] = 0
        wid = random.choice(list(waifus.keys()))
        w = waifus[wid]
        try:
            await context.bot.send_photo(
                cid, w["photo_id"],
                caption=(
                    "🌸 **EK WAIFU AAYI HAI!** 🌸\n\n"
                    f"| 🎬 ᴀɴɪᴍᴇ: {w['anime']}\n"
                    f"| 💎 ʀᴀʀɪᴛʏ: {RARITY.get(w['rarity'], '?')}\n\n"
                    "🍀 `/hunt <character name>` likhke claim karo!"
                ),
                parse_mode="Markdown"
            )
            active_hunts[cid] = wid
        except Exception as e:
            print(f"Summon error: {e}")


# ══════════════════════════════════════════════════════
#  /ChatOn
# ══════════════════════════════════════════════════════
async def chaton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    chat_mode_users.add(u.id)
    await update.message.reply_text(
        f"💕 *Chat Mode ON!*\n\n"
        f"Hieee {u.first_name}-san~! 😊✨\n"
        f"Main tumhare saath baat karne ke liye taiyaar hoon!\n"
        f"Kuch bhi likho main jawab dungi~ 💖\n\n"
        f"Band karne ke liye: /ChatOff",
        parse_mode="Markdown"
    )

# ══════════════════════════════════════════════════════
#  /ChatOff
# ══════════════════════════════════════════════════════
async def chatoff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    chat_mode_users.discard(u.id)
    await update.message.reply_text(
        f"💔 *Chat Mode OFF*\n\n"
        f"Aww {u.first_name}-san~ 🥺\n"
        f"Dobara aana zaroor! Main wait karungi...\n"
        f"Wapas aane ke liye: /ChatOn 💕",
        parse_mode="Markdown"
    )


# ══════════════════════════════════════════════════════
#  /broadcast  /bcast
# ══════════════════════════════════════════════════════
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    if not is_admin(u.id):
        await update.message.reply_text("❌ Sirf admin use kar sakta hai!")
        return
    msg = update.message.reply_to_message
    if not msg:
        await update.message.reply_text(
            "❌ Kisi message/photo ko **reply** karo phir `/broadcast` likho!",
            parse_mode="Markdown"
        )
        return
    status = await update.message.reply_text("📡 Broadcast shuru ho raha hai...")
    success = 0
    failed = 0
    targets = list(all_user_ids) + list(all_group_ids)
    for tid in targets:
        try:
            if msg.photo:
                await context.bot.send_photo(tid, msg.photo[-1].file_id, caption=msg.caption or "", parse_mode="Markdown")
            elif msg.text:
                await context.bot.send_message(tid, msg.text, parse_mode="Markdown")
            elif msg.sticker:
                await context.bot.send_sticker(tid, msg.sticker.file_id)
            elif msg.video:
                await context.bot.send_video(tid, msg.video.file_id, caption=msg.caption or "")
            elif msg.document:
                await context.bot.send_document(tid, msg.document.file_id, caption=msg.caption or "")
            success += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)
    await status.edit_text(
        f"✅ *Broadcast Complete!*\n\n"
        f"👥 Total Users: {len(all_user_ids)}\n"
        f"🌐 Total Groups: {len(all_group_ids)}\n"
        f"✅ Success: {success}\n"
        f"❌ Failed: {failed}",
        parse_mode="Markdown"
    )


# ══════════════════════════════════════════════════════
#  /hunt
# ══════════════════════════════════════════════════════
async def hunt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    u = update.effective_user
    if update.effective_chat.type == "private":
        await update.message.reply_text("❌ /hunt sirf group mein kaam karta hai!")
        return
    if cid not in active_hunts:
        await update.message.reply_text("🌸 Abhi koi waifu nahi! Mazeed messages bhejo.")
        return
    if not context.args:
        await update.message.reply_text("❌ `/hunt CharacterName`", parse_mode="Markdown")
        return
    guess = " ".join(context.args).lower().strip()
    wid = active_hunts[cid]
    w = waifus.get(wid)
    if not w:
        active_hunts.pop(cid, None)
        return
    if guess in w["name"].lower() or w["name"].lower() in guess:
        d = get_user(u.id, u.first_name)
        d["name"] = u.first_name
        d["harem"].append(wid)
        get_group(cid, update.effective_chat.title or "Group")["claimed"] += 1
        active_hunts.pop(cid)
        m = f"[{u.first_name}](tg://user?id={u.id})"
        await update.message.reply_text(
            f"🎉 *{m} ne {w['name']} claim kiya!*\n\n"
            f"| 🌸 ɴᴀᴍᴇ: {w['name']}\n"
            f"| 🎬 ᴀɴɪᴍᴇ: {w['anime']}\n"
            f"| 💎 ʀᴀʀɪᴛʏ: {RARITY.get(w['rarity'], '?')}\n"
            f"| 🎴 ʜᴀʀᴇᴍ: {len(d['harem'])}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ Wrong guess! Try again.")


# ══════════════════════════════════════════════════════
#  /harem
# ══════════════════════════════════════════════════════
async def harem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    d = get_user(u.id, u.first_name)
    total = len(d["harem"])
    uniq = len(set(d["harem"]))
    db = len(waifus)
    pct = (uniq / db * 100) if db > 0 else 0
    bar = pbar(uniq, db)
    rank = get_rank(total)
    caption = (
        f"╒═══「 𝗨𝗦𝗘𝗥 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡 」\n"
        f"╰─➩ ᴜsᴇʀ: {u.first_name}\n"
        f"╰─➩ ᴜsᴇʀ ɪᴅ: {u.id}\n"
        f"╰─➩ ᴛᴏᴛᴀʟ ᴡᴀɪғᴜ: {total} ({uniq})\n"
        f"╰─➩ ʜᴀʀᴇᴍ: {uniq}/{db} ({pct:.3f}%)\n"
        f"╰─➩ ʀᴀɴᴋ: {rank}\n"
        f"╰─➩ ᴘʀᴏɢʀᴇss ʙᴀʀ: {bar}\n"
        f"╰──────────────────"
    )
    markup = None
    if d["harem"]:
        markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("🎴 View Collection ➡️", callback_data=f"hr_{u.id}_0")
        ]])
    else:
        caption += "\n\n🎴 Koi waifu nahi! /hunt karo."
    try:
        photos = await context.bot.get_user_profile_photos(u.id, limit=1)
        if photos.total_count > 0:
            pid = photos.photos[0][-1].file_id
            await context.bot.send_photo(
                update.effective_chat.id, pid,
                caption=caption, reply_markup=markup, parse_mode="Markdown"
            )
            return
    except Exception:
        pass
    await update.message.reply_text(caption, reply_markup=markup, parse_mode="Markdown")

async def harem_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    parts = q.data.split("_")
    uid, page = int(parts[1]), int(parts[2])
    if q.from_user.id != uid:
        await q.answer("Apna /harem use karo!", show_alert=True)
        return
    d = users.get(uid)
    if not d or not d["harem"]:
        return
    lst = d["harem"]
    total = len(lst)
    page = max(0, min(page, total - 1))
    wid = lst[page]
    w = waifus.get(wid, {})
    rtxt = RARITY.get(w.get("rarity", 1), "?")
    fav_txt = " 💝 **FAV**" if d.get("fav") == wid else ""
    cap = (
        f"🎴 **Waifu {page+1}/{total}**{fav_txt}\n\n"
        f"| 🌸 ɴᴀᴍᴇ: {w.get('name','?')}\n"
        f"| 🆔 ɪᴅ: {wid}\n"
        f"| 🎬 ᴀɴɪᴍᴇ: {w.get('anime','?')}\n"
        f"| 💎 ʀᴀʀɪᴛʏ: {rtxt}"
    )
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"hr_{uid}_{page-1}"))
    if page < total - 1:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"hr_{uid}_{page+1}"))
    markup = InlineKeyboardMarkup([nav]) if nav else None
    try:
        if w.get("photo_id"):
            await q.message.reply_photo(
                w["photo_id"], caption=cap, reply_markup=markup, parse_mode="Markdown"
            )
        else:
            await q.message.reply_text(cap, reply_markup=markup, parse_mode="Markdown")
    except Exception:
        pass

# ══════════════════════════════════════════════════════
#  /fav
# ══════════════════════════════════════════════════════
async def fav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    d = get_user(u.id, u.first_name)
    if not context.args:
        await update.message.reply_text("❌ `/fav <waifu_id>`", parse_mode="Markdown")
        return
    try:
        wid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Valid ID daalo!")
        return
    if wid not in d["harem"]:
        await update.message.reply_text("❌ Yeh waifu tumhare paas nahi!")
        return
    d["fav"] = wid
    w = waifus.get(wid, {})
    await update.message.reply_text(f"💝 *{w.get('name','?')}* favorite set!", parse_mode="Markdown")


# ══════════════════════════════════════════════════════
#  /wpass / /wpss
# ══════════════════════════════════════════════════════
async def wpass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    d = get_user(u.id, u.first_name)
    total = len(d["harem"])
    rank = get_rank(total)
    nxt = ""
    for t, name in RANKS:
        if total < t:
            nxt = f"╰─➩ ɴᴇxᴛ: {name} ({t - total} more)\n"
            break
    await update.message.reply_text(
        f"🦁 **WAIFU PASS**\n\n"
        f"╒═══「 {u.first_name} 」\n"
        f"╰─➩ ʀᴀɴᴋ: {rank}\n"
        f"╰─➩ ᴛᴏᴛᴀʟ: {total}\n"
        f"╰─➩ ᴏɴᴇx: {d['onex']}\n"
        f"╰─➩ ᴡᴇʟᴋɪɴ: {d['welkin']}\n"
        f"{nxt}"
        f"╰──────────────────\n\n"
        f"🎀 **RARITY (High → Low):**\n"
        f"¹ 🌟 God Summon\n² 🎀 Only Shop\n³ 🔮 Limited\n"
        f"⁴ 💎 Premium\n⁵ 🎐 Special\n⁶ 💮 Exclusive\n"
        f"⁷ 🪽 Celestial\n⁸ 🟡 Legendary\n⁹ 🟠 Rare\n"
        f"¹⁰ 🔵 Medium\n¹² 🟢 Common",
        parse_mode="Markdown"
    )


# ══════════════════════════════════════════════════════
#  /shop
# ══════════════════════════════════════════════════════
async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    av = [(wid, info) for wid, info in shop_list.items() if info["qty"] > 0]
    if not av:
        await update.message.reply_text("🛍️ Shop khaali hai!")
        return
    await _shop_send(update.effective_chat.id, uid, 0, context)

async def _shop_send(chat_id, uid, page, context):
    av = [(wid, info) for wid, info in shop_list.items() if info["qty"] > 0]
    if not av or page >= len(av):
        return
    wid, si = av[page]
    w = waifus.get(wid, {})
    rtxt = RARITY.get(w.get("rarity", 1), "?")
    cap = (
        f"╭── 𝐒ʜᴏᴘ ⁻ 𝐖ᴀɪꜰᴜ 𝐒ʜᴏᴘ\n"
        f" | ⤇ 🌸 ɴᴀᴍᴇ: {w.get('name','?')}\n"
        f" | ⤇ 🆔 ɪᴅ: {wid}\n"
        f" | ⤇ 🎬 ᴀɴɪᴍᴇ: {w.get('anime','?')}\n"
        f" | ⤇ 💎 ʀᴀʀɪᴛʏ: {rtxt}\n"
        f"▰▱▱▱▱▱▱▱▱▱▰\n"
        f"📦 ᴀᴠᴀɪʟᴀʙʟᴇ: {si['qty']}\n\n"
        f"| 💰 ᴘʀɪᴄᴇ: {si['price']} Onex"
    )
    btns = [[InlineKeyboardButton("🛒 Buy", callback_data=f"sbuy_{uid}_{wid}_{page}")]]
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"snav_{uid}_{page-1}"))
    if page < len(av) - 1:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"snav_{uid}_{page+1}"))
    if nav:
        btns.append(nav)
    mk = InlineKeyboardMarkup(btns)
    try:
        if w.get("photo_id"):
            await context.bot.send_photo(chat_id, w["photo_id"], caption=cap, reply_markup=mk, parse_mode="Markdown")
        else:
            await context.bot.send_message(chat_id, cap, reply_markup=mk, parse_mode="Markdown")
    except Exception as e:
        print(f"Shop error: {e}")


async def shop_nav_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    _, uid_s, page_s = q.data.split("_")
    uid, page = int(uid_s), int(page_s)
    if q.from_user.id != uid:
        await q.answer("Apni /shop use karo!", show_alert=True)
        return
    av = [(wid, info) for wid, info in shop_list.items() if info["qty"] > 0]
    if not av or page >= len(av):
        return
    wid, si = av[page]
    w = waifus.get(wid, {})
    rtxt = RARITY.get(w.get("rarity", 1), "?")
    cap = (
        f"╭── 𝐒ʜᴏᴘ ⁻ 𝐖ᴀɪꜰᴜ 𝐒ʜᴏᴘ\n"
        f" | ⤇ 🌸 ɴᴀᴍᴇ: {w.get('name','?')}\n"
        f" | ⤇ 🆔 ɪᴅ: {wid}\n"
        f" | ⤇ 🎬 ᴀɴɪᴍᴇ: {w.get('anime','?')}\n"
        f" | ⤇ 💎 ʀᴀʀɪᴛʏ: {rtxt}\n"
        f"▰▱▱▱▱▱▱▱▱▱▰\n"
        f"📦 ᴀᴠᴀɪʟᴀʙʟᴇ: {si['qty']}\n\n"
        f"| 💰 ᴘʀɪᴄᴇ: {si['price']} Onex"
    )
    btns = [[InlineKeyboardButton("🛒 Buy", callback_data=f"sbuy_{uid}_{wid}_{page}")]]
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"snav_{uid}_{page-1}"))
    if page < len(av) - 1:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"snav_{uid}_{page+1}"))
    if nav:
        btns.append(nav)
    mk = InlineKeyboardMarkup(btns)
    try:
        if w.get("photo_id"):
            await q.message.edit_caption(cap, reply_markup=mk, parse_mode="Markdown")
        else:
            await q.message.edit_text(cap, reply_markup=mk, parse_mode="Markdown")
    except Exception:
        pass


async def shop_buy_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    parts = q.data.split("_")
    uid, wid, page = int(parts[1]), int(parts[2]), int(parts[3])
    if q.from_user.id != uid:
        await q.answer("Apni /shop use karo!", show_alert=True)
        return
    d = get_user(uid)
    if wid not in shop_list or shop_list[wid]["qty"] <= 0:
        await q.answer("❌ Sold out!", show_alert=True)
        return
    price = shop_list[wid]["price"]
    if d["onex"] < price:
        await q.answer(f"❌ Onex kam! {price} chahiye, paas {d['onex']}", show_alert=True)
        return
    d["onex"] -= price
    d["harem"].append(wid)
    shop_list[wid]["qty"] -= 1
    w = waifus.get(wid, {})
    await q.message.reply_text(
        f"✅ *{w.get('name','?')}* khareed liya!\n💰 Baaki: {d['onex']} Onex",
        parse_mode="Markdown"
    )


# ══ /gift ══
async def gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    d = get_user(u.id, u.first_name)
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Kisi ke message ko reply karo + `/gift <id>`", parse_mode="Markdown")
        return
    if not context.args:
        await update.message.reply_text("❌ `/gift <waifu_id>`", parse_mode="Markdown")
        return
    try:
        wid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Valid ID!")
        return
    if wid not in d["harem"]:
        await update.message.reply_text("❌ Yeh waifu tumhare paas nahi!")
        return
    t = update.message.reply_to_message.from_user
    if t.id == u.id:
        await update.message.reply_text("❌ Khud ko nahi!")
        return
    td = get_user(t.id, t.first_name)
    d["harem"].remove(wid)
    td["harem"].append(wid)
    if d.get("fav") == wid:
        d["fav"] = None
    w = waifus.get(wid, {})
    mf = f"[{u.first_name}](tg://user?id={u.id})"
    mt = f"[{t.first_name}](tg://user?id={t.id})"
    await update.message.reply_text(
        f"🎁 {mf} ne {mt} ko *{w.get('name','?')}* gift diya!", parse_mode="Markdown"
    )


# ══ /rank ══
async def rank_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    d = get_user(u.id, u.first_name)
    total = len(d["harem"])
    rank = get_rank(total)
    nxt = ""
    for t, name in RANKS:
        if total < t:
            nxt = f"🎯 Next: **{name}** ({t - total} more)"
            break
    await update.message.reply_text(
        f"🐲 **Rank**\n\n👤 {u.first_name}\n🏅 {rank}\n🎴 Waifus: {total}\n{nxt}",
        parse_mode="Markdown"
    )


# ══ /hclaim ══
async def hclaim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    d = get_user(u.id, u.first_name)
    today = str(date.today())
    if d["hclaim"] == today:
        await update.message.reply_text("🎀 Aaj ka waifu le liya! Kal aana.")
        return
    if not waifus:
        await update.message.reply_text("❌ Database khaali!")
        return
    cw = [wid for wid, w in waifus.items() if w["rarity"] <= 3]
    wid = random.choice(cw if cw else list(waifus.keys()))
    w = waifus[wid]
    d["harem"].append(wid)
    d["hclaim"] = today
    m = f"[{u.first_name}](tg://user?id={u.id})"
    try:
        await context.bot.send_photo(
            update.effective_chat.id, w["photo_id"],
            caption=(
                f"🎀 *Daily Waifu Claim!*\n\n"
                f"| 🌸 ɴᴀᴍᴇ: {w['name']}\n"
                f"| 🎬 ᴀɴɪᴍᴇ: {w['anime']}\n"
                f"| 💎 ʀᴀʀɪᴛʏ: {RARITY.get(w['rarity'],'?')}\n\n"
                f"🎉 {m} ne claim kiya!"
            ),
            parse_mode="Markdown"
        )
    except Exception:
        await update.message.reply_text(f"🎀 *{w['name']}* mili! {m}", parse_mode="Markdown")


# ══ /top ══
async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not users:
        await update.message.reply_text("Koi user nahi!")
        return
    sl = sorted(users.items(), key=lambda x: len(x[1]["harem"]), reverse=True)[:10]
    medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
    text = "🏆 **Top 10 Waifu Collectors**\n\n"
    for i, (uid, d) in enumerate(sl):
        text += f"{medals[i]} **{d['name']}** — {len(d['harem'])} | {get_rank(len(d['harem']))}\n"
    await update.message.reply_text(text, parse_mode="Markdown")


# ══ /topgroups ══
async def topgroups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not groups:
        await update.message.reply_text("Koi group data nahi!")
        return
    sl = sorted(groups.items(), key=lambda x: x[1]["claimed"], reverse=True)[:10]
    medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
    text = "🌐 **Top 10 Groups**\n\n"
    for i, (gid, g) in enumerate(sl):
        text += f"{medals[i]} **{g['name']}** — {g['claimed']} claimed\n"
    await update.message.reply_text(text, parse_mode="Markdown")


# ══ /onex ══
async def onex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    d = get_user(u.id, u.first_name)
    await update.message.reply_text(
        f"💸 **Onex Balance**\n\n👤 {u.first_name}\n💰 Onex: {d['onex']}\n🥇 Welkin: {d['welkin']}",
        parse_mode="Markdown"
    )


# ══ /check ══
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ `/check <waifu_id>`", parse_mode="Markdown")
        return
    try:
        wid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Valid ID!")
        return
    if wid not in waifus:
        await update.message.reply_text(f"❌ ID {wid} nahi mila!")
        return
    w = waifus[wid]
    rtxt = RARITY.get(w["rarity"], "?")
    owners = sum(1 for d in users.values() if wid in d["harem"])
    cap = (
        f"🔎 **Character Info**\n\n"
        f"| 🌸 ɴᴀᴍᴇ: {w['name']}\n"
        f"| 🆔 ɪᴅ: {wid}\n"
        f"| 🎬 ᴀɴɪᴍᴇ: {w['anime']}\n"
        f"| 💎 ʀᴀʀɪᴛʏ: {rtxt}\n"
        f"| 👥 ᴏᴡɴᴇʀs: {owners}"
)
    try:
        await context.bot.send_photo(update.effective_chat.id, w["photo_id"], caption=cap, parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(cap, parse_mode="Markdown")


# ══ /wsell ══
async def wsell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    d = get_user(u.id, u.first_name)
    if not context.args:
        await update.message.reply_text("❌ `/wsell <waifu_id>`", parse_mode="Markdown")
        return
    try:
        wid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Valid ID!")
        return
    if wid not in d["harem"]:
        await update.message.reply_text("❌ Yeh waifu tumhare paas nahi!")
        return
    w = waifus.get(wid, {})
    price = SELL_PRICE.get(w.get("rarity", 1), 50)
    d["harem"].remove(wid)
    d["onex"] += price
    if d.get("fav") == wid:
        d["fav"] = None
    await update.message.reply_text(
        f"💶 *{w.get('name','?')}* bech diya!\n+{price} Onex\n💰 Total: {d['onex']}",
        parse_mode="Markdown"
    )


# ══ /daily ══
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    d = get_user(u.id, u.first_name)
    today = str(date.today())
    if d["daily"] == today:
        await update.message.reply_text("💎 Aaj ke Onex le liye! Kal aana.")
        return
    n = random.randint(100, 500)
    d["onex"] += n
    d["daily"] = today
    await update.message.reply_text(
        f"💎 *Daily Onex!*\n\n+{n} Onex\n💰 Total: {d['onex']}", parse_mode="Markdown"
    )


# ══ /pay ══
async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    d = get_user(u.id, u.first_name)
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply karo + `/pay <amount>`", parse_mode="Markdown")
        return
    if not context.args:
        await update.message.reply_text("❌ `/pay <amount>`", parse_mode="Markdown")
        return
    try:
        n = int(context.args[0])
        if n <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Valid amount!")
        return
    if d["onex"] < n:
        await update.message.reply_text(f"❌ Onex kam! Tumhare paas {d['onex']}.")
        return
    t = update.message.reply_to_message.from_user
    if t.id == u.id:
        await update.message.reply_text("❌ Khud ko nahi!")
        return
    td = get_user(t.id, t.first_name)
    d["onex"] -= n
    td["onex"] += n
    mf = f"[{u.first_name}](tg://user?id={u.id})"
    mt = f"[{t.first_name}](tg://user?id={t.id})"
    await update.message.reply_text(
        f"💰 {mf} → {mt}: {n} Onex\n💳 Tumhara: {d['onex']}", parse_mode="Markdown"
    )


# ══ /welkin ══
async def welkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    d = get_user(u.id, u.first_name)
    today = str(date.today())
    if d["welkin_d"] == today:
        await update.message.reply_text("🗓 Aaj ka welkin le liya! Kal aana.")
        return
    n = random.randint(50, 150)
    d["onex"] += n
    d["welkin"] += 1
    d["welkin_d"] = today
    await update.message.reply_text(
        f"🗓 *Welkin!*\n\n+{n} Onex\n+1 Welkin\n💰 Total: {d['onex']}", parse_mode="Markdown"
    )


# ══ /tesure ══
async def tesure(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    d = get_user(u.id, u.first_name)
    today = str(date.today())
    if d["tesure"] == today:
        await update.message.reply_text("🪅 Aaj ka treasure le liya! Kal aana.")
        return
    d["tesure"] = today
    if random.random() < 0.1 and waifus:
        wid = random.choice(list(waifus.keys()))
        w = waifus[wid]
        d["harem"].append(wid)
        await update.message.reply_text(
            f"🪅 *Treasure!*\n\n🎉 Lucky! Free Waifu!\n🌸 {w['name']}", parse_mode="Markdown"
        )
        return
    n = random.randint(200, 1000)
    d["onex"] += n
    await update.message.reply_text(
        f"🪅 *Treasure!*\n\n+{n} Onex\n💰 Total: {d['onex']}", parse_mode="Markdown"
    )


# ══ /tops ══
async def tops(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not users:
        await update.message.reply_text("Koi user nahi!")
        return
    sl = sorted(users.items(), key=lambda x: x[1]["onex"], reverse=True)[:10]
    medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
    text = "🥇 **Top 10 Onex Users**\n\n"
    for i, (uid, d) in enumerate(sl):
        text += f"{medals[i]} **{d['name']}** — {d['onex']} Onex\n"
    await update.message.reply_text(text, parse_mode="Markdown")


# ══ /slavetime ══
async def slavetime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    cid = update.effective_chat.id
    if not is_admin(u.id):
        await update.message.reply_text("❌ Sirf admin/sudo use kar sakta hai!")
        return
    if not context.args:
        cur = group_slavetime.get(cid, 15)
        await update.message.reply_text(
            f"🐣 Current: **{cur} messages**\nChange: `/slavetime 20`", parse_mode="Markdown"
        )
        return
    try:
        n = int(context.args[0])
        if n < 15:
            await update.message.reply_text("❌ Minimum 15!")
            return
    except ValueError:
        await update.message.reply_text("❌ Number daalo!")
        return
    group_slavetime[cid] = n
    await update.message.reply_text(
        f"🐣 Summon interval: **{n} messages** set ho gaya!", parse_mode="Markdown"
    )


# ══ ADMIN: /upload ══
async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global next_waifu_id
    u = update.effective_user
    if not is_admin(u.id):
        await update.message.reply_text("❌ Sirf admin use kar sakta hai!")
        return
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text(
            "❌ *Wrong format!*\n\nKisi *photo* ko reply karo:\n"
            "`/upload muzan-kibutsuji Demon-slayer 3`\n\n"
            "Rarity: 1🟢 2🔵 3🟠 4🟡 5🪽 6💮 7🎐 8💎 9🔮 10🔖 11✨ 12🌟",
            parse_mode="Markdown"
        )
        return
    if len(context.args) < 3:
        await update.message.reply_text("❌ `/upload character-name anime-name rarity`", parse_mode="Markdown")
        return
    try:
        rarity = int(context.args[-1])
        if not 1 <= rarity <= 12:
            raise ValueError
        anime = context.args[-2].replace("-", " ").title()
        name = " ".join(context.args[:-2]).replace("-", " ").title()
    except ValueError:
        await update.message.reply_text("❌ Rarity 1-12 ke beech honi chahiye!")
        return
    photo_id = update.message.reply_to_message.photo[-1].file_id
    wid = next_waifu_id
    next_waifu_id += 1
    waifus[wid] = {"name": name, "anime": anime, "rarity": rarity, "photo_id": photo_id}
    await update.message.reply_text(
        f"✅ *Waifu uploaded!*\n\n"
        f"| 🌸 ɴᴀᴍᴇ: {name}\n| 🆔 ɪᴅ: {wid}\n"
        f"| 🎬 ᴀɴɪᴍᴇ: {anime}\n| 💎 ʀᴀʀɪᴛʏ: {RARITY.get(rarity,'?')}",
        parse_mode="Markdown"
    )


# ══ ADMIN: /deleteWaifu ══
async def delete_waifu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    if not is_admin(u.id):
        await update.message.reply_text("❌ Sirf admin use kar sakta hai!")
        return
    if not context.args:
        await update.message.reply_text("❌ `/deleteWaifu <id>`", parse_mode="Markdown")
        return
    try:
        wid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Valid ID!")
        return
    if wid not in waifus:
        await update.message.reply_text(f"❌ ID {wid} nahi mila!")
        return
    name = waifus[wid]["name"]
    del waifus[wid]
    for d in users.values():
        d["harem"] = [x for x in d["harem"] if x != wid]
        if d.get("fav") == wid:
            d["fav"] = None
    shop_list.pop(wid, None)
    await update.message.reply_text(f"🗑️ *{name}* (ID: {wid}) delete ho gaya!", parse_mode="Markdown")


# ══ ADMIN: /addSudo ══
async def add_sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    if u.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Sirf main admin use kar sakta hai!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Kisi ke message ko reply karo!")
        return
    t = update.message.reply_to_message.from_user
    sudo_users.add(t.id)
    await update.message.reply_text(f"✅ *{t.first_name}* sudo ban gaya!", parse_mode="Markdown")


# ══ ADMIN: /addsh ══
async def addsh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    if not is_admin(u.id):
        await update.message.reply_text("❌ Sirf admin use kar sakta hai!")
        return
    if len(context.args) != 3:
        await update.message.reply_text(
            "❌ `/addsh <waifu_id> <price> <quantity>`\nExample: `/addsh 296 50000 100`",
            parse_mode="Markdown"
        )
        return
    try:
        wid, price, qty = int(context.args[0]), int(context.args[1]), int(context.args[2])
    except ValueError:
        await update.message.reply_text("❌ Sahi numbers daalo!")
        return
    if wid not in waifus:
        await update.message.reply_text(f"❌ ID {wid} ka waifu nahi!")
        return
    shop_list[wid] = {"price": price, "qty": qty}
    w = waifus[wid]
    await update.message.reply_text(
        f"✅ *{w['name']}* shop mein add!\n\n| 💰 Price: {price} Onex\n| 📦 Qty: {qty}",
        parse_mode="Markdown"
    )


# ══ ADMIN: /Rshop ══
async def rshop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    if not is_admin(u.id):
        await update.message.reply_text("❌ Sirf admin use kar sakta hai!")
        return
    if not context.args:
        await update.message.reply_text("❌ `/Rshop <waifu_id>`", parse_mode="Markdown")
        return
    try:
        wid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Valid ID!")
        return
    if wid not in shop_list:
        await update.message.reply_text(f"❌ ID {wid} shop mein nahi!")
        return
    del shop_list[wid]
    w = waifus.get(wid, {})
    await update.message.reply_text(
        f"🗑️ *{w.get('name', str(wid))}* shop se remove ho gaya!", parse_mode="Markdown"
    )


# ══ ADMIN: /setphoto ══
async def setphoto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    if not is_admin(u.id):
        await update.message.reply_text("❌ Sirf admin use kar sakta hai!")
        return
    if not context.args:
        await update.message.reply_text(
            f"📷 Current:\n`{bot_settings['photo']}`\n\nChange: `/setphoto <url>`",
            parse_mode="Markdown"
        )
        return
    bot_settings["photo"] = context.args[0]
    await update.message.reply_text("✅ Start photo change ho gaya!")


# ══ ADMIN: /setcaption ══
async def setcaption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    if not is_admin(u.id):
        await update.message.reply_text("❌ Sirf admin use kar sakta hai!")
        return
    if not context.args:
        await update.message.reply_text(
            "⚠️ `/setcaption Naya caption {name} se`",
            parse_mode="Markdown"
        )
        return
    bot_settings["caption"] = " ".join(context.args)
    await update.message.reply_text("✅ Caption change ho gaya!")


# ══ ADMIN: /setlink ══
async def setlink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    if not is_admin(u.id):
        await update.message.reply_text("❌ Sirf admin use kar sakta hai!")
        return
    keys = {"group": "link_group", "owner": "link_owner", "channel": "link_channel", "kidnap": "link_kidnap"}
    if len(context.args) < 2:
        current = "\n".join([f"`{k}` → {bot_settings[v]}" for k, v in keys.items()])
        await update.message.reply_text(
            f"🔗 *Current Links:*\n\n{current}\n\n"
            "Change: `/setlink group https://t.me/...`",
            parse_mode="Markdown"
        )
        return
    btn_name = context.args[0].lower()
    if btn_name not in keys:
        await update.message.reply_text("❌ Valid: `group` `owner` `channel` `kidnap`", parse_mode="Markdown")
        return
    bot_settings[keys[btn_name]] = context.args[1]
    await update.message.reply_text(f"✅ `{btn_name}` link update ho gaya!", parse_mode="Markdown")


# ══ ADMIN: /addOnex ══
async def add_onex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    if not is_admin(u.id):
        await update.message.reply_text("❌ Sirf admin!")
        return
    if not update.message.reply_to_message or not context.args:
        await update.message.reply_text("❌ Reply karo + `/addOnex <amount>`", parse_mode="Markdown")
        return
    try:
        n = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Valid number!")
        return
    t = update.message.reply_to_message.from_user
    td = get_user(t.id, t.first_name)
    td["onex"] += n
    await update.message.reply_text(
        f"✅ *{t.first_name}* ko {n} Onex diya! Total: {td['onex']}", parse_mode="Markdown"
    )


# ══ ADMIN: /removeOnex ══
async def remove_onex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    if not is_admin(u.id):
        await update.message.reply_text("❌ Sirf admin!")
        return
    if not update.message.reply_to_message or not context.args:
        await update.message.reply_text("❌ Reply karo + `/removeOnex <amount>`", parse_mode="Markdown")
        return
    try:
        n = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Valid number!")
        return
    t = update.message.reply_to_message.from_user
    td = get_user(t.id, t.first_name)
    td["onex"] = max(0, td["onex"] - n)
    await update.message.reply_text(
        f"✅ *{t.first_name}* se {n} Onex hataya! Total: {td['onex']}", parse_mode="Markdown"
    )


# ══ APP BUILD ══
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start",       start))
app.add_handler(CommandHandler("hunt",        hunt))
app.add_handler(CommandHandler("fav",         fav))
app.add_handler(CommandHandler("harem",       harem))
app.add_handler(CommandHandler("wpass",       wpass))
app.add_handler(CommandHandler("wpss",        wpass))
app.add_handler(CommandHandler("shop",        shop))
app.add_handler(CommandHandler("gift",        gift))
app.add_handler(CommandHandler("rank",        rank_cmd))
app.add_handler(CommandHandler("hclaim",      hclaim))
app.add_handler(CommandHandler("top",         top))
app.add_handler(CommandHandler("topgroups",   topgroups))
app.add_handler(CommandHandler("onex",        onex))
app.add_handler(CommandHandler("check",       check))
app.add_handler(CommandHandler("wsell",       wsell))
app.add_handler(CommandHandler("daily",       daily))
app.add_handler(CommandHandler("pay",         pay))
app.add_handler(CommandHandler("welkin",      welkin))
app.add_handler(CommandHandler("tesure",      tesure))
app.add_handler(CommandHandler("tops",        tops))
app.add_handler(CommandHandler("slavetime",   slavetime))
app.add_handler(CommandHandler("ChatOn",      chaton))
app.add_handler(CommandHandler("chaton",      chaton))
app.add_handler(CommandHandler("ChatOff",     chatoff))
app.add_handler(CommandHandler("chatoff",     chatoff))
app.add_handler(CommandHandler("broadcast",   broadcast))
app.add_handler(CommandHandler("bcast",       broadcast))
app.add_handler(CommandHandler("upload",      upload))
app.add_handler(CommandHandler("deleteWaifu", delete_waifu))
app.add_handler(CommandHandler("addSudo",     add_sudo))
app.add_handler(CommandHandler("addsh",       addsh))
app.add_handler(CommandHandler("Rshop",       rshop))
app.add_handler(CommandHandler("setphoto",    setphoto))
app.add_handler(CommandHandler("setcaption",  setcaption))
app.add_handler(CommandHandler("setlink",     setlink))
app.add_handler(CommandHandler("addOnex",     add_onex))
app.add_handler(CommandHandler("removeOnex",  remove_onex))
app.add_handler(CallbackQueryHandler(harem_cb,    pattern=r"^hr_"))
app.add_handler(CallbackQueryHandler(shop_nav_cb, pattern=r"^snav_"))
app.add_handler(CallbackQueryHandler(shop_buy_cb, pattern=r"^sbuy_"))
app.add_handler(CallbackQueryHandler(game_info,   pattern="^game_info$"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

print("✅ Sinzhu Waifu Bot chal raha hai...")
app.run_polling()
    
