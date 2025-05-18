import ccxt
import pandas as pd
import time
import requests
import ta

# === CONFIGURACIÓN TELEGRAM ===
TOKEN = "7952245288:AAEsnf6Kvyel9gtm67RZP_JeGptXxM1cH_0"
CHAT_ID = "7344543544"

# === PARES A ANALIZAR ===
pares = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "PEPE/USDT"]

# === CONECTAR A BINANCE ===
exchange = ccxt.binance({
    'enableRateLimit': True,
})

# === FUNCIÓN: Enviar mensaje a Telegram ===
def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensaje}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Error al enviar Telegram:", e)

# === FUNCIÓN: Analizar cada par ===
def analizar_par(par):
    try:
        ohlcv = exchange.fetch_ohlcv(par, timeframe='1m', limit=100)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

        df['rsi'] = ta.momentum.RSIIndicator(close=df['close']).rsi()
        df['ema20'] = ta.trend.EMAIndicator(close=df['close'], window=20).ema_indicator()
        df['ema50'] = ta.trend.EMAIndicator(close=df['close'], window=50).ema_indicator()

        precio = df['close'].iloc[-1]
        rsi = df['rsi'].iloc[-1]
        ema20 = df['ema20'].iloc[-1]
        ema50 = df['ema50'].iloc[-1]

        # Señal de compra
        if rsi < 30 and ema20 > ema50:
            mensaje = (
                f"🟢 Señal de COMPRA detectada\n"
                f"Par: {par}\n"
                f"Precio: ${precio:.2f}\n"
                f"RSI: {rsi:.2f}\nEMA20: {ema20:.2f} | EMA50: {ema50:.2f}\n"
                f"Confianza: Alta"
            )
            enviar_telegram(mensaje)

        # Señal de venta
        elif rsi > 70 and ema20 < ema50:
            mensaje = (
                f"🔴 Señal de VENTA detectada\n"
                f"Par: {par}\n"
                f"Precio: ${precio:.2f}\n"
                f"RSI: {rsi:.2f}\nEMA20: {ema20:.2f} | EMA50: {ema50:.2f}\n"
                f"Confianza: Alta"
            )
            enviar_telegram(mensaje)

    except Exception as e:
        print(f"Error analizando {par}:", e)

# === LOOP PRINCIPAL ===
while True:
    for par in pares:
        analizar_par(par)
    time.sleep(60)
