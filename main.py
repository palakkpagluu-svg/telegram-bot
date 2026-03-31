import logging
import qrcode
from telegram import Update, ReplyKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "YOUR_BOT_TOKEN"
ADMIN_ID = 7705209352
UPI_ID = "niteshextema@fam"
NAME = "Nitesh"

user_data_store = {}

def generate_qr():
    upi_link = f"upi://pay?pa={UPI_ID}&pn={NAME}"
    qr = qrcode.make(upi_link)
    qr.save("qr.png")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["1K Followers - ₹10"],
        ["5K Followers - ₹50"],
        ["10K Followers - ₹100"],
        ["💬 Support"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text("🔥 Welcome!\n\nChoose a package:", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "Followers" in text:
        user_data_store[update.effective_user.id] = text
        generate_qr()

        await update.message.reply_photo(
            photo=InputFile("qr.png"),
            caption=f"💰 Pay for {text}\n\n📸 Payment ke baad screenshot bhejo"
        )

    elif "Support" in text:
        await update.message.reply_text("❓ Problem hai? Yaha likho.")

    else:
        await context.bot.forward_message(
            chat_id=ADMIN_ID,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )

        await update.message.reply_text("✅ Payment received! Verification pending.")

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if context.args:
        user_id = int(context.args[0])
        await context.bot.send_message(
            chat_id=user_id,
            text="🎉 Payment verified! Followers will be delivered soon."
        )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("verify", verify))
    app.add_handler(MessageHandler(filters.ALL, handle_message))

    print("🤖 Bot running...")
    app.run_polling()
