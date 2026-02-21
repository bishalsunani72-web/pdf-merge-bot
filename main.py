import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from pypdf import PdfReader, PdfWriter
from PIL import Image

TOKEN = os.getenv("BOT_TOKEN")

user_files = {}
user_images = {}

# -------------------- START --------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send PDFs to merge.\nAfter sending all, type /merge\n\n"
        "Send Images to convert into PDF.\nAfter sending all, type /imgpdf\n\n"
        "💎 Crystal clear output guaranteed."
    )

# -------------------- PDF MERGE --------------------

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
        await update.message.reply_text("Send PDFs first.")
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

# -------------------- IMAGE COLLECT --------------------

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_images:
        user_images[user_id] = []

    photo = update.message.photo[-1]  # highest resolution
    file = await photo.get_file()

    image_path = f"{user_id}_{len(user_images[user_id])}.png"
    await file.download_to_drive(image_path)

    user_images[user_id].append(image_path)
    await update.message.reply_text("Image added ✅\nAfter sending all images type /imgpdf")

# -------------------- IMAGE TO PDF --------------------

async def img_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_images or not user_images[user_id]:
        await update.message.reply_text("Send images first.")
        return

    image_list = []

    for img_path in user_images[user_id]:
        img = Image.open(img_path)

        if img.mode != "RGB":
            img = img.convert("RGB")

        image_list.append(img)

    output_file = f"{user_id}_images.pdf"

    image_list[0].save(
        output_file,
        save_all=True,
        append_images=image_list[1:],
        resolution=300.0
    )

    await update.message.reply_document(document=open(output_file, "rb"))

    for img_path in user_images[user_id]:
        os.remove(img_path)

    os.remove(output_file)
    user_images[user_id] = []

# -------------------- RUN APP --------------------

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("merge", merge))
app.add_handler(CommandHandler("imgpdf", img_to_pdf))
app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
app.add_handler(MessageHandler(filters.PHOTO, handle_image))

app.run_polling()
