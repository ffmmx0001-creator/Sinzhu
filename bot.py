import os
import random
import math
import asyncio
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import database as db
from keyboards import main_menu_keyboard, harem_keyboard, waifu_detail_keyboard, sell_confirm_keyboard, shop_keyboard, buy_confirm_keyboard, admin_panel_keyboard, top_keyboard, rank_keyboard
import admin as adm
from waifu_data import RARITY_TIERS

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "123456789").split(",")]
WAIFU_PER_PAGE = 6
ANIME_REPLIES = [
    "Kawaii! 🌸 Aapne kya kaha? ~",
    "Hmm~ mujhe samajh nahi aaya! 😊",
    "Wah! Bahut interesting! ✨",
    "Eto ne~ aisa kyun bol rahe ho? 💕",
    "Sugoi desu ne! 🎌",
    "Mou~ don't tease me! 🥺",
    "Nani?! That's amazing! 🎆",
]


def get_display_name(user):
    return f"@{user.username}" if user.username else user.first_name


def paginate(items, page, per_page):
    total = math.ceil(len(items) / per_page) if items else 1
    start = (page - 1) * per_page
    return items[start:start + per_page], total


async def spawn_waifu(context, chat_id):
    waifus = db.get_all_waifus()
    if not waifus:
        return
    weights = [RARITY_TIERS.get(w["rarity"], {}).get("weight", 50) for w in waifus]
    chosen = random.choices(waifus, weights=weights, k=1)[0]
    db.update_group(chat_id, current_waifu_id=chosen["id"], current_waifu_claimed=0)
    caption = (
        f"✨ **A Wild Waifu Appeared!** ✨\n\n"
        f"🎴 **{chosen['name']}**\n"
        f"📺 Anime: {chosen['anime']}\n"
        f"⭐ Rarity: {chosen['rarity']}\n\n"
        f"🏹 Type `/hunt {chosen['name']}` to claim her!"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🏹 Hunt {chosen['name']}", callback_data=f"quick_hunt_{chosen['id']}")]
    ])
    try:
        if chosen.get("image_url"):
            await context.bot.send_photo(chat_id=chat_id, photo=chosen["image_url"], caption=caption, reply_markup=keyboard, parse_mode="Markdown")
        else:
            await context.bot.send_message(chat_id=chat_id, text=caption, reply_markup=keyboard, parse_mode="Markdown")
    except Exception as e:
        print(f"Spawn error: {e}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.get_user(user.id, user.username, user.first_name)
    welcome = (
        f"🌸 **Welcome, {user.first_name}!**\n\n"
        "I'm **Sinzhu Waifu Bot** 🎴\n\n"
        "╔══════════════════════╗\n"
        "       🎮 SINZHU BOT GUIDE\n"
        "╚══════════════════════╝\n\n"
        "🌟 Rarity: God Summon › Goddess › Limited\n"
        "💎 Premium › Special › Exclusive › Celestial\n"
        "🟡 Legendary › 🟠 Rare › 🔵 Medium › 🟢 Common\n\n"
        "Choose an option below! 👇"
    )
    await update.message.reply_text(welcome, reply_markup=main_menu_keyboard(), parse_mode="Markdown")


async def hunt_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.message.reply_text("❌ Hunt only works in group chats!")
        return
    user = update.effective_user
    args = context.args
    if not args:
        await update.message.reply_text("Usage: `/hunt <waifu name>`", parse_mode="Markdown")
        return
    name = " ".join(args).strip()
    group = db.get_group(update.effective_chat.id)
    if not group["current_waifu_id"]:
        await update.message.reply_text("😴 No waifu has spawned yet!")
        return
    if group["current_waifu_claimed"]:
        await update.message.reply_text("💨 Too slow! Already claimed.")
        return
    conn = db.get_conn()
    waifu = conn.execute("SELECT * FROM waifus WHERE id=?", (group["current_waifu_id"],)).fetchone()
    conn.close()
    if not waifu:
        await update.message.reply_text("❌ Waifu not found.")
        return
    if name.lower() != waifu["name"].lower():
        await update.message.reply_text(f"❌ Wrong name! Hint: starts with **{waifu['name'][0]}**...", parse_mode="Markdown")
        return
    db.update_group(update.effective_chat.id, current_waifu_claimed=1)
    db.get_user(user.id, user.username, user.first_name)
    db.give_waifu_to_user(user.id, waifu["id"])
    bonus_onex = RARITY_TIERS.get(waifu["rarity"], {}).get("sell_price", 50) // 5
    db.update_user(user.id, onex=db.get_user(user.id)["onex"] + bonus_onex)
    text = (
        f"🎉 **{get_display_name(user)} caught {waifu['name']}!**\n\n"
        f"⭐ {waifu['rarity']}\n📺 {waifu['anime']}\n💰 +{bonus_onex} Onex"
    )
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🎴 View Harem", callback_data="harem_1"),
        InlineKeyboardButton("💰 Balance", callback_data="balance"),
    ]])
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")


