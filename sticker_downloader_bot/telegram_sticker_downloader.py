import os
import logging
import zipfile
import asyncio
import traceback
import httpx
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from static_methods import create_unique_directory, convert_tgs_to_gif, convert_tgs_to_png, convert_tgs_to_webp, convert_tgs_to_lottie, split_files_into_directories
import shutil

# Load environment variables from .env file
load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN_STICKER')

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def retry_async(func, *args, retries=5, delay=1, **kwargs):
    """Retry an async function with exponential backoff."""
    for attempt in range(retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error on attempt {attempt + 1} for {func.__name__}: {e}\n{traceback.format_exc()}")
            if attempt < retries - 1:
                await asyncio.sleep(delay * 2 ** attempt)
            else:
                raise

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    context.user_data.clear()
    logger.info(f"User {chat_id} started a new session.")
    await context.bot.send_message(
        chat_id=chat_id,
        text="Send me an animated sticker and I'll download the entire sticker set as a ZIP file."
    )

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    context.user_data.clear()
    logger.info(f"User {chat_id} stopped the current download.")
    await context.bot.send_message(chat_id=chat_id, text="Current download stopped.")

async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sticker = update.message.sticker
    chat_id = update.effective_chat.id
    if sticker and sticker.is_animated:
        try:
            logger.info(f"Received animated sticker from {chat_id}. Fetching sticker set...")
            context.user_data['sticker_set_name'] = sticker.set_name
            context.user_data['sticker'] = sticker
            await context.bot.send_message(
                chat_id=chat_id,
                text="Do you want to download just this sticker or the whole set?",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Just this one", callback_data="just_one")],
                        [InlineKeyboardButton("Whole set", callback_data="whole_set")]
                    ]
                )
            )
        except Exception as e:
            logger.error(f"Error handling sticker: {e}\n{traceback.format_exc()}")
            await context.bot.send_message(chat_id=chat_id, text="An error occurred while processing the sticker.")
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Please send an animated sticker."
        )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data

    if action in ["just_one", "whole_set"]:
        context.user_data['download_type'] = action
        await query.edit_message_text(text="Choose the format:")
        await query.message.reply_text(
            text="Choose the format:",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("PNG", callback_data="format_png"), InlineKeyboardButton("WEBP", callback_data="format_webp")],
                    [InlineKeyboardButton("GIF", callback_data="format_gif"), InlineKeyboardButton("LOTTIE", callback_data="format_lottie")],
                    [InlineKeyboardButton("Download All", callback_data="format_all")]
                ]
            )
        )
    elif action.startswith("format_"):
        format = action.split("_")[1]
        await handle_download(query, context, format)

async def handle_download(query, context, format):
    chat_id = query.message.chat_id
    download_type = context.user_data.get('download_type')
    sticker_set_name = context.user_data.get('sticker_set_name')
    base_name = sticker_set_name

    try:
        if download_type == "just_one":
            await context.bot.send_message(chat_id=chat_id, text=f"Downloading the sticker in {format} format...")
            sticker = context.user_data['sticker']
            await download_and_send_sticker(context, chat_id, sticker, format, base_name)
        elif download_type == "whole_set":
            await context.bot.send_message(chat_id=chat_id, text=f"Downloading the whole set '{sticker_set_name}' in {format} format...")
            sticker_set = await context.bot.get_sticker_set(sticker_set_name)
            await download_and_send_sticker_set(context, chat_id, sticker_set, format, base_name)
    except Exception as e:
        logger.error(f"Error downloading sticker(s): {e}\n{traceback.format_exc()}")
        await context.bot.send_message(chat_id=chat_id, text="An error occurred while downloading the sticker(s).")

