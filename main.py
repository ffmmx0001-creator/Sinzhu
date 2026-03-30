from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from datetime import date, datetime
import random

TOKEN = "8683534945:AAEk_LcMWJmI0oMIbejGxtbpVM-1QAapGV4"
ADMIN_IDS = [7088023034]  # @userinfobot se apna ID lo

rooms = {}
users = {}
groups = {}

WORDS = ["Pizza","Burger","Train","Car","School","Hospital","Beach","Cinema","Airport","Library","Market","Temple"]

# Shop list - ID = index (0, 1, 2...)
shop_items = []

def get_user(uid, name="Player"):
    if uid not in users:
        users[uid] = {
            "name": name, "coins": 100, "gold": 0,
            "wins": 0, "games": 0, "spy_wins": 0,
            "pfp": "🎮 Default", "pfp_photo_id": None,
            "daily_claimed": None, "weekly_claimed": None,
        }
    return users[uid]

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    d = get_user(u.id, u.first_name)
    d["name"] = u.first_name
    await update.message.reply_text(
        f"🌟 *Welcome {u.first_name}!*\n\n"
        "🀄 /room 4 — Game room banao\n"
        "🎴 /profile — Profile dekho\n"
        "🍄 /rank — Rank check karo\n"
        "💸 /daily — Daily coins lo\n"
        "💰 /weekly — Weekly gold lo\n"
        "🏪 /shop — PFP kharido\n"
        "🌍 /top — Top 10 Villagers\n"
        "❄️ /topgroups — Top 10 Groups\n\n"
        "👑 *Admin:*\n"
        "/upload <title> <price> — Photo ko reply karo\n"
        "/dpfp <id> — Item delete karo",
        parse_mode="Markdown"
    )

# /profile - Telegram profile photo show karo
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    d = get_user(u.id, u.first_name)
    wr = round((d["wins"]/d["games"])*100) if d["games"] > 0 else 0
    text = (
        f"🎴 *{d['name']} ka Profile*\n\n"
        f"🖼 PFP: {d['pfp']}\n"
        f"💰 Coins: {d['coins']}\n"
        f"🥇 Gold: {d['gold']}\n"
        f"🎮 Games: {d['games']}\n"
        f"🏆 Wins: {d['wins']}\n"
        f"🕵️ Spy Wins: {d['spy_wins']}\n"
        f"📊 Win Rate: {wr}%"
    )
    # Telegram profile photo fetch karo
    try:
        photos = await context.bot.get_user_profile_photos(u.id, limit=1)
        if photos.total_count > 0:
            photo_id = photos.photos[0][-1].file_id
            await context.bot.send_photo(update.effective_chat.id, photo_id, caption=text, parse_mode="Markdown")
            return
    except:
        pass
    # Agar pfp kharida ho
    if d.get("pfp_photo_id"):
        await context.bot.send_photo(update.effective_chat.id, d["pfp_photo_id"], caption=text, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, parse_mode="Markdown")

# /shop - pehla item dikha
async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not shop_items:
        await update.message.reply_text("🏪 Shop abhi khaali hai!")
        return
    await show_shop_item(update.message.chat.id, 0, context, update.message)

async def show_shop_item(chat_id, index, context, message=None, edit_msg=None):
    if not shop_items or index < 0 or index >= len(shop_items):
        return
    item = shop_items[index]
    total = len(shop_items)

    caption = (
        f"┌─── 🏪 *SHOP - SPY SHOP* ───┐\n\n"
        f"| ➡ 💖 *TITLE:* {item['name']}\n"
        f"| ➡ 🆔 *ID:* {index}\n"
        f"| ➡ 🦋 *PRICE:* {item['price']} coins\n\n"
        f"└──────────────────────┘\n"
        f"📦 Item {index+1} of {total}"
    )

    buttons = []
    buy_row = [InlineKeyboardButton("🛒 Buy", callback_data=f"buy_{index}")]
    buttons.append(buy_row)

    nav_row = []
    if index > 0:
        nav_row.append(InlineKeyboardButton("⬅ Previous", callback_data=f"shop_{index-1}"))
    if index < total - 1:
        nav_row.append(InlineKeyboardButton("➡ Next", callback_data=f"shop_{index+1}"))
    if nav_row:
        buttons.append(nav_row)

    markup = InlineKeyboardMarkup(buttons)

    if item["photo_id"]:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=item["photo_id"],
            caption=caption,
            reply_markup=markup,
            parse_mode="Markdown"
        )
    else:
        if message:
            await message.reply_text(caption, reply_markup=markup, parse_mode="Markdown")
        else:
            await context.bot.send_message(chat_id, caption, reply_markup=markup, parse_mode="Markdown")

# Shop navigation callback
async def shop_nav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    index = int(q.data.split("_")[1])
    await show_shop_item(q.message.chat.id, index, context)