async def harem_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.get_user(user.id, user.username, user.first_name)
    waifus = db.get_user_waifus(user.id)
    if not waifus:
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]])
        await update.message.reply_text("💔 Your harem is empty! Hunt waifus in a group!", reply_markup=kb)
        return
    page = 1
    chunk, total_pages = paginate(waifus, page, WAIFU_PER_PAGE)
    u_data = db.get_user(user.id)
    text = f"🎴 **{user.first_name}'s Harem** ({len(waifus)} waifus)\n\n"
    for w in chunk:
        fav_star = " ⭐" if u_data.get("favorite_waifu_id") == w["id"] else ""
        text += f"• {w['rarity']} **{w['name']}** — {w['anime']}{fav_star}\n"
    await update.message.reply_text(text, reply_markup=harem_keyboard(chunk, page, total_pages, user.id), parse_mode="Markdown")


async def daily_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u = db.get_user(user.id, user.username, user.first_name)
    today = date.today().isoformat()
    if u["daily_claim"] == today:
        tomorrow = (date.today() + timedelta(days=1)).strftime("%d %b")
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]])
        await update.message.reply_text(f"⏰ Already claimed! Come back tomorrow ({tomorrow}).", reply_markup=kb)
        return
    reward = random.randint(200, 500)
    db.update_user(user.id, onex=u["onex"] + reward, daily_claim=today)
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("💰 Balance", callback_data="balance"),
        InlineKeyboardButton("🌟 Welkin", callback_data="welkin")
    ]])
    await update.message.reply_text(f"✅ **Daily!**\n\n💰 +{reward} Onex\n💎 Balance: {u['onex'] + reward}", reply_markup=kb, parse_mode="Markdown")


async def welkin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u = db.get_user(user.id, user.username, user.first_name)
    today = date.today().isoformat()
    if u["welkin_claim"] == today:
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]])
        await update.message.reply_text("⏰ Welkin already claimed today!", reply_markup=kb)
        return
    db.update_user(user.id, onex=u["onex"] + 300, welkin_claim=today)
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("💰 Balance", callback_data="balance"),
        InlineKeyboardButton("📦 Daily", callback_data="daily")
    ]])
    await update.message.reply_text("🌟 **Welkin Reward!**\n\n💰 +300 Onex", reply_markup=kb, parse_mode="Markdown")


async def treasure_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u = db.get_user(user.id, user.username, user.first_name)
    result = random.choices(["onex", "waifu", "nothing"], weights=[50, 30, 20], k=1)[0]
    if result == "onex":
        amount = random.randint(100, 1000)
        db.update_user(user.id, onex=u["onex"] + amount)
        text = f"💎 **Treasure!** You found **{amount} Onex**!"
    elif result == "waifu":
        waifus = db.get_all_waifus()
        if waifus:
            w = random.choice(waifus)
            db.give_waifu_to_user(user.id, w["id"])
            text = f"💎 **Treasure!** You got **{w['name']}** ({w['rarity']})!"
        else:
            text = "💎 Empty chest! 😢"
    else:
        text = "💎 Empty chest! Better luck next time. 😢"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]])
    await update.message.reply_text(text, reply_markup=kb, parse_mode="Markdown")


