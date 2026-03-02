#!/usr/bin/env python3
"""
🔐 NumINTEL-X | Official Bot of HackingHubk
Telecom Intelligence & Number Metadata System
"""
import os
from dotenv import load_dotenv
load_dotenv()

import re
import time
import json
import logging
from pathlib import Path
from collections import defaultdict

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ================= 🔧 CONFIG =================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

CHANNEL_USERNAME = "@HackingHubk"
CHANNEL_URL = "https://t.me/HackingHubk"

ADMIN_IDS = {6667369072}

DATA_FILE = Path("data.json")

STARTING_BALANCE = 10
COST_PER_LOOKUP = 1
REFERRAL_BONUS = 5
RATE_LIMIT_SECONDS = 5

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NumINTELX_Bot")

# ================= 💾 DATA SYSTEM =================

def load_data():
    if not DATA_FILE.exists():
        base = {"users": {}}
        DATA_FILE.write_text(json.dumps(base, indent=2))
        return base
    try:
        return json.loads(DATA_FILE.read_text())
    except:
        base = {"users": {}}
        DATA_FILE.write_text(json.dumps(base, indent=2))
        return base

def save_data(d):
    DATA_FILE.write_text(json.dumps(d, indent=2))

data = load_data()

def ensure_user(uid: int):
    uid = str(uid)
    if uid not in data["users"]:
        data["users"][uid] = {
            "balance": STARTING_BALANCE,
            "created": int(time.time()),
            "ref_by": None,
        }
        save_data(data)
    return data["users"][uid]

def add_balance(uid: int, amt: int):
    ensure_user(uid)["balance"] += amt
    save_data(data)

def deduct_balance(uid: int, amt: int):
    user = ensure_user(uid)
    if user["balance"] >= amt:
        user["balance"] -= amt
        save_data(data)
        return True
    return False

def get_balance(uid: int):
    return ensure_user(uid)["balance"]

# ================= 🛠 UTILITIES =================

async def is_member(app, user_id):
    try:
        m = await app.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return m.status in ("member", "administrator", "creator")
    except:
        return False

def main_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔎 Number Lookup", callback_data="menu_lookup"),
            InlineKeyboardButton("💰 My Balance", callback_data="menu_balance"),
        ],
        [
            InlineKeyboardButton("🎁 Referral Info", callback_data="menu_referral"),
            InlineKeyboardButton("📢 Join Channel", url=CHANNEL_URL),
        ],
    ])

PHONE_RE = re.compile(r"\b\d{10}\b")
last_call_time = defaultdict(lambda: 0)

def mask_id(value):
    return "*" * (len(value) - 4) + value[-4:] if value else ""

# ================= 🚀 BOT HANDLERS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    args = context.args

    ensure_user(chat_id)

    # Referral Logic
    if args and args[0].isdigit():
        ref_id = args[0]
        if ref_id != str(chat_id) and ref_id in data["users"]:
            if not ensure_user(chat_id).get("ref_by"):
                ensure_user(chat_id)["ref_by"] = ref_id
                add_balance(int(ref_id), REFERRAL_BONUS)
                add_balance(chat_id, REFERRAL_BONUS)
                save_data(data)
                await update.message.reply_text(
                    f"🎉 Referral Activated!\n\nBoth users received +{REFERRAL_BONUS} credits."
                )

    text = (
        f"🔐 *Welcome to NumINTEL-X*\n\n"
        f"Official Intelligence Bot of *HackingHubk* ⚡\n\n"
        f"🧠 Telecom Intelligence System\n"
        f"💳 Credit-Based Access Model\n"
        f"🎁 Referral Rewards Available\n\n"
        f"🔍 Each lookup costs *{COST_PER_LOOKUP}* credit.\n\n"
        f"💰 Starting Balance: *{STARTING_BALANCE}*\n\n"
        f"🔗 Your Referral Link:\n"
        f"`t.me/{context.bot.username}?start={chat_id}`"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 Open Dashboard", callback_data="open_menu")],
            [InlineKeyboardButton("📢 Join HackingHubk", url=CHANNEL_URL)],
        ])
    )

async def open_menu_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🖥 *NumINTEL-X Dashboard*\n\nSelect an option below:",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

async def menu_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id

    if query.data == "menu_lookup":
        if not await is_member(context.application, chat_id):
            await query.edit_message_text(
                f"🚫 Access Restricted!\n\nPlease join {CHANNEL_USERNAME} first.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📢 Join Now", url=CHANNEL_URL)]
                ])
            )
            return

        await context.bot.send_message(
            chat_id,
            "📱 Send a *10-digit mobile number* to begin lookup.",
            parse_mode="Markdown"
        )

    elif query.data == "menu_balance":
        await query.edit_message_text(
            f"💰 *Your Current Balance:* {get_balance(chat_id)} credits",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )

    elif query.data == "menu_referral":
        await query.edit_message_text(
            f"🎁 *Referral System*\n\n"
            f"Invite friends & earn *{REFERRAL_BONUS} credits* each!\n\n"
            f"🔗 `t.me/{context.bot.username}?start={chat_id}`",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )

async def text_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text or ""

    match = PHONE_RE.search(text)
    if not match:
        return

    number = match.group()

    if time.time() - last_call_time[chat_id] < RATE_LIMIT_SECONDS:
        await update.message.reply_text("⏳ Please wait before next lookup.")
        return

    if not await is_member(context.application, chat_id):
        await update.message.reply_text(f"🚫 Join {CHANNEL_USERNAME} first.")
        return

    if not deduct_balance(chat_id, COST_PER_LOOKUP):
        await update.message.reply_text("❌ Insufficient balance.")
        return

    last_call_time[chat_id] = time.time()

    # 🔥 Demo Dataset
    demo_data = {
        "9876543210": {
            "name": "Rahul Sharma",
            "circle": "Delhi",
            "email": "rahul.sharma@rahat.com",
            "id_number": "458712369874"
        },
        "9123456789": {
            "name": "Priya Verma",
            "circle": "Mumbai",
            "email": "priya.verma@st.com",
            "id_number": "784512369852"
        },
        "9988776655": {
            "name": "Amit Singh",
            "circle": "Lucknow",
            "email": "amit.singh@ji.com",
            "id_number": "963258741236"
        }
    }

    record = demo_data.get(number, {
        "name": "Unknown User",
        "circle": "Unknown Region",
        "email": "not_available@example.com",
        "id_number": None
    })

    result_text = (
        f"📊 *NumINTEL-X Analysis Result*\n\n"
        f"📱 Number: `{number}`\n"
        f"👤 Name: {record.get('name')}\n"
        f"🌍 Circle: {record.get('circle')}\n"
        f"✉ Email: {record.get('email')}\n"
    )

    if record.get("id_number"):
        result_text += f"🆔 ID: `{mask_id(record['id_number'])}`\n"

    result_text += f"\n💰 Remaining Credits: {get_balance(chat_id)}"

    await update.message.reply_text(result_text, parse_mode="Markdown")

# ================= 🚀 MAIN =================

def main():
    if not TELEGRAM_TOKEN:
        raise ValueError("❌ Set TELEGRAM_BOT_TOKEN environment variable first!")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(open_menu_cb, pattern="^open_menu$"))
    app.add_handler(CallbackQueryHandler(menu_cb, pattern="^menu_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_msg))

    logger.info("✅ NumINTEL-X running successfully...")
    app.run_polling()

if __name__ == "__main__":
    main()