# Buy callback
async def buy_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    u = q.from_user
    d = get_user(u.id, u.first_name)
    index = int(q.data.split("_")[1])
    if index < 0 or index >= len(shop_items):
        await q.answer("Yeh item available nahi!", show_alert=True); return
    item = shop_items[index]
    if d["coins"] < item["price"]:
        await q.answer(f"Coins kam hain! {item['price']} chahiye, tumhare paas {d['coins']}", show_alert=True); return
    d["coins"] -= item["price"]
    d["pfp"] = item["name"]
    if item["photo_id"]: d["pfp_photo_id"] = item["photo_id"]
    await q.message.reply_text(
        f"✅ *{item['name']}* khareed liya!\n💰 Baaki Coins: {d['coins']}",
        parse_mode="Markdown"
    )

# /upload <title> <price> - photo ko reply karo
async def upload_pfp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    if u.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Sirf admin use kar sakta hai!")
        return
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text("⚠️ Kisi *photo* ko reply karo aur likho:\n/upload Hinata 5000", parse_mode="Markdown")
        return
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Sahi tarika: /upload Title 5000\n(Photo ko reply karo)")
        return
    try:
        price = int(context.args[-1].replace("₹","").replace(",","").strip())
        title = " ".join(context.args[:-1])
    except:
        await update.message.reply_text("⚠️ Sahi tarika: /upload Title 5000")
        return
    photo_id = update.message.reply_to_message.photo[-1].file_id
    new_id = len(shop_items)
    shop_items.append({"name": title, "price": price, "photo_id": photo_id})
    await update.message.reply_text(
        f"✅ *Shop mein add ho gaya!*\n\n"
        f"💖 Title: {title}\n"
        f"🆔 ID: {new_id}\n"
        f"🦋 Price: {price} coins",
        parse_mode="Markdown"
    )

# /dpfp <id> - item delete karo
async def delete_pfp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    if u.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Sirf admin use kar sakta hai!")
        return
    try:
        del_id = int(context.args[0])
    except:
        await update.message.reply_text("⚠️ Sahi tarika: /dpfp 0")
        return
    if del_id < 0 or del_id >= len(shop_items):
        await update.message.reply_text(f"❌ ID {del_id} exist nahi karta!")
        return
    removed = shop_items.pop(del_id)
    await update.message.reply_text(
        f"🗑 *{removed['name']}* (ID: {del_id}) delete ho gaya!\n"
        f"Ab shop mein {len(shop_items)} items hain.",
        parse_mode="Markdown"
    )

# /rank
async def rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    d = get_user(u.id, u.first_name)
    sl = sorted(users.items(), key=lambda x: x[1]["wins"], reverse=True)
    pos = next((i+1 for i,(uid,_) in enumerate(sl) if uid == u.id), "?")
    w = d["wins"]
    if w >= 50: t = "👑 Grand Spy Master"
    elif w >= 30: t = "💎 Elite Spy"
    elif w >= 15: t = "🔥 Senior Spy"
    elif w >= 5: t = "⚔️ Spy Agent"
    else: t = "🌱 Rookie"
    await update.message.reply_text(
        f"🍄 *Tumhara Rank*\n\n🏅 {t}\n📊 Position: #{pos}/{len(users)}\n🏆 Wins: {w}",
        parse_mode="Markdown"
    )

# /daily
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    d = get_user(u.id, u.first_name)
    today = str(date.today())
    if d["daily_claimed"] == today:
        await update.message.reply_text("💸 Aaj ke coins le liye! Kal aana."); return
    c = random.randint(50, 200)
    d["coins"] += c; d["daily_claimed"] = today
    await update.message.reply_text(f"💸 *+{c} Coins!*\nTotal: {d['coins']}", parse_mode="Markdown")

# /weekly
async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    d = get_user(u.id, u.first_name)
    wk = str(datetime.now().isocalendar()[:2])
    if d["weekly_claimed"] == wk:
        await update.message.reply_text("💰 Is hafte ka gold le liya!"); return
    g = random.randint(5, 20)
    d["gold"] += g; d["weekly_claimed"] = wk
    await update.message.reply_text(f"💰 *+{g} Gold!*\nTotal: {d['gold']}", parse_mode="Markdown")

# /top
async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not users:
        return await update.message.reply_text("Abhi koi player nahi!")
    sl = sorted(users.items(), key=lambda x: x[1]["wins"], reverse=True)[:10]
    m = ["🥇","🥈","🥉"] + ["🏅"]*7
    text = "🌍 *Top 10 Villagers*\n\n"
    for i,(uid,d) in enumerate(sl): text += f"{m[i]} {d['name']} — {d['wins']} wins\n"
    await update.message.reply_text(text, parse_mode="Markdown")

# /topgroups
async def topgroups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not groups:
        return await update.message.reply_text("Abhi koi group data nahi!")
    sl = sorted(groups.items(), key=lambda x: x[1]["wins"], reverse=True)[:10]
    m = ["🥇","🥈","🥉"] + ["🏅"]*7
    text = "❄️ *Top 10 Groups*\n\n"
    for i,(gid,d) in enumerate(sl): text += f"{m[i]} {d['name']} — {d['wins']} wins\n"
    await update.message.reply_text(text, parse_mode="Markdown")

