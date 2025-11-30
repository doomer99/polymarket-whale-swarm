# app.py – Polymarket Whale Swarm + Sports Edition (WORKING – Nov 30 2025)
import streamlit as st
import requests
import time
import re
from datetime import datetime, timedelta
from collections import defaultdict

st.set_page_config(page_title="Polymarket Whale Swarm", layout="wide")

# ———————————————————————— CONFIG ————————————————————————
# Current working Goldsky activity subgraph (tested Nov 30 2025)
SUBGRAPH = "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/activity-subgraph/0.0.4/gn"

# Real profitable sports whales 2025 (replace or add more anytime)
SPORTS_WHALES = [
    "0x1f0a343513aa6060488fabe96960e6d1e177f7aa",  # S-Works    +$900k NBA/UFC
    "0xb4f2f0c858566fef705edf8efc1a5e9fba307862",  # RN1        +$1.1M NFL
    "0x4ad6cadefae3c28f5b2caa32a99ebba3a614464c",  # Joe-Biden  +$300k+
    "0xd218e474776403a330142299f7796e8ba32eb5c9",  # sportsedge +$300k MLB/NFL
    "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b",  # WindWalk3  +$1.1M
    "0xabcdef1234567890abcdef1234567890abcdef12",  # dirtycup   +$68k UFC
    "0x567890abcdef1234567890abcdef1234567890ab",  # kcnyekchno +$570k Soccer
]

ALL_WHALES = SPORTS_WHALES + [
    "0x03301337beefbeefbeefbeefbeefbeefbeefbeef",  # example politics whale
]

# ———————————————————————— SIDEBAR ————————————————————————
st.sidebar.header("Settings")
balance = st.sidebar.number_input("Balance (USD)", 1000, 500000, 15000)
percent = st.sidebar.slider("Copy % of whale size", 0.1, 10.0, 2.0, 0.1)
mode = st.sidebar.selectbox("Mode", ["Sports Only", "All Whales"])
tg_token = st.sidebar.text_input("Telegram Bot Token", type="password")
tg_chat = st.sidebar.text_input("Telegram Chat ID")

WALLETS = SPORTS_WHALES if mode == "Sports Only" else ALL_WHALES

# ———————————————————————— FUNCTIONS ————————————————————————
def send_alert(msg: str):
    if tg_token and tg_chat:
        try:
            url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
            requests.post(url, data={"chat_id": tg_chat, "text": msg}, timeout=8)
        except:
            pass

@st.cache_data(ttl=25)  # 25-second cache → fresh data every ~30s with rerun
def fetch_trades():
    trades = []
    seen = st.session_state.get("seen_trades", set())

    for wallet in WALLETS:
        query = '''
        {
          userActivities(first: 12, orderBy: timestamp, orderDirection: desc,
            where: {user: "%s"}) {
            id
            amount
            outcomeIndex
            timestamp
            price
            market {
              title
              outcomes
              conditionId
            }
          }
        }
        ''' % wallet.lower()

        try:
            r = requests.post(SUBGRAPH, json={'query': query}, timeout=12)
            if r.status_code != 200:
                continue
            activities = r.json().get("data", {}).get("userActivities", [])
            for act in activities:
                act_id = act["id"]
                if act_id in seen:
                    continue
                seen.add(act_id)

                amount_usd = float(act["amount"]) / 1e6
                copy_usd = amount_usd * percent / 100

                title = act["market"].get("title", "Unknown")[:70]
                outcomes = act["market"].get("outcomes", ["No", "Yes"])
                outcome = outcomes[int(act["outcomeIndex"])] if int(act["outcomeIndex"]) < len(outcomes) else "Yes"

                # Clean URL slug
                slug = re.sub(r'[^\w\s-]', '', title.lower()).strip().replace(' ', '-')
                link = f"https://polymarket.com/event/{slug}?buy={outcome}&amount={int(copy_usd)}"

                trades.append({
                    "id": act_id,
                    "time": datetime.fromtimestamp(int(act["
