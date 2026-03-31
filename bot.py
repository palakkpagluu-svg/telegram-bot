from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from flask import Flask
from threading import Thread

# =========================
# 🔐 DETAILS
# =========================
TOKEN = "8758864770:AAGsopycO503b7P6S6zs8eKKU_CjYyoCwBs"
ADMIN_ID = 7705209352

UPI_ID = "niteshextema@fam"
NAME = "Nitesh"

# =========================
# 🧠 STORAGE
# =========================
user_data_store = {}
used_utrs = set()

# =========================
# 📋 MENU
# =========================
keyboard = [
    ["💰 1K Followers - ₹10", "💰 5K Followers - ₹50"],
    ["💰 10K Followers - ₹100"],
    ["🆘 Support / Problem"]
]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# =========================
# 🚀 START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 *Welcome*\n\nOption select karo:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# =========================
# 📥 USERNAME INPUT
# =========================
async def ask_username(update, plan):
    user_id = update.message.from_user.id
    user_data_store[user_id] = {"plan": plan, "step": "username"}

    await update.message.reply_text("📩 Apna Instagram username bhejo:")

# =========================
# 💸 PAYMENT (QR + LINK)
# =========================
async def send_payment(update, user_id):
    plan = user_data_store[user_id]["plan"]
    username = user_data_store[user_id]["username"]

    upi_link = f"upi://pay?pa={UPI_ID}&pn={NAME}&cu=INR"

    try:
        with open("qr.png", "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=f"💸 *{plan}*\n👤 Username: {username}\n\nScan karke payment karo\n📸 Screenshot bhejo",
                parse_mode="Markdown"
            )
    except:
        await update.message.reply_text("❌ QR missing (qr.png upload karo)")

    await update.message.reply_text("📸 Payment ke baad screenshot bhejo")

# =========================
# 🧠 HANDLE TEXT
# =========================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # Plan select
    if "1K" in text or "5K" in text or "10K" in text:
        await ask_username(update, text)
        return

    # Support
    if "Support" in text or "Problem" in text:
        user_data_store[user_id] = {"step": "support"}
        await update.message.reply_text("📝 Apni problem likho:")
        return

    # Username input
    if user_id in user_data_store and user_data_store[user_id].get("step") == "username":
        user_data_store[user_id]["username"] = text
        user_data_store[user_id]["step"] = "payment"

        await send_payment(update, user_id)
        return

    # UTR input
    if user_id in user_data_store and user_data_store[user_id].get("step") == "utr":
        utr = text.strip()

        if utr in used_utrs:
            await update.message.reply_text("❌ Fake payment detected (duplicate UTR)")
            return

        if len(utr) < 8:
            await update.message.reply_text("❌ Invalid UTR number")
            return

        used_utrs.add(utr)
        user_data_store[user_id]["utr"] = utr
        user_data_store[user_id]["step"] = "done"

        data = user_data_store[user_id]

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💰 Payment Details\nUser ID: {user_id}\nUsername: {data['username']}\nPlan: {data['plan']}\nUTR: {utr}\nApprove: /approve {user_id}"
        )

        await update.message.reply_text("⏳ Payment under verification...")
        return

    # Support message
    if user_id in user_data_store and user_data_store[user_id].get("step") == "support":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🆘 Support Message\nUser ID: {user_id}\nMessage: {text}"
        )
        await update.message.reply_text("✅ Problem admin ko bhej di gayi hai")
        user_data_store[user_id]["step"] = None
        return

# =========================
# 📸 SCREENSHOT VERIFY
# =========================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id

    data = user_data_store.get(user_id, {})
    username = data.get("username", "N/A")
    plan = data.get("plan", "N/A")

    # admin ko forward
    await context.bot.forward_message(
        chat_id=ADMIN_ID,
        from_chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"User ID: {user_id}\nUsername: {username}\nPlan: {plan}\n📸 Screenshot received\n🔢 Ask UTR now"
    )

    # next step → UTR
    user_data_store[user_id]["step"] = "utr"

    await update.message.reply_text("🔢 Apna UTR / Transaction ID bhejo:")

# =========================
# ✅ APPROVE
# =========================
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    try:
        user_id = int(context.args[0])

        await context.bot.send_message(
            chat_id=user_id,
            text="✅ Payment Successful 🎉\n🚀 Order started!"
        )

    except:
        await update.message.reply_text("❌ Error")

# =========================
# 🌐 FLASK (Koyeb)
# =========================
app = Flask('')

@app.route('/')
def home():
    return "Bot running"

def run():
    app.run(host='0.0.0.0', port=8000)

def keep_alive():
    Thread(target=run).start()

# =========================
# ▶️ MAIN
# =========================
async def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(MessageHandler(filters.TEXT, handle_text))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("🤖 Bot running...")
    await application.run_polling()

if __name__ == "__main__":
    keep_alive()

    import asyncio
    asyncio.run(main())