import os
import qrcode
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7705209352
UPI_ID = "niteshextema@fam"

# ===== QR GENERATE =====
def generate_qr():
    upi_link = f"upi://pay?pa={UPI_ID}&pn=Payment"
    qr = qrcode.make(upi_link)
    qr.save("qr.png")

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1K Followers - ₹10", callback_data="1k")],
        [InlineKeyboardButton("5K Followers - ₹50", callback_data="5k")],
        [InlineKeyboardButton("10K Followers - ₹100", callback_data="10k")],
        [InlineKeyboardButton("Payment Screenshot", callback_data="pay")],
        [InlineKeyboardButton("Support", callback_data="support")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome! Choose option:", reply_markup=reply_markup)

# ===== BUTTON =====
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data in ["1k", "5k", "10k"]:
        await query.message.reply_text("Send your username:")
        context.user_data["step"] = "username"

    elif query.data == "pay":
        generate_qr()
        await query.message.reply_photo(photo=open("qr.png", "rb"), caption="Pay and send screenshot")

    elif query.data == "support":
        await query.message.reply_text("Write your problem here:")
        context.user_data["step"] = "support"

# ===== MESSAGE =====
async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("step") == "username":
        context.user_data["username"] = update.message.text
        await update.message.reply_text("Now send payment screenshot")
        context.user_data["step"] = "screenshot"

    elif context.user_data.get("step") == "support":
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"Support: {update.message.text}")
        await update.message.reply_text("Sent to admin ✅")
        context.user_data["step"] = None

# ===== PHOTO =====
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("step") == "screenshot":
        file = await update.message.photo[-1].get_file()
        await file.download_to_drive("payment.jpg")

        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=open("payment.jpg", "rb"),
            caption=f"Payment from @{update.message.from_user.username}"
        )

        await update.message.reply_text("Payment submitted! Wait for admin approval ✅")
        context.user_data["step"] = None

# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT, message))
    app.add_handler(MessageHandler(filters.PHOTO, photo))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
