import os
import qrcode
from io import BytesIO
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("8758864770:AAGsopycO503b7P6S6zs8eKKU_CjYyoCwBs")
ADMIN_ID = 7705209352
UPI_ID = "niteshextema@fam"
NAME = "Nitesh"

users = {}

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["1K Followers - ₹10"],
        ["5K Followers - ₹50"],
        ["10K Followers - ₹100"],
        ["💬 Support"]
    ]
    await update.message.reply_text(
        "🔥 Welcome!\nSelect a package:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ===== QR GENERATE =====
def generate_qr():
    upi_link = f"upi://pay?pa={UPI_ID}&pn={NAME}&cu=INR"
    img = qrcode.make(upi_link)
    bio = BytesIO()
    bio.name = "qr.png"
    img.save(bio, "PNG")
    bio.seek(0)
    return bio

# ===== HANDLE =====
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # PACKAGE SELECT
    if "Followers" in text:
        users[user_id] = {"package": text, "step": "username"}

        await update.message.reply_text("📌 Apna Instagram username bhejo:")

    # USERNAME
    elif user_id in users and users[user_id]["step"] == "username":
        users[user_id]["username"] = text
        users[user_id]["step"] = "payment"

        qr = generate_qr()

        await update.message.reply_photo(
            photo=qr,
            caption=f"💰 {users[user_id]['package']}\n\nUPI: {UPI_ID}\n\n📸 Payment karke screenshot bhejo"
        )

    # SCREENSHOT / PAYMENT
    elif update.message.photo:
        await context.bot.forward_message(
            chat_id=ADMIN_ID,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )

        await update.message.reply_text("✅ Payment received! Admin verify karega.")

    # SUPPORT
    elif "Support" in text:
        await update.message.reply_text("❓ Apni problem likho:")

    # DEFAULT
    else:
        await update.message.reply_text("⚠️ Please valid option select karo.")

# ===== ADMIN VERIFY =====
async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if context.args:
        user_id = int(context.args[0])

        await context.bot.send_message(
            chat_id=user_id,
            text="🎉 Payment verified! Followers jaldi deliver honge."
        )

# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("verify", verify))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
