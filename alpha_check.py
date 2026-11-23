import json
import os
import requests

BOT_TOKEN = os.environ["TG_TOKEN"]
CHAT_ID = os.environ["TG_CHAT"]
STATE_FILE = "known_tokens.json"

ALPHA_URL = (
    "https://www.binance.com/bapi/defi/v1/public/"
    "wallet-direct/buw/wallet/cex/alpha/all/token/list"
)
HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_tokens():
    r = requests.get(ALPHA_URL, headers=HEADERS, timeout=20)
    r.raise_for_status()
    data = r.json().get("data", [])
    tokens = {}
    for t in data:
        key = t.get("alphaId") or f"{t.get('chainId')}:{t.get('contractAddress')}"
        tokens[key] = {
            "symbol": t.get("symbol", "?"),
            "name": t.get("name", "?"),
            "chain": t.get("chainName", "?"),
        }
    return tokens


def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=20)


def main():
    tokens = fetch_tokens()
    if not tokens:
        print("القائمة فاضية، تخطي.")
        return

    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(tokens.keys()), f)
        send("✅ البوت اشتغل وبيراقب Binance Alpha")
        return

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        known = set(json.load(f))

    new_keys = set(tokens) - known
    for k in new_keys:
        t = tokens[k]
        send(
            f"🚨 عملة جديدة على Binance Alpha\n"
            f"الاسم: {t['name']}\n"
            f"الرمز: {t['symbol']}\n"
            f"الشبكة: {t['chain']}"
        )

    if new_keys:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(known | new_keys), f)


if __name__ == "__main__":
    main()
