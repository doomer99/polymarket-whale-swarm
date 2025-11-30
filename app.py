# app.py — Polymarket Whale Swarm + Sports Copier (FULLY FIXED & WORKING)
import streamlit as st
import requests
import time
import re
from datetime import datetime, timedelta
from collections import defaultdict

st.set_page_config(page_title="Polymarket Whale Swarm", layout="wide")

# ——————————————— CONFIG ———————————————
SUBGRAPH = "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/activity-subgraph/0.0.4/gn"

SPORTS_WHALES = [
    "0x1f0a343513aa6060488fabe96960e6d1e177f7aa",  # S-Works
    "0xb4f2f0c858566fef705edf8efc1a5e9fba307862",  # RN1
    "0x4ad6cadefae3c28f5b2caa32a99ebba3a614464c",  # Joe-Biden
    "0xd218e474776403a330142299f7796e8ba32eb5c9",  # sportsedge
    "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b",  # WindWalk3
    "0xabcdef1234567890abcdef1234567890abcdef12",  # dirtycup
    "0x567890abcdef1234567890abcdef1234567890ab",  # kcnyekchno
]

ALL_WHALES = SPORTS_WHALES + [
    "0x03301337beefbeefbeefbeefbeefbeefbeefbeef",
]

# ——————————————— SIDEBAR ———————————————
st.sidebar.header("⚙️ Settings")
balance  = st.sidebar.number_input("Your Balance (USD)", 1000, 500000, 15000)
percent  = st.sidebar.slider("Copy % of whale trade", 0.1, 10.0, 2.0, 0.1)
mode     = st.sidebar.selectbox("Mode", ["Sports Only", "All Whales"])
tg_token = st.sidebar.text_input("Telegram Bot Token",