async def hclaim_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u = db.get_user(user.id, user.username, user.first_name)
    today = date.today().isoformat()
    if u["hclaim_date"] == today:
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🎴 View Harem", callback_data="harem_1")]])
        await update.message.reply_text("⏰ Free waifu already claimed today!", reply_markup=kb)
        return
    waifus = db.get_all_waifus()
    if not waifus:
        await update.message.reply_text("❌ No waifus in database yet!")
        return
    common_waifus = [w for w in waifus if w["rarity"] in ["🟢 Common", "🔵 Medium", "🟠 Rare"]]
    w = random.choice(common_waifus if common_waifus else waifus)
    db.give_waifu_to_user(user.id, w["id"])
    db.update_user(user.id, hclaim_date=today)
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("🎴 View Harem", callback_data="harem_1"),
        InlineKeyboardButton("🔙 Menu", callback_data="main_menu")
    ]])
    await update.message.reply_text(f"🎁 **Free Daily Waifu!**\n\n🎴 {w['name']} ({w['rarity']}) added!", reply_markup=kb, parse_mode="Markdown")


async def onex_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u = db.get_user(user.id, user.username, user.first_name)
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("📦 Daily", callback_data="daily"),
        InlineKeyboardButton("🛒 Shop", callback_data="shop_1")
    ]])
    await update.message.reply_text(f"💰 **{user.first_name}'s Balance**\n\n💎 Onex: `{u['onex']}`", reply_markup=kb, parse_mode="Markdown")


async def pay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u = db.get_user(user.id, user.username, user.first_name)
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to someone's message to pay them!")
        return
    if not context.args:
        await update.message.reply_text("Usage: `/pay <amount>` (reply to user)", parse_mode="Markdown")
        return
    try:
        amount = int(context.args[0])
        assert amount > 0
    except Exception:
        await update.message.reply_text("❌ Invalid amount!")
        return
    target = update.message.reply_to_message.from_user
    if target.id == user.id:
        await update.message.reply_text("❌ Can't pay yourself!")
        return
    if u["onex"] < amount:
        await update.message.reply_text(f"❌ Insufficient Onex! You have {u['onex']}.")
        return
    t_user = db.get_user(target.id, target.username, target.first_name)
    db.update_user(user.id, onex=u["onex"] - amount)
    db.update_user(target.id, onex=t_user["onex"] + amount)
    await update.message.reply_text(
        f"✅ **Transfer!**\n\n💸 {get_display_name(user)} → {get_display_name(target)}\n💰 {amount} Onex",
        parse_mode="Markdown"
    )


async def shop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    waifus = db.get_all_waifus()
    if not waifus:
        await update.message.reply_text("🛒 Shop is empty!")
        return
    page = 1
    chunk, total_pages = paginate(waifus, page, WAIFU_PER_PAGE)
    await update.message.reply_text(f"🛒 **Waifu Shop** (Page {page}/{total_pages})\n\nSelect a waifu to buy:", reply_markup=shop_keyboard(chunk, page, total_pages), parse_mode="Markdown")


async def rank_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u = db.get_user(user.id, user.username, user.first_name)
    top = db.get_top_collectors(1000)
    rank = next((i + 1 for i, r in enumerate(top) if r["user_id"] == user.id), "N/A")
    await update.message.reply_text(
        f"🏅 **{user.first_name}'s Rank**\n\n📊 #{rank}\n🎴 Waifus: {u['total_waifus']}\n💰 Onex: {u['onex']}",
        reply_markup=rank_keyboard(), parse_mode="Markdown"
    )


async def wpass_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u = db.get_user(user.id, user.username, user.first_name)
    waifus = db.get_user_waifus(user.id)
    rarity_counts = {}
    for w in waifus:
        rarity_counts[w["rarity"]] = rarity_counts.get(w["rarity"], 0) + 1
    text = f"📜 **{user.first_name}'s Waifu Pass**\n\n🎴 Total: {len(waifus)}\n💰 Onex: {u['onex']}\n\n"
    for rarity in RARITY_TIERS:
        count = rarity_counts.get(rarity, 0)
        if count > 0:
            text += f"{rarity}: {count}\n"
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("🎴 View Harem", callback_data="harem_1"),
        InlineKeyboardButton("🏅 Rank", callback_data="rank")
    ]])
    await update.message.reply_text(text, reply_markup=kb, parse_mode="Markdown")


