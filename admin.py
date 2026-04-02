from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import database as db
from keyboards import admin_panel_keyboard
import os

ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "123456789").split(",")]

def is_admin(user_id):
    return user_id in ADMIN_IDS

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("❌ You don't have admin access!")
        return
    
    all_waifus = db.get_all_waifus()
    conn = db.get_conn()
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_groups = conn.execute("SELECT COUNT(*) FROM group_data").fetchone()[0]
    conn.close()
    
    text = (
        "🔧 **SINZHU ADMIN PANEL**\n\n"
        f"👤 Total Users: `{total_users}`\n"
        f"👥 Total Groups: `{total_groups}`\n"
        f"🎴 Total Waifus: `{len(all_waifus)}`\n\n"
        "Choose an action below:"
    )
    await update.message.reply_text(text, reply_markup=admin_panel_keyboard(), parse_mode="Markdown")

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data
    
    if not is_admin(user.id):
        await query.answer("❌ No access!", show_alert=True)
        return
    
    await query.answer()
    
    if data == "admin_stats":
        conn = db.get_conn()
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_groups = conn.execute("SELECT COUNT(*) FROM group_data").fetchone()[0]
        total_waifus = conn.execute("SELECT COUNT(*) FROM waifus").fetchone()[0]
        total_uw = conn.execute("SELECT COUNT(*) FROM user_waifus").fetchone()[0]
        conn.close()
        text = (
            "📊 **BOT STATISTICS**\n\n"
            f"👤 Users: `{total_users}`\n"
            f"👥 Groups: `{total_groups}`\n"
            f"🎴 Waifu Types: `{total_waifus}`\n"
            f"💝 Total Collected: `{total_uw}`\n"
        )
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Admin Panel", callback_data="back_admin")]
        ]), parse_mode="Markdown")
    
    elif data == "back_admin":
        await query.edit_message_text(
            "🔧 **SINZHU ADMIN PANEL**\n\nChoose an action:",
            reply_markup=admin_panel_keyboard(),
            parse_mode="Markdown"
        )
    
    elif data == "admin_add_waifu":
        context.user_data["admin_state"] = "awaiting_waifu_name"
        await query.edit_message_text(
            "➕ **ADD NEW WAIFU**\n\nSend waifu details in this format:\n"
            "`Name | Anime | Rarity | ImageURL`\n\n"
            "Rarities:\n"
            "🌟 God Summon, ✨ Goddess, 🔮 Limited, 💎 Premium,\n"
            "🎐 Special, 💮 Exclusive, 🪽 Celestial, 🟡 Legendary,\n"
            "🟠 Rare, 🔵 Medium, 🟢 Common",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel", callback_data="back_admin")]
            ]),
            parse_mode="Markdown"
        )
    
    elif data.startswith("admin_del_waifu_list_"):
        page = int(data.split("_")[-1])
        all_waifus = db.get_all_waifus()
        per_page = 8
        start = (page-1)*per_page
        end = start+per_page
        chunk = all_waifus[start:end]
        total_pages = max(1, (len(all_waifus)+per_page-1)//per_page)
        
        buttons = []
        for w in chunk:
            buttons.append([InlineKeyboardButton(
                f"🗑️ {w['name']} ({w['rarity']})",
                callback_data=f"admin_del_confirm_{w['id']}"
            )])
        
        nav = []
        if page > 1:
            nav.append(InlineKeyboardButton("◀️", callback_data=f"admin_del_waifu_list_{page-1}"))
        nav.append(InlineKeyboardButton(f"{page}/{total_pages}", callback_data="noop"))
        if page < total_pages:
            nav.append(InlineKeyboardButton("▶️", callback_data=f"admin_del_waifu_list_{page+1}"))
        if nav:
            buttons.append(nav)
        buttons.append([InlineKeyboardButton("🔙 Back", callback_data="back_admin")])
        
        await query.edit_message_text(
            f"🗑️ **DELETE WAIFU** (Page {page}/{total_pages})\nSelect waifu to delete:",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="Markdown"
        )
    
    elif data.startswith("admin_del_confirm_"):
        wid = int(data.split("_")[-1])
        conn = db.get_conn()
        w = conn.execute("SELECT * FROM waifus WHERE id=?", (wid,)).fetchone()
        conn.close()
        if w:
            await query.edit_message_text(
                f"🗑️ Delete **{w['name']}** ({w['rarity']})?\nThis will remove it from ALL user harams!",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✅ Delete", callback_data=f"admin_del_do_{wid}"),
                        InlineKeyboardButton("❌ Cancel", callback_data="admin_del_waifu_list_1"),
                    ]
                ]),
                parse_mode="Markdown"
            )
    
    elif data.startswith("admin_del_do_"):
        wid = int(data.split("_")[-1])
        conn = db.get_conn()
        w = conn.execute("SELECT name FROM waifus WHERE id=?", (wid,)).fetchone()
        conn.close()
        name = w['name'] if w else "Unknown"
        db.delete_waifu_from_db(wid)
        await query.edit_message_text(
            f"✅ **{name}** deleted successfully!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Admin Panel", callback_data="back_admin")]
            ]),
            parse_mode="Markdown"
        )
    
    elif data == "admin_broadcast":
        context.user_data["admin_state"] = "awaiting_broadcast"
        await query.edit_message_text(
            "📢 **BROADCAST**\n\nSend the message to broadcast to all users.\n(Can include photo — reply /bcast to a message)",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel", callback_data="back_admin")]
            ]),
            parse_mode="Markdown"
        )
    
    elif data == "admin_give_onex":
        context.user_data["admin_state"] = "awaiting_give_onex"
        await query.edit_message_text(
            "💰 **GIVE ONEX**\n\nFormat: `user_id amount`\nExample: `123456789 5000`",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel", callback_data="back_admin")]
            ]),
            parse_mode="Markdown"
        )
    
    elif data == "close_menu":
        await query.edit_message_text("✅ Admin panel closed.")

    
