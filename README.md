# TelegramBot

## Description
This is a Telegram bot developed in Python. It uses the Binance API to fetch cryptocurrency prices and responds to various commands.

## Features
- Fetches real-time cryptocurrency prices.
- Responds to commands like `get_price`, `start`, `alert`, and `show_processes`.

## Setup and Installation
1. Clone the repository.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Set up your `.env` file with your Binance API keys and Telegram bot token.
4. Run the bot using `python main.py`.

## Commands
- `/get_price <cryptocurrency> <cryptocurrency_pair>`: Fetches the real-time price of the specified cryptocurrency pair.
- `/start`: Starts the bot.
- `/alert`: Alerts the user when a specified price is reached.
- `/show_processes`: Shows the current running processes of the bot.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)