async def top_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top = db.get_top_collectors(10)
    text = "🏅 **Top 10 Waifu Collectors**\n\n"
    medals = ["🥇", "🥈", "🥉"] + ["🔹"] * 7
    for i, u in enumerate(top):
        name = f"@{u['username']}" if u["username"] else u["first_name"]
        text += f"{medals[i]} {name} — {u['total_waifus']} waifus\n"
    await update.message.reply_text(text, reply_markup=top_keyboard("collectors"), parse_mode="Markdown")


async def tops_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top = db.get_top_rich(10)
    text = "💸 **Top 10 Richest**\n\n"
    medals = ["🥇", "🥈", "🥉"] + ["🔹"] * 7
    for i, u in enumerate(top):
        name = f"@{u['username']}" if u["username"] else u["first_name"]
        text += f"{medals[i]} {name} — {u['onex']} Onex\n"
    await update.message.reply_text(text, reply_markup=top_keyboard("rich"), parse_mode="Markdown")


async def topgroups_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    groups = db.get_top_groups(10)
    text = "🏆 **Top 10 Active Groups**\n\n"
    for i, g in enumerate(groups, 1):
        text += f"{i}. Chat `{g['chat_id']}` — {g['message_count']} messages\n"
    await update.message.reply_text(text, parse_mode="Markdown")


async def fav_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        await update.message.reply_text("Usage: `/fav <harem_id>`", parse_mode="Markdown")
        return
    try:
        uw_id = int(context.args[0])
    except Exception:
        await update.message.reply_text("❌ Invalid ID!")
        return
    waifu = db.get_waifu_by_uw_id(uw_id)
    if not waifu or waifu["user_id"] != user.id:
        await update.message.reply_text("❌ Waifu not found in your harem!")
        return
    db.update_user(user.id, favorite_waifu_id=uw_id)
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🎴 View Harem", callback_data="harem_1")]])
    await update.message.reply_text(f"⭐ **{waifu['name']}** set as favorite!", reply_markup=kb, parse_mode="Markdown")


