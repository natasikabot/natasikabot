import telebot
import requests
import time

# === ТВОЙ TELEGRAM ТОКЕН ===
TOKEN = "7579221769:AAF21MsH9VGD7_Cc1kMAVrxONhDn8Qitk1A"
bot = telebot.TeleBot(TOKEN)

# === Настройки ===
PAIR = "BTCUSDT"
RSI_PERIOD = 14
EMA_SHORT = 50
EMA_LONG = 200


def get_klines(symbol="BTCUSDT", interval="3m", limit=200):
url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={symbol}&interval={interval}&limit={limit}"
response = requests.get(url).json()
return [float(i['close']) for i in response['result']['list'][::-1]]


def calculate_rsi(data, period=14):
gains = []
losses = []
for i in range(1, len(data)):
change = data[i] - data[i - 1]
gains.append(max(change, 0))
losses.append(abs(min(change, 0)))
avg_gain = sum(gains[:period]) / period
avg_loss = sum(losses[:period]) / period
rsi_values = []
for i in range(period, len(data)):
avg_gain = (avg_gain * (period - 1) + gains[i]) / period
avg_loss = (avg_loss * (period - 1) + losses[i]) / period
rs = avg_gain / avg_loss if avg_loss != 0 else 0
rsi = 100 - (100 / (1 + rs))
rsi_values.append(rsi)
return rsi_values[-1]


def send_signal(message):
bot.send_message(chat_id="770009158", text=message)


@bot.message_handler(commands=['start'])
def start(message):
bot.send_message(message.chat.id, "✅ Бот запущен. Жду сигналов...")


def main_loop():
while True:
prices = get_klines(PAIR)
rsi = calculate_rsi(prices, RSI_PERIOD)
ema50 = sum(prices[-EMA_SHORT:]) / EMA_SHORT
ema200 = sum(prices[-EMA_LONG:]) / EMA_LONG

# --- RSI сигналы ---
if rsi < 30:
send_signal(f"💚 {PAIR}: RSI={rsi:.2f} — возможный ЛОНГ 📈")
elif rsi > 70:
send_signal(f"❤️ {PAIR}: RSI={rsi:.2f} — возможный ШОРТ 📉")

# --- EMA пересечение ---
if ema50 > ema200:
trend = "📊 Тренд бычий (ищем лонги)"
else:
trend = "📉 Тренд медвежий (ищем шорты)"
send_signal(trend)

time.sleep(180) # Проверка каждые 3 минуты


if __name__ == "__main__":
main_loop()
