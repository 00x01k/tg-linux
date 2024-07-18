import logging
import subprocess
import telebot
from telebot import types
import time
import signal
import sys
import asyncio
from babel import Locale
from flask import Flask, render_template

# Replace with your Telegram bot token
bot_token = "XXXXXXXXX:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"

# Replace with your user ID (integer)
user_id = 123456789  # Update with your user ID

# Initialize the bot
bot = telebot.TeleBot(bot_token)

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Handler for text messages
@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.chat.id == user_id:  # Check if message is from authorized user
        command = message.text.strip()  # Get the command text
        markup = types.InlineKeyboardMarkup()  # Create inline keyboard
        button = types.InlineKeyboardButton(text="Repeat", callback_data=command)  # Create a button
        markup.add(button)  # Add button to keyboard
        try:
            output = execute_command(command)  # Execute command
            bot.send_message(user_id, output, reply_markup=markup)  # Send command output with keyboard
        except Exception as e:
            bot.send_message(user_id, f"Error: {str(e)}")  # Send error message if command fails

# Handler for callback queries (button presses)
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    command = call.data  # Get command from callback data
    markup = types.InlineKeyboardMarkup()  # Create inline keyboard
    button = types.InlineKeyboardButton(text="Repeat", callback_data=command)  # Create a button
    markup.add(button)  # Add button to keyboard
    try:
        output = execute_command(command)  # Execute command
        bot.send_message(user_id, output, reply_markup=markup)  # Send command output with keyboard
    except Exception as e:
        bot.send_message(user_id, f"Error: {str(e)}")  # Send error message if command fails

# Handler for Ctrl+C
def signal_handler(sig, frame):
    logging.info('Stopping bot...')
    bot.stop_polling()
    sys.exit(0)

# Main function to start the bot
def main():
    signal.signal(signal.SIGINT, signal_handler)  # Assign the signal handler for Ctrl+C
    while True:
        try:
            bot.polling(none_stop=True)  # Start polling for updates
        except Exception as e:
            logging.error(f"Error in main loop: {str(e)}")
            time.sleep(10)  # Sleep and retry if polling fails

# Helper function to execute commands securely
def execute_command(command):
    try:
        result = subprocess.run(command.split(), capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "Timeout occurred while executing the command."
    except Exception as e:
        return f"Error: {str(e)}"

# Flask web interface for administration
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    main()  # Run the main function