async def check_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/check <harem_id>`", parse_mode="Markdown")
        return
    try:
        uw_id = int(context.args[0])
    except Exception:
        await update.message.reply_text("❌ Invalid ID!")
        return
    waifu = db.get_waifu_by_uw_id(uw_id)
    if not waifu:
        await update.message.reply_text("❌ Waifu not found!")
        return
    u = db.get_user(update.effective_user.id)
    sell_price = RARITY_TIERS.get(waifu["rarity"], {}).get("sell_price", 50)
    text = (
        f"🎴 **Waifu Details**\n\n"
        f"👤 {waifu['name']}\n📺 {waifu['anime']}\n⭐ {waifu['rarity']}\n"
        f"💰 Sell: {sell_price} Onex\n🆔 ID: {uw_id}"
    )
    kb = waifu_detail_keyboard(uw_id, u.get("favorite_waifu_id"))
    try:
        await update.message.reply_photo(photo=waifu["image_url"], caption=text, reply_markup=kb, parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(text, reply_markup=kb, parse_mode="Markdown")


async def wsell_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        await update.message.reply_text("Usage: `/wsell <harem_id>`", parse_mode="Markdown")
        return
    try:
        uw_id = int(context.args[0])
    except Exception:
        await update.message.reply_text("❌ Invalid ID!")
        return
    waifu = db.get_waifu_by_uw_id(uw_id)
    if not waifu or waifu["user_id"] != user.id:
        await update.message.reply_text("❌ Waifu not found in your harem!")
        return
    sell_price = RARITY_TIERS.get(waifu["rarity"], {}).get("sell_price", 50)
    await update.message.reply_text(f"💸 Sell **{waifu['name']}** for {sell_price} Onex?", reply_markup=sell_confirm_keyboard(uw_id, sell_price), parse_mode="Markdown")


async def gift_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to someone's message to gift!")
        return
    if not context.args:
        await update.message.reply_text("Usage: `/gift <harem_id>` (reply to user)", parse_mode="Markdown")
        return
    try:
        uw_id = int(context.args[0])
    except Exception:
        await update.message.reply_text("❌ Invalid ID!")
        return
    waifu = db.get_waifu_by_uw_id(uw_id)
    if not waifu or waifu["user_id"] != user.id:
        await update.message.reply_text("❌ Waifu not in your harem!")
        return
    target = update.message.reply_to_message.from_user
    if target.id == user.id:
        await update.message.reply_text("❌ Can't gift yourself!")
        return
    db.remove_user_waifu(uw_id, user.id)
    db.get_user(target.id, target.username, target.first_name)
    db.give_waifu_to_user(target.id, waifu["waifu_id"])
    await update.message.reply_text(
        f"🎁 {get_display_name(user)} gifted **{waifu['name']}** to {get_display_name(target)}!",
        parse_mode="Markdown"
    )


async def chaton_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.update_group(update.effective_chat.id, active_chat_mode=1)
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("💬 Chat Off", callback_data="chat_off")]])
    await update.message.reply_text("💬 **Anime Chat Mode ON!** 🌸", reply_markup=kb, parse_mode="Markdown")


async def chatoff_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.update_group(update.effective_chat.id, active_chat_mode=0)
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("💬 Chat On", callback_data="chat_on")]])
    await update.message.reply_text("💬 **Anime Chat Mode OFF.** 😴", reply_markup=kb, parse_mode="Markdown")


async def bcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not adm.is_admin(user.id):
        await update.message.reply_text("❌ Admin only!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a message with /bcast to broadcast it.")
        return
    conn = db.get_conn()
    users = conn.execute("SELECT user_id FROM users").fetchall()
    conn.close()
    success = 0
    for u in users:
        try:
            await context.bot.forward_message(chat_id=u["user_id"], from_chat_id=update.effective_chat.id, message_id=update.message.reply_to_message.message_id)
            success += 1
        except Exception:
            pass
        await asyncio.sleep(0.05)
    await update.message.reply_text(f"✅ Broadcast sent to {success}/{len(users)} users.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat:
        return
    msg = update.message
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == "private":
        text = msg.text or ""
        if context.user_data.get("admin_state") == "awaiting_waifu_name":
            parts = [p.strip() for p in text.split("|")]
            if len(parts) >= 4:
                name, anime, rarity, image = parts[0], parts[1], parts[2], parts[3]
                wid = db.add_waifu_to_db(name, anime, rarity, image, user.id)
                context.user_data.pop("admin_state", None)
                await msg.reply_text(
                    f"✅ **{name}** added! (ID: {wid})",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Admin Panel", callback_data="back_admin")]]),
                    parse_mode="Markdown"
                )
            else:
                await msg.reply_text("❌ Wrong format! Use: `Name | Anime | Rarity | ImageURL`", parse_mode="Markdown")
            return
        if context.user_data.get("admin_state") == "awaiting_give_onex":
            try:
                uid, amount = text.strip().split()
                uid, amount = int(uid), int(amount)
                u = db.get_user(uid)
                db.update_user(uid, onex=u["onex"] + amount)
                context.user_data.pop("admin_state", None)
                await msg.reply_text(
                    f"✅ Gave {amount} Onex to user {uid}",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Admin", callback_data="back_admin")]]),
                    parse_mode="Markdown"
                )
            except Exception:
                await msg.reply_text("❌ Format: `user_id amount`", parse_mode="Markdown")
            return
        await msg.reply_text(random.choice(ANIME_REPLIES))
        return
    db.get_user(user.id, user.username, user.first_name)
    group = db.get_group(chat.id)
    new_count = group["message_count"] + 1
    spawn_interval = group["spawn_interval"] or 15
    if new_count >= spawn_interval:
        db.update_group(chat.id, message_count=0)
        await spawn_waifu(context, chat.id)
    else:
        db.update_group(chat.id, message_count=new_count)
    if group["active_chat_mode"] and msg.text:
        if random.random() < 0.3:
            await msg.reply_text(random.choice(ANIME_REPLIES))


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data
    if data.startswith("admin_") or data in ("back_admin", "close_menu"):
        await adm.handle_admin_callback(update, context)
        return
    await query.answer()
    if data == "noop":
        return
    elif data == "main_menu":
        await query.edit_message_text(f"🌸 **Welcome back, {user.first_name}!**\n\nChoose an option:", reply_markup=main_menu_keyboard(), parse_mode="Markdown")
    elif data == "balance":
        u = db.get_user(user.id)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📦 Daily", callback_data="daily"), InlineKeyboardButton("🛒 Shop", callback_data="shop_1")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ])
        await query.edit_message_text(f"💰 **{user.first_name}'s Wallet**\n\n💎 Onex: `{u['onex']}`", reply_markup=kb, parse_mode="Markdown")
    elif data == "daily":
        u = db.get_user(user.id)
        today = date.today().isoformat()
        if u["daily_claim"] == today:
            await query.edit_message_text("⏰ Already claimed today!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]))
        else:
            reward = random.randint(200, 500)
            db.update_user(user.id, onex=u["onex"] + reward, daily_claim=today)
            await query.edit_message_text(f"✅ **Daily!**\n\n💰 +{reward} Onex\n💎 {u['onex'] + reward} Onex", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]]), parse_mode="Markdown")
    elif data == "welkin":
        u = db.get_user(user.id)
        today = date.today().isoformat()
        if u["welkin_claim"] == today:
            await query.edit_message_text("⏰ Welkin already claimed!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]))
        else:
            db.update_user(user.id, onex=u["onex"] + 300, welkin_claim=today)
            await query.edit_message_text("🌟 **Welkin!** +300 Onex", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]]), parse_mode="Markdown")
    elif data == "treasure":
        u = db.get_user(user.id)
        result = random.choices(["onex", "waifu", "nothing"], weights=[50, 30, 20], k=1)[0]
        if result == "onex":
            amount = random.randint(100, 1000)
            db.update_user(user.id, onex=u["onex"] + amount)
            text = f"💎 **Treasure!** Found **{amount} Onex**!"
        elif result == "waifu":
            waifus = db.get_all_waifus()
            if waifus:
                w = random.choice(waifus)
                db.give_waifu_to_user(user.id, w["id"])
                text = f"💎 Got **{w['name']}** ({w['rarity']})!"
            else:
                text = "💎 Empty chest! 😢"
        else:
            text = "💎 Empty chest! 😢"
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]]), parse_mode="Markdown")
    elif data.startswith("harem_"):
        page = int(data.split("_")[1])
        waifus = db.get_user_waifus(user.id)
        if not waifus:
            await query.edit_message_text("💔 Harem is empty!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]]))
            return
        chunk, total_pages = paginate(waifus, page, WAIFU_PER_PAGE)
        page = max(1, min(page, total_pages))
        chunk, total_pages = paginate(waifus, page, WAIFU_PER_PAGE)
        u = db.get_user(user.id)
        text = f"🎴 **{user.first_name}'s Harem** ({len(waifus)} waifus)\n\n"
        for w in chunk:
            fav = " ⭐" if u.get("favorite_waifu_id") == w["id"] else ""
            text += f"• {w['rarity']} **{w['name']}** — {w['anime']}{fav} [ID:{w['id']}]\n"
        await query.edit_message_text(text, reply_markup=harem_keyboard(chunk, page, total_pages, user.id), parse_mode="Markdown")
    elif data.startswith("waifu_detail_"):
        uw_id = int(data.split("_")[2])
        waifu = db.get_waifu_by_uw_id(uw_id)
        u = db.get_user(user.id)
        if not waifu:
            await query.edit_message_text("❌ Waifu not found!")
            return
        sell_price = RARITY_TIERS.get(waifu["rarity"], {}).get("sell_price", 50)
        text = f"🎴 **{waifu['name']}**\n\n📺 {waifu['anime']}\n⭐ {waifu['rarity']}\n💰 Sell: {sell_price} Onex\n🆔 ID: {uw_id}"
        await query.edit_message_text(text, reply_markup=waifu_detail_keyboard(uw_id, u.get("favorite_waifu_id")), parse_mode="Markdown")
    elif data.startswith("fav_"):
        uw_id = int(data.split("_")[1])
        waifu = db.get_waifu_by_uw_id(uw_id)
        u = db.get_user(user.id)
        if not waifu or waifu["user_id"] != user.id:
            await query.answer("❌ Not your waifu!", show_alert=True)
            return
        new_fav = None if u.get("favorite_waifu_id") == uw_id else uw_id
        db.update_user(user.id, favorite_waifu_id=new_fav)
        await query.answer(f"⭐ {'Set as fav!' if new_fav else 'Removed from fav!'}", show_alert=True)
        await query.edit_message_reply_markup(reply_markup=waifu_detail_keyboard(uw_id, new_fav))
    elif data.startswith("sell_confirm_"):
        uw_id = int(data.split("_")[2])
        waifu = db.get_waifu_by_uw_id(uw_id)
        if not waifu or waifu["user_id"] != user.id:
            await query.answer("❌ Not your waifu!", show_alert=True)
            return
        sell_price = RARITY_TIERS.get(waifu["rarity"], {}).get("sell_price", 50)
        await query.edit_message_text(f"💸 Sell **{waifu['name']}** for {sell_price} Onex?", reply_markup=sell_confirm_keyboard(uw_id, sell_price), parse_mode="Markdown")
    elif data.startswith("sell_do_"):
        uw_id = int(data.split("_")[2])
        waifu = db.get_waifu_by_uw_id(uw_id)
        if not waifu or waifu["user_id"] != user.id:
            await query.answer("❌ Not your waifu!", show_alert=True)
            return
        sell_price = RARITY_TIERS.get(waifu["rarity"], {}).get("sell_price", 50)
        db.remove_user_waifu(uw_id, user.id)
        u = db.get_user(user.id)
        db.update_user(user.id, onex=u["onex"] + sell_price)
        await query.edit_message_text(f"✅ Sold **{waifu['name']}** for {sell_price} Onex!\n💎 Balance: {u['onex'] + sell_price}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎴 Harem", callback_data="harem_1"), InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]]), parse_mode="Markdown")
    elif data.startswith("shop_"):
        page = int(data.split("_")[1])
        waifus = db.get_all_waifus()
        chunk, total_pages = paginate(waifus, page, WAIFU_PER_PAGE)
        await query.edit_message_text(f"🛒 **Waifu Shop** ({page}/{total_pages})", reply_markup=shop_keyboard(chunk, page, total_pages), parse_mode="Markdown")
    elif data.startswith("buy_confirm_"):
        wid = int(data.split("_")[2])
        conn = db.get_conn()
        w = conn.execute("SELECT * FROM waifus WHERE id=?", (wid,)).fetchone()
        conn.close()
        if not w:
            await query.answer("❌ Not found!", show_alert=True)
            return
        price = RARITY_TIERS.get(w["rarity"], {}).get("buy_price", 1000)
        await query.edit_message_text(f"🛒 Buy **{w['name']}** for {price} Onex?", reply_markup=buy_confirm_keyboard(wid, price), parse_mode="Markdown")
    elif data.startswith("buy_do_"):
        wid = int(data.split("_")[2])
        conn = db.get_conn()
        w = conn.execute("SELECT * FROM waifus WHERE id=?", (wid,)).fetchone()
        conn.close()
        if not w:
            await query.answer("❌ Not found!", show_alert=True)
            return
        u = db.get_user(user.id)
        price = RARITY_TIERS.get(w["rarity"], {}).get("buy_price", 1000)
        if u["onex"] < price:
            await query.answer(f"❌ Need {price} Onex!", show_alert=True)
            return
        db.update_user(user.id, onex=u["onex"] - price)
        db.give_waifu_to_user(user.id, wid)
        await query.edit_message_text(f"✅ Bought **{w['name']}!**\n💎 {u['onex'] - price} Onex left", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎴 Harem", callback_data="harem_1"), InlineKeyboardButton("🛒 Shop", callback_data="shop_1")]]), parse_mode="Markdown")
    elif data == "top":
        top = db.get_top_collectors(10)
        text = "🏅 **Top 10 Collectors**\n\n"
        medals = ["🥇", "🥈", "🥉"] + ["🔹"] * 7
        for i, u in enumerate(top):
            name = f"@{u['username']}" if u["username"] else u["first_name"]
            text += f"{medals[i]} {name} — {u['total_waifus']} waifus\n"
        await query.edit_message_text(text, reply_markup=top_keyboard("collectors"), parse_mode="Markdown")
    elif data == "tops":
        top = db.get_top_rich(10)
        text = "💸 **Top 10 Richest**\n\n"
        medals = ["🥇", "🥈", "🥉"] + ["🔹"] * 7
        for i, u in enumerate(top):
            name = f"@{u['username']}" if u["username"] else u["first_name"]
            text += f"{medals[i]} {name} — {u['onex']} Onex\n"
        await query.edit_message_text(text, reply_markup=top_keyboard("rich"), parse_mode="Markdown")
    elif data == "rank":
        u = db.get_user(user.id)
        top = db.get_top_collectors(1000)
        rank = next((i + 1 for i, r in enumerate(top) if r["user_id"] == user.id), "N/A")
        await query.edit_message_text(f"🏅 Rank: #{rank}\n🎴 {u['total_waifus']} waifus\n💰 {u['onex']} Onex", reply_markup=rank_keyboard(), parse_mode="Markdown")
    elif data == "wpass":
        u = db.get_user(user.id)
        waifus = db.get_user_waifus(user.id)
        rarity_counts = {}
        for w in waifus:
            rarity_counts[w["rarity"]] = rarity_counts.get(w["rarity"], 0) + 1
        text = f"📜 **{user.first_name}'s Waifu Pass**\n\n🎴 {len(waifus)}\n💰 {u['onex']}\n\n"
        for rarity in RARITY_TIERS:
            c = rarity_counts.get(rarity, 0)
            if c:
                text += f"{rarity}: {c}\n"
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎴 Harem", callback_data="harem_1"), InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]]), parse_mode="Markdown")
    elif data.startswith("quick_hunt_"):
        wid = int(data.split("_")[2])
        if update.effective_chat.type == "private":
            await query.answer("❌ Groups only!", show_alert=True)
            return
        group = db.get_group(update.effective_chat.id)
        if group["current_waifu_claimed"]:
            await query.answer("💨 Already claimed!", show_alert=True)
            return
        if group["current_waifu_id"] != wid:
            await query.answer("❌ No longer available!", show_alert=True)
            return
        db.update_group(update.effective_chat.id, current_waifu_claimed=1)
        db.get_user(user.id, user.username, user.first_name)
        db.give_waifu_to_user(user.id, wid)
        conn = db.get_conn()
        w = conn.execute("SELECT * FROM waifus WHERE id=?", (wid,)).fetchone()
        conn.close()
        wname = w["name"] if w else "Unknown"
        await query.edit_message_caption(caption=f"✅ **{get_display_name(user)} claimed {wname}!** 🎉\n\nUse /harem to view collection.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎴 View Harem", callback_data="harem_1")]]), parse_mode="Markdown")
    elif data == "chat_on":
        db.update_group(update.effective_chat.id, active_chat_mode=1)
        await query.edit_message_text("💬 **Chat Mode ON!** 🌸", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💬 Chat Off", callback_data="chat_off")]]))
    elif data == "chat_off":
        db.update_group(update.effective_chat.id, active_chat_mode=0)
        await query.edit_message_text("💬 **Chat Mode OFF.** 😴", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💬 Chat On", callback_data="chat_on")]]))


def main():
    db.init_db()
    db.seed_waifus()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hunt", hunt_cmd))
    app.add_handler(CommandHandler("harem", harem_cmd))
    app.add_handler(CommandHandler("hclaim", hclaim_cmd))
    app.add_handler(CommandHandler("fav", fav_cmd))
    app.add_handler(CommandHandler("check", check_cmd))
    app.add_handler(CommandHandler("wsell", wsell_cmd))
    app.add_handler(CommandHandler("gift", gift_cmd))
    app.add_handler(CommandHandler("daily", daily_cmd))
    app.add_handler(CommandHandler("welkin", welkin_cmd))
    app.add_handler(CommandHandler("tesure", treasure_cmd))
    app.add_handler(CommandHandler("onex", onex_cmd))
    app.add_handler(CommandHandler("pay", pay_cmd))
    app.add_handler(CommandHandler("shop", shop_cmd))
    app.add_handler(CommandHandler("rank", rank_cmd))
    app.add_handler(CommandHandler("wpass", wpass_cmd))
    app.add_handler(CommandHandler("top", top_cmd))
    app.add_handler(CommandHandler("tops", tops_cmd))
    app.add_handler(CommandHandler("topgroups", topgroups_cmd))
    app.add_handler(CommandHandler("ChatOn", chaton_cmd))
    app.add_handler(CommandHandler("ChatOff", chatoff_cmd))
    app.add_handler(CommandHandler("bcast", bcast_cmd))
    app.add_handler(CommandHandler("admin", adm.admin_panel))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    print("🤖 Sinzhu Waifu Bot started!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
