# Telegram Animated Sticker Bot

This Telegram bot allows users to convert animated stickers (`.tgs` files) into various formats (GIF, PNG, WEBP, LOTTIE) and download them either individually or as a whole set. The bot can also handle splitting large sticker sets into multiple zip files to ensure that each zip file does not exceed 49MB.

## Features

- Convert animated stickers to GIF, PNG, WEBP, or LOTTIE format.
- Download a single sticker or an entire sticker set.
- Automatically split large sticker sets into multiple zip files if they exceed 49MB.

## Requirements

- Python 3.8+
- Telegram Bot API token
- RLottie Python library
- httpx library
- python-dotenv library
- python-telegram-bot library

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/telegram-sticker-bot.git
cd telegram-sticker-bot
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project directory and add your Telegram Bot API token:

```env
TELEGRAM_TOKEN_STICKER=your_telegram_bot_token
```

4. Run the bot:

```bash
python telegram_bot.py
```

## Usage

1. Start the bot on Telegram by sending the `/start` command.
2. Send an animated sticker to the bot.
3. Choose whether to download just the sticker or the whole set.
4. Select the desired format (GIF, PNG, WEBP, LOTTIE, or All).
5. The bot will process your request and send you the converted files or a zip file containing the entire sticker set.

## Code Structure

- `statistics_methods.py`: Contains methods for converting `.tgs` files to various formats and splitting files into directories based on size.
- `telegram_bot.py`: Contains the main logic for the Telegram bot, including handling user commands and interactions.

## Methods

### `statistics_methods.py`

- `create_unique_directory(base_name)`: Creates a unique directory for storing output files.
- `convert_tgs_to_gif(input_path, output_dir, base_name, index)`: Converts a `.tgs` file to GIF format.
- `convert_tgs_to_png(input_path, output_dir, base_name, index)`: Converts a `.tgs` file to PNG format.
- `convert_tgs_to_webp(input_path, output_dir, base_name, index)`: Converts a `.tgs` file to WEBP format.
- `convert_tgs_to_lottie(input_path, output_dir, base_name, index)`: Converts a `.tgs` file to LOTTIE format.
- `split_files_into_directories(src_dir, dest_dir, max_size_mb=49)`: Splits files into directories not exceeding the specified size.

### `telegram_bot.py`

- `start(update, context)`: Handles the `/start` command.
- `stop(update, context)`: Handles the `/stop` command.
- `handle_sticker(update, context)`: Handles incoming stickers.
- `handle_callback(update, context)`: Handles callback queries from inline keyboard buttons.
- `handle_download(query, context, format)`: Handles the download process based on user selection.
- `download_and_send_sticker(context, chat_id, sticker, format, base_name)`: Downloads and sends a single sticker in the specified format.
- `download_and_send_sticker_set(context, chat_id, sticker_set, format, base_name)`: Downloads and sends an entire sticker set in the specified format.
- `send_zip_file(context, chat_id, zip_path)`: Sends a zip file to the user.

## License

This project is licensed under the MIT License.
```

Feel free to customize the `README.md` file according to your specific needs and project details.
