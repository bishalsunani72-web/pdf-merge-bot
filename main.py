import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from pypdf import PdfReader, PdfWriter

TOKEN = os.getenv("BOT_TOKEN")

user_files = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "PDF bhejo.\nSab bhejne ke baad /merge likho.\n\nCrystal clear merge hoga 💎"
    )

async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_files:
        user_files[user_id] = []

    file = await update.message.document.get_file()
    file_path = f"{user_id}_{update.message.document.file_name}"
    await file.download_to_drive(file_path)

    user_files[user_id].append(file_path)

    await update.message.reply_text("PDF added ✅")

async def merge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_files or not user_files[user_id]:
        await update.message.reply_text("Pehle PDF bhejo.")
        return

    writer = PdfWriter()

    for pdf_path in user_files[user_id]:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            writer.add_page(page)

    output_file = f"{user_id}_merged.pdf"

    with open(output_file, "wb") as f:
        writer.write(f)

    await update.message.reply_document(document=open(output_file, "rb"))

    for pdf in user_files[user_id]:
        os.remove(pdf)

    os.remove(output_file)
    user_files[user_id] = []

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("merge", merge))
app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))

app.run_polling()
