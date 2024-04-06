import os
import time
import psutil

import art
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, JobQueue, CallbackContext
import requests

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')


async def show_processes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    processes = ""
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cmdline']):
        if proc.info['cmdline'] is not None and 'main.py' in proc.info['cmdline']:
            processes += f"PID: {proc.info['pid']}, Name: {proc.info['name']}, Username: {proc.info['username']}\n"
    if update.message is not None:
        if len(processes) > 0:
            await update.message.reply_text(processes)
        else:
            await update.message.reply_text('No processes related to this program are currently running.')


def check_price(cryptocurrency: str, cryptocurrency_pair: str):
    cryptocurrency = cryptocurrency.upper()
    cryptocurrency_pair = cryptocurrency_pair.upper()
    symbol = cryptocurrency + cryptocurrency_pair
    price_url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(price_url)
    data = response.json()
    if 'price' in data:
        return float(data['price'])
    else:
        raise ValueError("Price data not found in API response")


async def set_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global target_price
    global target_currency
    global target_currency_pair
    if len(context.args) < 3:
        if update.message is not None:
            await update.message.reply_text(
                'Please provide a price and currency pair, e.g. "/set_price 50000 BTC USDT".')
        return
    target_price = float(context.args[0])
    target_currency = context.args[1]
    target_currency_pair = context.args[2]
    if update.message is not None:
        await update.message.reply_text(
            f'Target price for {target_currency}/{target_currency_pair} set to {target_price}. Starting to monitor price...')
    context.job_queue.run_repeating(monitor_price, interval=1, first=0,
                                    context={"cryptocurrency": target_currency,
                                             "cryptocurrency_pair": target_currency_pair})


async def monitor_price(context: CallbackContext) -> None:
    cryptocurrency = context.job.context["cryptocurrency"]
    cryptocurrency_pair = context.job.context["cryptocurrency_pair"]
    current_price = check_price(cryptocurrency, cryptocurrency_pair)
    if current_price < target_price:
        await context.bot.send_message(chat_id=context.job.context['chat_id'],
                                       text="The current price is below the target price!")


async def alert_command(price: float, cryptocurrency: str, cryptocurrency_pair: str, context: ContextTypes.DEFAULT_TYPE):
    await set_price(price, context)
    if context.job is not None:
        context.job.context["cryptocurrency"] = cryptocurrency
        context.job.context["cryptocurrency_pair"] = cryptocurrency_pair
    await monitor_price(context)


async def alert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 3:
        if update.message is not None:
            await update.message.reply_text('Please provide three arguments, e.g. "/alert 50000 BTC USDT".')
        return
    price, cryptocurrency, cryptocurrency_pair = context.args
    await alert_command(float(price), cryptocurrency, cryptocurrency_pair, context)
    if update.message is not None:
        await update.message.reply_text(f'Alert set for {cryptocurrency}/{cryptocurrency_pair} at price {price}.')


def binance_request_price(cryptocurrency: str, cryptocurrency_pair: str):
    cryptocurrency = cryptocurrency.upper()
    cryptocurrency_pair = cryptocurrency_pair.upper()
    symbol = cryptocurrency + cryptocurrency_pair
    price_url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(price_url)
    data = response.json()
    if 'price' in data:
        price = data['price']
        return price
    else:
        raise ValueError("Price data not found in API response")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ascii_art = art.text2art("TelegramBot, by tinesime")
    print(ascii_art)
    await update.message.reply_text('Hello! I am your cryptocurrency bot. You can get the price of a cryptocurrency '
                                    'pair by sending a message like "/get_price BTC USDT".')


async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        if update.message is not None:
            await update.message.reply_text('Please provide two arguments, e.g. "/get_price BTC USDT".')
        return
    cryptocurrency, cryptocurrency_pair = context.args
    price = binance_request_price(cryptocurrency, cryptocurrency_pair)
    if update.message is not None:
        await update.message.reply_text(f'The price of {cryptocurrency}/{cryptocurrency_pair} is {price}')


app = ApplicationBuilder().token(API_TOKEN).build()
app.add_handler(CommandHandler("get_price", get_price))
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("alert", alert))
app.add_handler(CommandHandler("show_processes", show_processes))

app.run_polling()