async def download_and_send_sticker(context, chat_id, sticker, format, base_name):
    dir_path = create_unique_directory(base_name)
    sticker_file = await retry_async(sticker.get_file)
    sticker_path = os.path.join(dir_path, f"{base_name}_1.tgs")
    await retry_async(sticker_file.download_to_drive, sticker_path)

    if format == "gif":
        output_path = convert_tgs_to_gif(sticker_path, dir_path, base_name, 1)
        zip_path = os.path.join(dir_path, f"{base_name}.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(output_path, os.path.basename(output_path))
        await send_zip_file(context, chat_id, zip_path)
        os.remove(output_path)
    elif format == "png":
        output_path = convert_tgs_to_png(sticker_path, dir_path, base_name, 1)
        await context.bot.send_document(chat_id=chat_id, document=open(output_path, 'rb'), filename=os.path.basename(output_path))
        os.remove(output_path)
    elif format == "webp":
        output_path = convert_tgs_to_webp(sticker_path, dir_path, base_name, 1)
        zip_path = os.path.join(dir_path, f"{base_name}.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(output_path, os.path.basename(output_path))
        await send_zip_file(context, chat_id, zip_path)
        os.remove(output_path)
    elif format == "lottie":
        output_path = convert_tgs_to_lottie(sticker_path, dir_path, base_name, 1)
        await context.bot.send_document(chat_id=chat_id, document=open(output_path, 'rb'), filename=os.path.basename(output_path))
        os.remove(output_path)
    elif format == "all":
        gif_path = convert_tgs_to_gif(sticker_path, dir_path, base_name, 1)
        png_path = convert_tgs_to_png(sticker_path, dir_path, base_name, 1)
        webp_path = convert_tgs_to_webp(sticker_path, dir_path, base_name, 1)
        lottie_path = convert_tgs_to_lottie(sticker_path, dir_path, base_name, 1)
        zip_path = os.path.join(dir_path, f"{base_name}.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(gif_path, os.path.basename(gif_path))
            zipf.write(png_path, os.path.basename(png_path))
            zipf.write(webp_path, os.path.basename(webp_path))
            zipf.write(lottie_path, os.path.basename(lottie_path))
        await send_zip_file(context, chat_id, zip_path)
        os.remove(gif_path)
        os.remove(png_path)
        os.remove(webp_path)
        os.remove(lottie_path)
    else:
        output_path = sticker_path  # Handle other formats as needed

    os.remove(sticker_path)
    os.rmdir(dir_path)

async def download_and_send_sticker_set(context, chat_id, sticker_set, format, base_name):
    dir_path = create_unique_directory(base_name)
    temp_dir = os.path.join(dir_path, "temp")
    os.makedirs(temp_dir)

    for index, sticker in enumerate(sticker_set.stickers, start=1):
        if sticker.is_animated:
            try:
                sticker_file = await retry_async(sticker.get_file)
                sticker_path = os.path.join(temp_dir, f"{base_name}_{index}.tgs")
                await retry_async(sticker_file.download_to_drive, sticker_path)

                if format == "gif":
                    convert_tgs_to_gif(sticker_path, temp_dir, base_name, index)
                elif format == "png":
                    convert_tgs_to_png(sticker_path, temp_dir, base_name, index)
                elif format == "webp":
                    convert_tgs_to_webp(sticker_path, temp_dir, base_name, index)
                elif format == "lottie":
                    convert_tgs_to_lottie(sticker_path, temp_dir, base_name, index)
                elif format == "all":
                    convert_tgs_to_gif(sticker_path, temp_dir, base_name, index)
                    convert_tgs_to_png(sticker_path, temp_dir, base_name, index)
                    convert_tgs_to_webp(sticker_path, temp_dir, base_name, index)
                    convert_tgs_to_lottie(sticker_path, temp_dir, base_name, index)
                else:
                    pass  # Handle other formats as needed
            except Exception as e:
                logger.error(f"Error downloading sticker: {e}\n{traceback.format_exc()}")
                continue

    split_dir = os.path.join(dir_path, "split")
    split_files_into_directories(temp_dir, split_dir, max_size_mb=49)

    for split_subdir in os.listdir(split_dir):
        split_subdir_path = os.path.join(split_dir, split_subdir)
        zip_path = os.path.join(dir_path, f"{base_name}_{split_subdir}.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, _, files in os.walk(split_subdir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, split_subdir_path))
        await send_zip_file(context, chat_id, zip_path)

    shutil.rmtree(temp_dir)
    shutil.rmtree(split_dir)

async def send_zip_file(context, chat_id, zip_path):
    await context.bot.send_document(chat_id=chat_id, document=open(zip_path, 'rb'), filename=os.path.basename(zip_path))
    os.remove(zip_path)

async def retry_task(task, *args, retries=5, delay=1, **kwargs):
    for attempt in range(retries):
        try:
            return await task(*args, **kwargs)
        except (httpx.ReadError, Exception) as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}\n{traceback.format_exc()}")
            if attempt + 1 == retries:
                raise

def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    start_handler = CommandHandler('start', start)
    stop_handler = CommandHandler('stop', stop)
    sticker_handler = MessageHandler(filters.Sticker.ALL, handle_sticker)
    callback_handler = CallbackQueryHandler(handle_callback)

    application.add_handler(start_handler)
    application.add_handler(stop_handler)
    application.add_handler(sticker_handler)
    application.add_handler(callback_handler)

    logger.info("Bot started.")
    application.run_polling()

if __name__ == '__main__':
    main()