# /room
async def room_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        size = int(context.args[0])
        if size < 4 or size > 8: return await update.message.reply_text("Room size 4-8 hona chahiye!")
    except: return await update.message.reply_text("Sahi tarika: /room 4")
    rid = update.effective_chat.id
    chat = update.effective_chat
    if rid not in groups: groups[rid] = {"name": chat.title or "Group", "wins": 0}
    rooms[rid] = {"players":[], "player_names":{}, "size":size, "started":False, "spy":None, "votes":{}, "word":""}
    await update.message.reply_text(
        f"🀄 *Room ban gaya!* {size} players chahiye.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✋ Join Game", callback_data="join")]]),
        parse_mode="Markdown"
    )

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    u = q.from_user; cid = q.message.chat.id
    if cid not in rooms: await q.answer("Koi room nahi!", show_alert=True); return
    game = rooms[cid]
    if game["started"]: await q.answer("Game shuru ho gaya!", show_alert=True); return
    if u.id in game["players"]: await q.answer("Pehle se join ho!", show_alert=True); return
    get_user(u.id, u.first_name)
    game["players"].append(u.id); game["player_names"][u.id] = u.first_name
    await q.message.reply_text(f"✅ *{u.first_name}* join! ({len(game['players'])}/{game['size']})", parse_mode="Markdown")
    if len(game["players"]) == game["size"]: await start_game(cid, q.message, context)

async def start_game(cid, message, context):
    game = rooms[cid]; players = game["players"]
    word = random.choice(WORDS); spy_word = random.choice([w for w in WORDS if w != word])
    spy = random.choice(players)
    game["spy"] = spy; game["started"] = True; game["word"] = word
    for p in players:
        if p in users: users[p]["games"] += 1
        try:
            if p == spy: await context.bot.send_message(p, f"💖*Tumhara!*\nWord: *{spy_word}*", parse_mode="Markdown")
            else: await context.bot.send_message(p, f"💖 *Tumhara!*\nWord: *{word}*", parse_mode="Markdown")
        except: pass
    await message.reply_text("🎯 *Game shuru!*\nVote: /vote user_id", parse_mode="Markdown")

async def vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rid = update.effective_chat.id; game = rooms.get(rid)
    if not game or not game["started"]: return await update.message.reply_text("Koi game nahi!")
    try: vid = int(context.args[0])
    except: return await update.message.reply_text("Sahi: /vote user_id")
    voter = update.effective_user.id
    if voter not in game["players"]: return await update.message.reply_text("Tum game mein nahi!")
    if vid not in game["players"]: return await update.message.reply_text("Yeh player nahi!")
    game["votes"][voter] = vid
    await update.message.reply_text(f"✅ Vote! ({len(game['votes'])}/{len(game['players'])})")
    if len(game["votes"]) == len(game["players"]): await end_game(update, context)

async def endgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rid = update.effective_chat.id
    if rid in rooms: rooms.pop(rid); await update.message.reply_text("🛑 Game band.")
    else: await update.message.reply_text("Koi game nahi.")

async def end_game(update, context):
    rid = update.effective_chat.id; game = rooms.get(rid)
    if not game: return
    vc = {}
    for v in game["votes"].values(): vc[v] = vc.get(v, 0) + 1
    accused = max(vc, key=vc.get); spy = game["spy"]
    sn = game["player_names"].get(spy, str(spy))
    if accused == spy:
        result = f"🎉 *Spy pakda! Villagers jeete!*\nSpy: {sn} | Word: {game['word']}"
        for p in game["players"]:
            if p != spy and p in users: users[p]["wins"] += 1; users[p]["coins"] += 100
        if spy in users: users[spy]["coins"] = max(0, users[spy]["coins"] - 50)
    else:
        result = f"😈 *Spy bach gaya!*\nSpy: {sn} | Word: {game['word']}"
        if spy in users: users[spy]["spy_wins"] += 1; users[spy]["wins"] += 1; users[spy]["coins"] += 200
        if rid in groups: groups[rid]["wins"] += 1
    await update.message.reply_text(result, parse_mode="Markdown")
    rooms.pop(rid, None)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("room", room_cmd))
app.add_handler(CommandHandler("vote", vote))
app.add_handler(CommandHandler("endgame", endgame))
app.add_handler(CommandHandler("profile", profile))
app.add_handler(CommandHandler("rank", rank))
app.add_handler(CommandHandler("daily", daily))
app.add_handler(CommandHandler("weekly", weekly))
app.add_handler(CommandHandler("shop", shop))
app.add_handler(CommandHandler("top", top))
app.add_handler(CommandHandler("topgroups", topgroups))
app.add_handler(CommandHandler("upload", upload_pfp))
app.add_handler(CommandHandler("dpfp", delete_pfp))
app.add_handler(CallbackQueryHandler(join, pattern="^join$"))
app.add_handler(CallbackQueryHandler(shop_nav, pattern="^shop_\\d+$"))
app.add_handler(CallbackQueryHandler(buy_item, pattern="^buy_\\d+$"))

print("Bot chal raha hai...")
app.run_polling()
        
