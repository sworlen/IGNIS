import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import os
import re
import html
import warnings
warnings.filterwarnings("ignore")
import requests

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="FinAnalyzer Pro 12.0",
    layout="wide",
    page_icon="◆",
    initial_sidebar_state="collapsed",
)

C = {
    "bg":        "#070b14",
    "bg2":       "#0d1526",
    "card":      "rgba(18, 28, 46, 0.72)",
    "border":    "rgba(125, 211, 252, 0.22)",
    "border2":   "rgba(148, 163, 184, 0.28)",
    "green":     "#22c55e",
    "green_d":   "rgba(34,197,94,0.16)",
    "red":       "#f43f5e",
    "red_d":     "rgba(244,63,94,0.14)",
    "blue":      "#38bdf8",
    "blue_d":    "rgba(56,189,248,0.16)",
    "purple":    "#a78bfa",
    "orange":    "#f59e0b",
    "t1":        "#e2e8f0",
    "t2":        "#94a3b8",
    "t3":        "#64748b",
    "grid":      "rgba(148,163,184,0.10)",
}

APP_VERSION = "12.0"

def with_alpha(color: str, alpha: float) -> str:
    alpha = max(0.0, min(1.0, alpha))
    if isinstance(color, str) and color.startswith("#") and len(color) == 7:
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        return f"rgba({r},{g},{b},{alpha})"
    if isinstance(color, str) and color.startswith("rgb(") and color.endswith(")"):
        vals = color[4:-1]
        return f"rgba({vals},{alpha})"
    return color

def sanitize_ticker_input(raw: str, default: str = "AAPL") -> str:
    """Keep ticker input stable and safe for yfinance calls."""
    if not isinstance(raw, str):
        return default
    candidate = raw.strip().upper().split()[0] if raw.strip() else ""
    candidate = re.sub(r"[^A-Z0-9\.\-\^]", "", candidate)
    return candidate[:12] if candidate else default

# ─────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

*, *::before, *::after {{ box-sizing: border-box; font-family: 'Inter', sans-serif; }}

.stApp {{
    background:
      radial-gradient(1200px 600px at 10% -10%, rgba(56,189,248,0.18), transparent 45%),
      radial-gradient(1000px 500px at 100% 0%, rgba(167,139,250,0.15), transparent 40%),
      linear-gradient(180deg, #060a12 0%, #0a1221 55%, #0b1324 100%);
    color: {C['t1']};
}}

/* Glass containers */
.fa-card {{
    background: {C['card']};
    border: 1px solid {C['border']};
    border-radius: 16px;
    padding: 16px 18px;
    margin-bottom: 10px;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(2, 8, 23, 0.35);
}}

/* buttons */
.stButton > button {{
    background: linear-gradient(180deg, rgba(30,41,59,0.7), rgba(15,23,42,0.7)) !important;
    color: {C['t1']} !important;
    border: 1px solid {C['border']} !important;
    border-radius: 12px !important;
    font-size: 0.86rem !important;
    font-weight: 600 !important;
    padding: 8px 14px !important;
    transition: all .18s ease !important;
    min-height: 44px !important;
    white-space: nowrap !important;
    line-height: 1.1 !important;
}}
.stButton > button:hover {{
    transform: translateY(-1px);
    border-color: {C['blue']} !important;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.14) !important;
}}
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, rgba(56,189,248,0.25), rgba(167,139,250,0.22)) !important;
    border-color: rgba(125,211,252,0.48) !important;
    color: #eaf6ff !important;
}}

/* inputs */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div {{
    background: rgba(15, 23, 42, 0.78) !important;
    border: 1px solid {C['border']} !important;
    color: {C['t1']} !important;
    border-radius: 12px !important;
}}
.stSelectbox [data-baseweb="select"] {{
    min-width: 160px !important;
}}

/* tabs */
.stTabs [data-baseweb="tab-list"] {{
    background: rgba(15,23,42,0.35);
    border: 1px solid {C['border']};
    border-radius: 12px;
    gap: 4px;
    padding: 4px;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: {C['t2']} !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.83rem !important;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, rgba(56,189,248,0.24), rgba(167,139,250,0.20)) !important;
    color: #dff4ff !important;
}}

/* metric */
[data-testid="stMetricValue"] {{ color: {C['t1']} !important; font-family: 'JetBrains Mono', monospace !important; }}
[data-testid="stMetricLabel"] {{ color: {C['t2']} !important; font-size: 0.78rem !important; }}

/* divider */
hr {{ border-color: rgba(148,163,184,0.2) !important; margin: 0.9rem 0 !important; }}

/* expander */
.streamlit-expanderHeader {{
    color: {C['t1']} !important;
    background: rgba(15, 23, 42, 0.7) !important;
    border: 1px solid {C['border']} !important;
    border-radius: 12px !important;
}}
.streamlit-expanderContent {{ background: transparent !important; border-radius: 0 0 12px 12px !important; }}

/* scrollbar */
::-webkit-scrollbar {{ width: 8px; height: 8px; }}
::-webkit-scrollbar-track {{ background: rgba(15,23,42,0.7); }}
::-webkit-scrollbar-thumb {{ background: rgba(100,116,139,0.55); border-radius: 6px; }}

/* hide streamlit chrome */
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 0.7rem !important; max-width: 1500px; }}

/* badges/text helpers */
.fa-pill {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    margin: 2px;
}}
.g {{ color: {C['green']}; font-weight: 700; }}
.r {{ color: {C['red']}; font-weight: 700; }}
.b {{ color: {C['blue']}; font-weight: 700; }}
.mono {{ font-family: 'JetBrains Mono', monospace; }}
.grad {{
    background: linear-gradient(135deg, #7dd3fc 0%, #a78bfa 45%, #22d3ee 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800;
    letter-spacing: 0.01em;
}}
.status-dot {{
    display: inline-block; width: 8px; height: 8px;
    border-radius: 50%; background: {C['green']};
    box-shadow: 0 0 10px {C['green']};
    animation: pulse 1.8s infinite;
}}
@keyframes pulse {{
    0%,100% {{ opacity:1; transform:scale(1); }}
    50% {{ opacity:.6; transform:scale(1.35); }}
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PERSISTENCE
# ─────────────────────────────────────────────
DATA_FILE = "finanalyzer_data.json"

def load_data() -> dict:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f:
                return ensure_data_schema(json.load(f))
        except Exception:
            pass
    return ensure_data_schema({
        "watchlist": ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META", "AMD"],
        "portfolio": {},
        "alerts": [],
        "preferences": {
            "debug_mode": False,
            "language": "CZ",
        },
    })

def save_data(d: dict):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2)

def ensure_data_schema(d: dict) -> dict:
    """Backfill missing keys to keep backwards compatibility."""
    if not isinstance(d, dict):
        return load_data()
    d.setdefault("watchlist", ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META", "AMD"])
    d.setdefault("portfolio", {})
    d.setdefault("alerts", [])
    prefs = d.get("preferences", {})
    if not isinstance(prefs, dict):
        prefs = {}
    prefs.setdefault("debug_mode", False)
    prefs.setdefault("language", "CZ")
    d["preferences"] = prefs
    return d

def is_debug_mode() -> bool:
    data = ensure_data_schema(load_data())
    return bool(data.get("preferences", {}).get("debug_mode", False))

def log_debug(message: str):
    if is_debug_mode():
        st.info(f"🧪 DEBUG: {message}")

def normalized_ticker_input(
    label: str,
    key: str,
    default: str = "AAPL",
    placeholder: str = "",
    label_visibility: str = "visible",
) -> str:
    raw_key = f"{key}_raw"
    if raw_key not in st.session_state:
        st.session_state[raw_key] = st.session_state.get(key, default)
    raw = st.text_input(label, key=raw_key, placeholder=placeholder, label_visibility=label_visibility)
    clean = sanitize_ticker_input(raw, default=default)
    if st.session_state.get(key) != clean:
        st.session_state[key] = clean
    return clean

# ─────────────────────────────────────────────
#  DATA ENGINE  (cached)
# ─────────────────────────────────────────────
@st.cache_data(ttl=120)
def fetch_stock(ticker: str, period: str = "1y", interval: str = "1d"):
    try:
        s = yf.Ticker(ticker)
        df = s.history(period=period, interval=interval, auto_adjust=True)
        info = s.info or {}
        return df, info
    except Exception as e:
        log_debug(f"fetch_stock failed for {ticker}: {e}")
        return None, {}

@st.cache_data(ttl=300)
def fetch_multi(tickers: list) -> dict:
    out = {}
    for t in tickers:
        try:
            s = yf.Ticker(t)
            h = s.history(period="5d")
            if h.empty:
                continue
            cur = h["Close"].iloc[-1]
            prev = h["Close"].iloc[-2] if len(h) > 1 else cur
            info = s.info or {}
            out[t] = {
                "price": cur,
                "change": ((cur - prev) / prev) * 100,
                "volume": h["Volume"].iloc[-1],
                "name": info.get("shortName", t),
                "market_cap": info.get("marketCap", 0),
                "sector": info.get("sector", "N/A"),
                "pe": info.get("trailingPE", None),
            }
        except Exception as e:
            log_debug(f"fetch_multi failed for {t}: {e}")
            continue
    return out

@st.cache_data(ttl=900)
def fetch_market_regime() -> dict:
    """Quick market regime snapshot using liquid macro proxies."""
    proxies = {
        "SPY": "SPY",
        "QQQ": "QQQ",
        "IWM": "IWM",
        "TLT": "TLT",
        "VIX": "^VIX",
    }
    out = {}
    for k, sym in proxies.items():
        try:
            h = yf.Ticker(sym).history(period="3mo")
            if h is None or h.empty or len(h) < 22:
                continue
            last = float(h["Close"].iloc[-1])
            chg_1d = (last / float(h["Close"].iloc[-2]) - 1) * 100
            chg_1m = (last / float(h["Close"].iloc[-22]) - 1) * 100
            out[k] = {"last": last, "d1": chg_1d, "m1": chg_1m}
        except Exception as e:
            log_debug(f"fetch_market_regime failed for {sym}: {e}")
    if not out:
        return {}
    risk_on_score = 0
    risk_on_score += 1 if out.get("SPY", {}).get("m1", -1) > 0 else 0
    risk_on_score += 1 if out.get("QQQ", {}).get("m1", -1) > 0 else 0
    risk_on_score += 1 if out.get("IWM", {}).get("m1", -1) > 0 else 0
    risk_on_score += 1 if out.get("VIX", {}).get("m1", 1) < 0 else 0
    regime = "RISK-ON" if risk_on_score >= 3 else "NEUTRAL" if risk_on_score == 2 else "RISK-OFF"
    out["regime"] = regime
    out["score"] = risk_on_score
    return out

@st.cache_data(ttl=600)
def fetch_news(ticker: str) -> list:
    try:
        raw = yf.Ticker(ticker).news or []
        normalized = []
        for n in raw:
            # yfinance 0.2.x+ wraps items in {"content": {...}} structure
            if "content" in n and isinstance(n.get("content"), dict):
                c = n["content"]
                provider = c.get("provider", {})
                pub_name = provider.get("displayName", "") if isinstance(provider, dict) else ""
                canon = c.get("canonicalUrl", {})
                link = canon.get("url", "#") if isinstance(canon, dict) else "#"
                ts = 0
                if c.get("pubDate"):
                    try:
                        ts = int(pd.Timestamp(c["pubDate"]).timestamp())
                    except Exception:
                        ts = 0
                normalized.append({
                    "title": c.get("title", ""),
                    "publisher": pub_name or c.get("publisher", ""),
                    "link": link or c.get("link", "#"),
                    "providerPublishTime": ts,
                })
            else:
                normalized.append(n)
        return normalized
    except Exception as e:
        log_debug(f"fetch_news failed for {ticker}: {e}")
        return []

@st.cache_data(ttl=3600)
def fetch_insider_sec(ticker: str) -> list:
    """Fetch real insider trades from SEC EDGAR Form 4."""
    try:
        # Get CIK for ticker
        headers = {"User-Agent": "FinAnalyzerPro contact@finanalyzer.app"}
        r = requests.get(
            f"https://efts.sec.gov/LATEST/search-index?q=%22{ticker}%22&dateRange=custom"
            f"&startdt={(datetime.now()-timedelta(days=180)).strftime('%Y-%m-%d')}"
            f"&enddt={datetime.now().strftime('%Y-%m-%d')}&forms=4",
            headers=headers, timeout=8
        )
        # Alternative: use company facts endpoint
        # First resolve ticker → CIK
        cik_r = requests.get(
            "https://www.sec.gov/files/company_tickers.json",
            headers=headers, timeout=8
        )
        cik_data = cik_r.json()
        cik = None
        for v in cik_data.values():
            if v.get("ticker", "").upper() == ticker.upper():
                cik = str(v["cik_str"]).zfill(10)
                break
        if not cik:
            return []

        # Fetch submissions (includes recent Form 4 filings)
        sub_r = requests.get(
            f"https://data.sec.gov/submissions/CIK{cik}.json",
            headers=headers, timeout=10
        )
        sub = sub_r.json()
        filings = sub.get("filings", {}).get("recent", {})
        forms = filings.get("form", [])
        dates = filings.get("filingDate", [])
        accessions = filings.get("accessionNumber", [])
        reporters = filings.get("reportingOwner", []) if "reportingOwner" in filings else []

        trades = []
        for i, form in enumerate(forms):
            if form == "4" and i < len(dates):
                date_str = dates[i]
                if datetime.strptime(date_str, "%Y-%m-%d") < datetime.now() - timedelta(days=180):
                    continue
                trades.append({
                    "date": date_str,
                    "form": form,
                    "accession": accessions[i] if i < len(accessions) else "",
                    "cik": cik,
                })
                if len(trades) >= 20:
                    break

        return trades
    except Exception as e:
        log_debug(f"fetch_insider_sec failed for {ticker}: {e}")
        return []

@st.cache_data(ttl=3600)
def fetch_analyst_info(ticker: str) -> dict:
    """Fetch analyst recommendations and price targets from yfinance."""
    try:
        s = yf.Ticker(ticker)
        recs = s.recommendations
        info = s.info or {}

        # Summarise recent recommendations
        rec_summary = {"strongBuy": 0, "buy": 0, "hold": 0, "sell": 0, "strongSell": 0}
        if recs is not None and not recs.empty:
            recent = recs.tail(10)
            for col in rec_summary:
                if col in recent.columns:
                    rec_summary[col] = int(recent[col].sum())

        return {
            "target_mean": info.get("targetMeanPrice", 0),
            "target_high": info.get("targetHighPrice", 0),
            "target_low":  info.get("targetLowPrice", 0),
            "recommendation": info.get("recommendationKey", "none"),
            "num_analysts": info.get("numberOfAnalystOpinions", 0),
            "rec_summary": rec_summary,
        }
    except Exception as e:
        log_debug(f"fetch_analyst_info failed for {ticker}: {e}")
        return {}

@st.cache_data(ttl=900)
def fetch_options_snapshot(ticker: str) -> dict:
    """Return nearest-expiry options sentiment summary."""
    try:
        tk = yf.Ticker(ticker)
        expiries = tk.options or []
        if not expiries:
            return {}
        expiry = expiries[0]
        chain = tk.option_chain(expiry)
        calls = chain.calls.copy() if chain and chain.calls is not None else pd.DataFrame()
        puts  = chain.puts.copy() if chain and chain.puts is not None else pd.DataFrame()
        if calls.empty and puts.empty:
            return {}

        call_oi = float(calls["openInterest"].fillna(0).sum()) if "openInterest" in calls.columns else 0.0
        put_oi  = float(puts["openInterest"].fillna(0).sum())  if "openInterest" in puts.columns else 0.0
        call_vol = float(calls["volume"].fillna(0).sum()) if "volume" in calls.columns else 0.0
        put_vol  = float(puts["volume"].fillna(0).sum())  if "volume" in puts.columns else 0.0
        pcr_oi = (put_oi / call_oi) if call_oi > 0 else np.nan
        pcr_vol = (put_vol / call_vol) if call_vol > 0 else np.nan

        spot = float(tk.history(period="5d")["Close"].iloc[-1])
        strikes = sorted(set(calls.get("strike", pd.Series(dtype=float)).dropna().tolist()) |
                         set(puts.get("strike", pd.Series(dtype=float)).dropna().tolist()))
        max_pain = None
        if strikes:
            pain_scores = []
            for k in strikes:
                call_pain = ((calls["strike"] - k).clip(lower=0) * calls["openInterest"]).sum() if not calls.empty else 0
                put_pain  = ((k - puts["strike"]).clip(lower=0) * puts["openInterest"]).sum() if not puts.empty else 0
                pain_scores.append((k, float(call_pain + put_pain)))
            max_pain = min(pain_scores, key=lambda x: x[1])[0] if pain_scores else None

        return {
            "expiry": expiry,
            "spot": spot,
            "call_oi": call_oi,
            "put_oi": put_oi,
            "call_vol": call_vol,
            "put_vol": put_vol,
            "pcr_oi": pcr_oi,
            "pcr_vol": pcr_vol,
            "max_pain": max_pain,
            "calls_top_oi": calls.nlargest(8, "openInterest")[["strike", "openInterest", "volume"]] if not calls.empty else pd.DataFrame(),
            "puts_top_oi": puts.nlargest(8, "openInterest")[["strike", "openInterest", "volume"]] if not puts.empty else pd.DataFrame(),
        }
    except Exception as e:
        log_debug(f"fetch_options_snapshot failed for {ticker}: {e}")
        return {}

# ─────────────────────────────────────────────
#  TECHNICAL INDICATORS
# ─────────────────────────────────────────────
def calc_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # SMAs
    for p in [20, 50, 200]:
        df[f"SMA{p}"] = df["Close"].rolling(p).mean()
    # EMAs
    df["EMA12"] = df["Close"].ewm(span=12, adjust=False).mean()
    df["EMA26"] = df["Close"].ewm(span=26, adjust=False).mean()
    # MACD
    df["MACD"]        = df["EMA12"] - df["EMA26"]
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"]   = df["MACD"] - df["MACD_Signal"]
    # RSI
    delta = df["Close"].diff()
    gain  = delta.where(delta > 0, 0).rolling(14).mean()
    loss  = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs    = gain / loss.replace(0, np.nan)
    df["RSI"] = 100 - (100 / (1 + rs))
    # Bollinger Bands
    df["BB_Mid"]   = df["Close"].rolling(20).mean()
    df["BB_Std"]   = df["Close"].rolling(20).std()
    df["BB_Upper"] = df["BB_Mid"] + 2 * df["BB_Std"]
    df["BB_Lower"] = df["BB_Mid"] - 2 * df["BB_Std"]
    df["BB_Pct"]   = (df["Close"] - df["BB_Lower"]) / (df["BB_Upper"] - df["BB_Lower"])
    # ATR
    df["TR"]  = np.maximum(df["High"] - df["Low"],
                np.maximum(abs(df["High"] - df["Close"].shift()),
                           abs(df["Low"]  - df["Close"].shift())))
    df["ATR"] = df["TR"].rolling(14).mean()
    # Volume ratio
    df["Vol_Avg20"] = df["Volume"].rolling(20).mean()
    df["RVOL"]      = df["Volume"] / df["Vol_Avg20"]
    # Stochastic RSI (3,3,14,14)
    rsi_s = df["RSI"]
    rsi_min = rsi_s.rolling(14).min()
    rsi_max = rsi_s.rolling(14).max()
    stoch_rsi = (rsi_s - rsi_min) / (rsi_max - rsi_min).replace(0, np.nan)
    df["StochRSI_K"] = stoch_rsi.rolling(3).mean() * 100
    df["StochRSI_D"] = df["StochRSI_K"].rolling(3).mean()
    # VWAP (cumulative daily — works well for intraday; for daily data use rolling 20-day)
    typical = (df["High"] + df["Low"] + df["Close"]) / 3
    df["VWAP"] = (typical * df["Volume"]).rolling(20).sum() / df["Volume"].rolling(20).sum()
    # OBV (On-Balance Volume)
    obv = [0]
    for i in range(1, len(df)):
        if df["Close"].iloc[i] > df["Close"].iloc[i-1]:
            obv.append(obv[-1] + df["Volume"].iloc[i])
        elif df["Close"].iloc[i] < df["Close"].iloc[i-1]:
            obv.append(obv[-1] - df["Volume"].iloc[i])
        else:
            obv.append(obv[-1])
    df["OBV"] = obv
    # Williams %R (14)
    high14 = df["High"].rolling(14).max()
    low14  = df["Low"].rolling(14).min()
    df["Williams_R"] = -100 * (high14 - df["Close"]) / (high14 - low14).replace(0, np.nan)
    # Ichimoku (simplified — Tenkan + Kijun)
    df["Ichimoku_Tenkan"] = (df["High"].rolling(9).max()  + df["Low"].rolling(9).min())  / 2
    df["Ichimoku_Kijun"]  = (df["High"].rolling(26).max() + df["Low"].rolling(26).min()) / 2
    return df

# ─────────────────────────────────────────────
#  BUY SCORE ENGINE
# ─────────────────────────────────────────────
def compute_buy_score(df: pd.DataFrame, info: dict, analyst: dict, insider_trades: list) -> dict:
    """
    Weighted multi-factor Buy Score (0–100).
    Components:
      Technical Analysis  25 %
      Fundamentals        25 %
      Momentum            20 %
      Analyst Consensus   20 %
      Insider Activity    10 %
    """
    if df is None or df.empty or len(df) < 50:
        return {"score": None, "components": {}, "signals": []}

    df = calc_indicators(df)
    last = df.iloc[-1]
    signals = []

    def _conf_adjust(score: float, confidence: float, min_factor: float = 0.55) -> float:
        """Pull extreme scores towards neutral when data coverage is low."""
        confidence = max(0.0, min(1.0, confidence))
        factor = min_factor + (1 - min_factor) * confidence
        return 50 + (score - 50) * factor

    # ── 1. TECHNICAL (25 %) ───────────────────
    tech_points = []

    # RSI
    rsi = last.get("RSI", 50)
    if pd.notna(rsi):
        if rsi < 30:
            tech_points.append(90); signals.append(("RSI", f"{rsi:.1f} — přeprodaný (bullish)", True))
        elif rsi < 45:
            tech_points.append(72); signals.append(("RSI", f"{rsi:.1f} — mírně přeprodaný", True))
        elif rsi < 55:
            tech_points.append(55); signals.append(("RSI", f"{rsi:.1f} — neutrální", None))
        elif rsi < 70:
            tech_points.append(40); signals.append(("RSI", f"{rsi:.1f} — mírně překoupený", False))
        else:
            tech_points.append(15); signals.append(("RSI", f"{rsi:.1f} — překoupený (bearish)", False))

    # MACD
    macd      = last.get("MACD", 0)
    macd_sig  = last.get("MACD_Signal", 0)
    prev_macd = df["MACD"].iloc[-2] if len(df) > 2 else macd
    prev_sig  = df["MACD_Signal"].iloc[-2] if len(df) > 2 else macd_sig
    if pd.notna(macd) and pd.notna(macd_sig):
        if macd > macd_sig and prev_macd <= prev_sig:
            tech_points.append(90); signals.append(("MACD", "Bullish crossover — silný nákupní signál", True))
        elif macd > macd_sig:
            tech_points.append(65); signals.append(("MACD", "MACD nad signální linií", True))
        elif macd < macd_sig and prev_macd >= prev_sig:
            tech_points.append(15); signals.append(("MACD", "Bearish crossover — silný prodejní signál", False))
        else:
            tech_points.append(35); signals.append(("MACD", "MACD pod signální linií", False))

    # SMA trend
    close = last["Close"]
    sma20  = last.get("SMA20", close)
    sma50  = last.get("SMA50", close)
    sma200 = last.get("SMA200", close)
    above_count = sum([close > sma20, close > sma50, close > sma200])
    sma_score = [20, 45, 70, 90][above_count]
    tech_points.append(sma_score)
    signals.append(("SMA trend", f"Cena nad {above_count}/3 klouzavými průměry", above_count >= 2))

    # Bollinger Band position
    bb_pct = last.get("BB_Pct", 0.5)
    if pd.notna(bb_pct):
        if bb_pct < 0.2:
            tech_points.append(85); signals.append(("Bollinger", "Blízko dolního pásma — potenciální reverze", True))
        elif bb_pct < 0.4:
            tech_points.append(65); signals.append(("Bollinger", "Spodní polovina pásma", True))
        elif bb_pct < 0.6:
            tech_points.append(50); signals.append(("Bollinger", "Střed pásma", None))
        elif bb_pct < 0.8:
            tech_points.append(40); signals.append(("Bollinger", "Horní polovina pásma", False))
        else:
            tech_points.append(20); signals.append(("Bollinger", "Blízko horního pásma — potenciální korekce", False))

    tech_score_raw = np.mean(tech_points) if tech_points else 50
    tech_conf = min(1.0, len(tech_points) / 4)  # RSI, MACD, SMA trend, BB position
    tech_score = _conf_adjust(tech_score_raw, tech_conf)

    # ── 2. FUNDAMENTALS (25 %) ───────────────
    fund_points = []

    # P/E ratio
    pe = info.get("trailingPE")
    if pe and pe > 0:
        if pe < 10:
            fund_points.append(88); signals.append(("P/E", f"{pe:.1f} — velmi nízké, podhodnocená akcie", True))
        elif pe < 20:
            fund_points.append(75); signals.append(("P/E", f"{pe:.1f} — přiměřené ocenění", True))
        elif pe < 35:
            fund_points.append(50); signals.append(("P/E", f"{pe:.1f} — mírně drahé", None))
        elif pe < 60:
            fund_points.append(30); signals.append(("P/E", f"{pe:.1f} — drahé", False))
        else:
            fund_points.append(12); signals.append(("P/E", f"{pe:.1f} — velmi drahé", False))

    # PEG ratio
    peg = info.get("pegRatio")
    if peg and peg > 0:
        if peg < 0.8:
            fund_points.append(90); signals.append(("PEG", f"{peg:.2f} — silně podhodnocený růst", True))
        elif peg < 1.2:
            fund_points.append(70); signals.append(("PEG", f"{peg:.2f} — férové ocenění", True))
        elif peg < 2.0:
            fund_points.append(45); signals.append(("PEG", f"{peg:.2f} — mírně drahý", None))
        else:
            fund_points.append(20); signals.append(("PEG", f"{peg:.2f} — předražený", False))

    # Return on Equity
    roe = info.get("returnOnEquity")
    if roe is not None:
        roe_pct = roe * 100
        if roe_pct > 25:
            fund_points.append(90); signals.append(("ROE", f"{roe_pct:.1f} % — výborné", True))
        elif roe_pct > 15:
            fund_points.append(70); signals.append(("ROE", f"{roe_pct:.1f} % — dobré", True))
        elif roe_pct > 5:
            fund_points.append(45); signals.append(("ROE", f"{roe_pct:.1f} % — průměrné", None))
        else:
            fund_points.append(20); signals.append(("ROE", f"{roe_pct:.1f} % — slabé", False))

    # Debt to Equity
    de = info.get("debtToEquity")
    if de is not None:
        if de < 30:
            fund_points.append(85); signals.append(("Dluh/Vlastní kap.", f"{de:.0f} — nízký dluh", True))
        elif de < 80:
            fund_points.append(62); signals.append(("Dluh/Vlastní kap.", f"{de:.0f} — přiměřený dluh", True))
        elif de < 150:
            fund_points.append(38); signals.append(("Dluh/Vlastní kap.", f"{de:.0f} — vysoký dluh", False))
        else:
            fund_points.append(15); signals.append(("Dluh/Vlastní kap.", f"{de:.0f} — zadlužena", False))

    # Profit margin
    pm = info.get("profitMargins")
    if pm is not None:
        pm_pct = pm * 100
        if pm_pct > 20:
            fund_points.append(90); signals.append(("Zisková marže", f"{pm_pct:.1f} % — výborná", True))
        elif pm_pct > 10:
            fund_points.append(68); signals.append(("Zisková marže", f"{pm_pct:.1f} % — dobrá", True))
        elif pm_pct > 0:
            fund_points.append(42); signals.append(("Zisková marže", f"{pm_pct:.1f} % — nízká", None))
        else:
            fund_points.append(10); signals.append(("Zisková marže", f"{pm_pct:.1f} % — ztrátová", False))

    fund_score_raw = np.mean(fund_points) if fund_points else 50
    fund_conf = min(1.0, len(fund_points) / 5)  # P/E, PEG, ROE, D/E, margin
    fund_score = _conf_adjust(fund_score_raw, fund_conf)

    # ── 3. MOMENTUM (20 %) ───────────────────
    mom_points = []

    # Price vs 52W high/low
    high52 = info.get("fiftyTwoWeekHigh", close)
    low52  = info.get("fiftyTwoWeekLow",  close)
    if high52 > low52:
        pos_52w = (close - low52) / (high52 - low52)
        if pos_52w > 0.85:
            mom_points.append(80); signals.append(("52W pozice", f"{pos_52w*100:.0f} % od low — blízko maxima", None))
        elif pos_52w > 0.6:
            mom_points.append(68); signals.append(("52W pozice", f"{pos_52w*100:.0f} % od low — horní polovina", True))
        elif pos_52w > 0.4:
            mom_points.append(50); signals.append(("52W pozice", f"{pos_52w*100:.0f} % od low — střed", None))
        else:
            mom_points.append(35); signals.append(("52W pozice", f"{pos_52w*100:.0f} % od low — spodní polovina", False))

    # 1M, 3M, 6M returns
    periods = {
        "1M výkon":  20,
        "3M výkon":  60,
        "6M výkon": 126,
    }
    for label, days in periods.items():
        if len(df) > days:
            past_price = df["Close"].iloc[-days]
            ret = (close - past_price) / past_price * 100
            if ret > 15:
                mom_points.append(88); signals.append((label, f"{ret:+.1f} %", True))
            elif ret > 5:
                mom_points.append(70); signals.append((label, f"{ret:+.1f} %", True))
            elif ret > -5:
                mom_points.append(50); signals.append((label, f"{ret:+.1f} %", None))
            elif ret > -15:
                mom_points.append(30); signals.append((label, f"{ret:+.1f} %", False))
            else:
                mom_points.append(12); signals.append((label, f"{ret:+.1f} %", False))

    # Volume momentum
    rvol = last.get("RVOL", 1.0)
    if pd.notna(rvol):
        if rvol > 2.0:
            mom_points.append(80); signals.append(("Rel. objem", f"{rvol:.1f}x — silný zájem", True))
        elif rvol > 1.3:
            mom_points.append(65); signals.append(("Rel. objem", f"{rvol:.1f}x — nadprůměrný", True))
        elif rvol > 0.7:
            mom_points.append(50); signals.append(("Rel. objem", f"{rvol:.1f}x — normální", None))
        else:
            mom_points.append(30); signals.append(("Rel. objem", f"{rvol:.1f}x — nízký zájem", False))

    mom_score_raw = np.mean(mom_points) if mom_points else 50
    mom_conf = min(1.0, len(mom_points) / 5)  # 52W pos, 1M, 3M, 6M, RVOL
    mom_score = _conf_adjust(mom_score_raw, mom_conf)

    # ── 4. ANALYST CONSENSUS (20 %) ──────────
    ana_points = []

    rec_key = analyst.get("recommendation", "none")
    rec_map = {
        "strongBuy": 92, "strong_buy": 92,
        "buy": 75,
        "hold": 50,
        "sell": 25, "underperform": 22,
        "strongSell": 8, "strong_sell": 8,
    }
    rec_score = rec_map.get(rec_key, 50)
    ana_points.append(rec_score)
    signals.append(("Analyst rating", rec_key.replace("_", " ").title() or "N/A", rec_score > 55))

    # Target price upside
    target = analyst.get("target_mean", 0)
    if target and target > 0 and close > 0:
        upside = (target - close) / close * 100
        if upside > 25:
            ana_points.append(90); signals.append(("Target price upside", f"{upside:+.1f} % ({analyst.get('num_analysts',0)} analytiků)", True))
        elif upside > 10:
            ana_points.append(72); signals.append(("Target price upside", f"{upside:+.1f} % ({analyst.get('num_analysts',0)} analytiků)", True))
        elif upside > 0:
            ana_points.append(54); signals.append(("Target price upside", f"{upside:+.1f} %", None))
        elif upside > -10:
            ana_points.append(35); signals.append(("Target price upside", f"{upside:+.1f} %", False))
        else:
            ana_points.append(12); signals.append(("Target price upside", f"{upside:+.1f} % — analytici vidí pokles", False))

    ana_score_raw = np.mean(ana_points) if ana_points else 50
    ana_conf = min(1.0, len(ana_points) / 2)  # recommendation + target
    ana_score = _conf_adjust(ana_score_raw, ana_conf)

    # ── 5. INSIDER ACTIVITY (10 %) ───────────
    ins_score = 50  # neutral default
    ins_conf = 0.35
    if insider_trades:
        # Count recent filings — more Form 4 filings = more insider activity
        # We can't parse full XML here without heavy dependencies,
        # so we use count as a proxy (many filings in 180 days = active insiders)
        count = len(insider_trades)
        if count >= 10:
            ins_score = 72  # lots of Form 4 filings → moderate positive
            signals.append(("Insider aktivita", f"{count} Form-4 podání za 6M (SEC EDGAR)", True))
        elif count >= 5:
            ins_score = 60
            signals.append(("Insider aktivita", f"{count} Form-4 podání za 6M", None))
        elif count >= 1:
            ins_score = 52
            signals.append(("Insider aktivita", f"{count} Form-4 podání za 6M", None))
        else:
            ins_score = 45
            signals.append(("Insider aktivita", "Žádné Form-4 za 6M", False))
        ins_conf = 1.0
    else:
        signals.append(("Insider aktivita", "Nepodařilo se načíst ze SEC EDGAR", None))
    ins_score = _conf_adjust(ins_score, ins_conf)

    # ── WEIGHTED TOTAL (confidence-adjusted) ─
    base_weights = {
        "Technická analýza": 25,
        "Fundamenty":        25,
        "Momentum":          20,
        "Analytici":         20,
        "Insider aktivita":  10,
    }
    confidences = {
        "Technická analýza": tech_conf,
        "Fundamenty":        fund_conf,
        "Momentum":          mom_conf,
        "Analytici":         ana_conf,
        "Insider aktivita":  ins_conf,
    }
    # Low-confidence component keeps some weight, but less than full-confidence one.
    eff_weights = {k: v * (0.45 + 0.55 * confidences[k]) for k, v in base_weights.items()}
    w_sum = sum(eff_weights.values()) or 1.0
    norm_w = {k: v / w_sum for k, v in eff_weights.items()}
    total = (
        tech_score * norm_w["Technická analýza"] +
        fund_score * norm_w["Fundamenty"] +
        mom_score  * norm_w["Momentum"] +
        ana_score  * norm_w["Analytici"] +
        ins_score  * norm_w["Insider aktivita"]
    )
    total = max(0, min(100, total))
    overall_conf = np.mean(list(confidences.values()))
    signals.append(("Kvalita dat modelu", f"{overall_conf*100:.0f}% pokrytí vstupních faktorů", overall_conf >= 0.7))

    if total >= 80:
        label, color = "SILNĚ KOUPIT", C["green"]
    elif total >= 62:
        label, color = "KOUPIT", "#4ade80"
    elif total >= 45:
        label, color = "DRŽET", C["orange"]
    elif total >= 28:
        label, color = "PRODAT", "#fb923c"
    else:
        label, color = "SILNĚ PRODAT", C["red"]

    return {
        "score": round(total, 1),
        "label": label,
        "color": color,
        "components": {
            "Technická analýza": round(tech_score, 1),
            "Fundamenty":        round(fund_score, 1),
            "Momentum":          round(mom_score,  1),
            "Analytici":         round(ana_score,  1),
            "Insider aktivita":  round(ins_score,  1),
        },
        "weights": {
            "Technická analýza": round(norm_w["Technická analýza"] * 100),
            "Fundamenty":        round(norm_w["Fundamenty"] * 100),
            "Momentum":          round(norm_w["Momentum"] * 100),
            "Analytici":         round(norm_w["Analytici"] * 100),
            "Insider aktivita":  round(norm_w["Insider aktivita"] * 100),
        },
        "confidence": round(overall_conf * 100, 1),
        "signals": signals,
    }

# ─────────────────────────────────────────────
#  CHART HELPERS
# ─────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="rgba(0,0,0,0)",
    font=dict(color=C["t1"], family="Inter"),
    margin=dict(l=8, r=8, t=26, b=8),
    hovermode="x unified",
    hoverlabel=dict(
        bgcolor="rgba(15,23,42,0.92)",
        bordercolor=C["border2"],
        font=dict(color=C["t1"], size=12),
    ),
)

# ─────────────────────────────────────────────
#  NEW: SEASONALITY ANALYSIS
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def compute_seasonality(ticker: str, years: int = 10) -> pd.DataFrame:
    """Compute average monthly returns over N years."""
    try:
        df = yf.Ticker(ticker).history(period=f"{years}y")
        if df.empty:
            return pd.DataFrame()
        df["Month"]  = df.index.month
        df["Year"]   = df.index.year
        df["Return"] = df["Close"].pct_change()
        monthly = df.groupby(["Year","Month"])["Return"].sum() * 100
        avg = monthly.groupby("Month").mean()
        med = monthly.groupby("Month").median()
        pos = monthly.groupby("Month").apply(lambda x: (x > 0).mean() * 100)
        result = pd.DataFrame({"avg": avg, "median": med, "positive_pct": pos})
        result.index = [datetime(2000, m, 1).strftime("%b") for m in result.index]
        return result
    except Exception:
        return pd.DataFrame()

# ─────────────────────────────────────────────
#  NEW: DCF FAIR VALUE CALCULATOR
# ─────────────────────────────────────────────
def compute_dcf(info: dict, growth_rate: float = 0.10, terminal_growth: float = 0.03,
                discount_rate: float = 0.10, years: int = 10, base_fcf: float = None,
                shares_outstanding: float = None) -> dict:
    """Simple DCF valuation based on free cash flow."""
    try:
        fcf   = (base_fcf if base_fcf is not None else info.get("freeCashflow", 0)) or 0
        shares = (shares_outstanding if shares_outstanding is not None else info.get("sharesOutstanding", 1)) or 1
        cash  = info.get("totalCash", 0) or 0
        debt  = info.get("totalDebt", 0) or 0
        if discount_rate <= terminal_growth:
            return {"fair_value": None, "error": "Diskontní sazba musí být vyšší než terminální růst"}
        if fcf <= 0:
            return {"fair_value": None, "error": "Free cash flow není dostupný nebo záporný"}
        projected = []
        cf = fcf
        for _ in range(years):
            cf *= (1 + growth_rate)
            pv  = cf / ((1 + discount_rate) ** (_ + 1))
            projected.append(pv)
        terminal_val = projected[-1] * (1 + terminal_growth) / (discount_rate - terminal_growth)
        terminal_pv  = terminal_val / ((1 + discount_rate) ** years)
        enterprise_val = sum(projected) + terminal_pv
        equity_val     = enterprise_val + cash - debt
        fair_value     = equity_val / shares
        return {
            "fair_value":    round(fair_value, 2),
            "enterprise_val": round(enterprise_val / 1e9, 2),
            "projected_pvs": [round(p / 1e9, 3) for p in projected],
            "terminal_pv":   round(terminal_pv / 1e9, 2),
            "error": None,
        }
    except Exception as e:
        return {"fair_value": None, "error": str(e)}

def resolve_shares_outstanding(info: dict, current_price: float = None) -> dict:
    """Resolve shares outstanding with robust fallbacks."""
    shares_info = info.get("sharesOutstanding")
    if isinstance(shares_info, (int, float)) and shares_info > 0:
        return {"value": float(shares_info), "source": "info.sharesOutstanding", "fallback": False}

    float_shares = info.get("floatShares")
    if isinstance(float_shares, (int, float)) and float_shares > 0:
        return {"value": float(float_shares), "source": "info.floatShares", "fallback": True}

    mc = info.get("marketCap")
    if isinstance(mc, (int, float)) and mc > 0 and isinstance(current_price, (int, float)) and current_price > 0:
        inferred = mc / current_price
        if np.isfinite(inferred) and inferred > 0:
            return {"value": float(inferred), "source": "marketCap / current_price (fallback)", "fallback": True}

    return {"value": 1.0, "source": "default=1 (fallback)", "fallback": True}

def compute_risk_pack(df: pd.DataFrame, info: dict, current_price: float) -> dict:
    """Institutional-like risk snapshot from price history + metadata."""
    try:
        if df is None or df.empty or "Close" not in df.columns:
            return {}
        rets = df["Close"].pct_change().dropna()
        if rets.empty:
            return {}
        vol_daily = float(rets.std())
        vol_annual = vol_daily * np.sqrt(252)
        var_95_1d = float(np.quantile(rets, 0.05))
        cum = (1 + rets).cumprod()
        peak = cum.cummax()
        dd = (cum / peak) - 1
        max_dd = float(dd.min()) if not dd.empty else 0.0
        beta = info.get("beta")
        beta = float(beta) if isinstance(beta, (int, float)) else np.nan
        risk_score = (min(abs(max_dd) * 100, 40) + min(vol_annual * 100, 40) + min(abs(var_95_1d) * 100, 20))
        risk_score = min(max(risk_score, 0), 100)
        return {
            "vol_annual": vol_annual,
            "var_95_1d": var_95_1d,
            "max_drawdown": max_dd,
            "beta": beta if np.isfinite(beta) else None,
            "risk_score": risk_score,
            "current_price": current_price,
        }
    except Exception:
        return {}

def generate_investment_memo(ticker: str, info: dict, dcf: dict, risk_pack: dict, score_data: dict) -> dict:
    """Generate concise memo for retail + institutional workflows."""
    fv = dcf.get("fair_value") if isinstance(dcf, dict) else None
    cur = risk_pack.get("current_price") if isinstance(risk_pack, dict) else None
    upside = ((fv - cur) / cur * 100) if fv and cur else None
    score = score_data.get("score") if isinstance(score_data, dict) else None
    risk_score = risk_pack.get("risk_score") if isinstance(risk_pack, dict) else None
    thesis = "Neutrální"
    if upside is not None and score is not None and risk_score is not None:
        if upside > 20 and score >= 70 and risk_score < 55:
            thesis = "Kandidát na akumulaci"
        elif upside < -10 or score < 40:
            thesis = "Spíše redukovat / vyčkat"
        else:
            thesis = "Selektivní držení"
    return {
        "ticker": ticker,
        "company": info.get("shortName", ticker),
        "thesis": thesis,
        "fair_value": fv,
        "current_price": cur,
        "upside_pct": upside,
        "buy_score": score,
        "risk_score": risk_score,
        "key_risks": [
            "DCF je citlivé na WACC/terminal growth.",
            "Historická volatilita se může výrazně změnit při výsledcích (earnings).",
            "Makro režim (sazby, kreditní podmínky) může přebít fundament."
        ],
    }

@st.cache_data(ttl=600)
def get_unlevered_fcf_ttm(ticker: str, info: dict) -> dict:
    """
    Return unlevered FCF (TTM) primarily from cash-flow statements:
    FCF = Operating Cash Flow - CapEx.
    Falls back to info['freeCashflow'] only when statements are unavailable.
    """
    def _extract_fcf_from_cashflow(cashflow_df: pd.DataFrame) -> float:
        if cashflow_df is None or cashflow_df.empty:
            return None
        ocf_labels = ["Operating Cash Flow", "Total Cash From Operating Activities"]
        capex_labels = ["Capital Expenditure", "Capital Expenditures"]
        ocf = None
        capex = None
        for lbl in ocf_labels:
            if lbl in cashflow_df.index:
                ocf = cashflow_df.loc[lbl].dropna().head(4).sum()
                break
        for lbl in capex_labels:
            if lbl in cashflow_df.index:
                capex = cashflow_df.loc[lbl].dropna().head(4).sum()
                break
        if ocf is None or capex is None:
            return None
        capex_abs = -capex if capex < 0 else capex
        return float(ocf - capex_abs)

    try:
        stock = yf.Ticker(ticker)
        fcf_q = _extract_fcf_from_cashflow(stock.quarterly_cashflow)
        if fcf_q is not None and np.isfinite(fcf_q):
            return {"value": fcf_q, "source": "quarterly_cashflow (TTM OCF − CapEx)", "fallback": False}

        fcf_a = _extract_fcf_from_cashflow(stock.cashflow)
        if fcf_a is not None and np.isfinite(fcf_a):
            return {"value": fcf_a, "source": "cashflow (latest OCF − CapEx)", "fallback": False}
    except Exception:
        pass

    fcf_info = info.get("freeCashflow", 0) or 0
    return {"value": fcf_info, "source": "info.freeCashflow (fallback)", "fallback": True}

# ─────────────────────────────────────────────
#  NEW: RELATIVE STRENGTH vs S&P 500
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def compute_relative_strength(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Returns ratio of ticker performance vs S&P 500."""
    try:
        t_df  = yf.Ticker(ticker).history(period=period)["Close"]
        sp_df = yf.Ticker("^GSPC").history(period=period)["Close"]
        t_norm  = t_df  / t_df.iloc[0]
        sp_norm = sp_df / sp_df.iloc[0]
        rs = (t_norm / sp_norm).dropna()
        return rs
    except Exception:
        return pd.Series(dtype=float)

# ─────────────────────────────────────────────
#  NEW: PORTFOLIO CORRELATION MATRIX
# ─────────────────────────────────────────────
@st.cache_data(ttl=600)
def compute_correlation(tickers: tuple, period: str = "1y") -> pd.DataFrame:
    """Compute return correlation matrix for a list of tickers."""
    try:
        data = {}
        for t in tickers:
            h = yf.Ticker(t).history(period=period)["Close"]
            if not h.empty:
                data[t] = h.pct_change()
        if len(data) < 2:
            return pd.DataFrame()
        df = pd.DataFrame(data).dropna()
        return df.corr()
    except Exception:
        return pd.DataFrame()



def mini_sparkline(values, color, height=55):
    fig = go.Figure(go.Scatter(
        y=values, mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy", fillcolor=with_alpha(color, 0.12),
    ))
    fig.update_layout(
        height=height, margin=dict(l=0,r=0,t=0,b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        showlegend=False,
    )
    return fig

def to_tradingview_symbol(ticker: str, info: dict = None) -> str:
    t = sanitize_ticker_input(ticker, default="AAPL")
    if t.startswith("^"):
        mapping = {"^GSPC": "SP:SPX", "^IXIC": "NASDAQ:IXIC", "^DJI": "DJ:DJI", "^VIX": "CBOE:VIX"}
        return mapping.get(t, "SP:SPX")
    ex = (info or {}).get("exchange", "")
    if ex in ("NMS", "NAS", "NGM", "NCM"):
        return f"NASDAQ:{t}"
    if ex in ("NYQ", "NYE"):
        return f"NYSE:{t}"
    return f"NASDAQ:{t}"

def render_tradingview_chart(ticker: str, info: dict = None, interval: str = "D", height: int = 640):
    tv_symbol = to_tradingview_symbol(ticker, info)
    tv_height = max(520, int(height) - 24)
    widget = f"""
    <div class="tradingview-widget-container">
      <div id="tradingview_chart" style="height:{tv_height}px;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "container_id": "tradingview_chart",
        "autosize": false,
        "width": "100%",
        "height": {tv_height},
        "symbol": "{tv_symbol}",
        "interval": "{interval}",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "cs",
        "allow_symbol_change": true,
        "studies": ["RSI@tv-basicstudies", "MASimple@tv-basicstudies", "BB@tv-basicstudies", "Volume@tv-basicstudies"],
        "hide_top_toolbar": false,
        "withdateranges": true
      }});
      </script>
    </div>
    """
    components.html(widget, height=height)

# ─────────────────────────────────────────────
#  NAV / HEADER
# ─────────────────────────────────────────────
PAGES = ["Dashboard", "Stock Detail", "Portfolio", "Charts", "Multi-Asset", "Insider", "Earnings", "Alerty", "Screener", "Makro", "Backtesting", "Monte Carlo", "Piotroski", "Settings"]
EMOJIS = {"Dashboard":"📊","Stock Detail":"🔍","Portfolio":"💼","Charts":"📉","Multi-Asset":"🌐","Insider":"👤","Earnings":"📅","Alerty":"🔔","Screener":"🔎","Makro":"🌍","Backtesting":"⚗️","Monte Carlo":"🎲","Piotroski":"🏆","Settings":"⚙️"}
CORE_PAGES = ["Dashboard", "Stock Detail", "Portfolio", "Screener", "Makro", "Alerty"]
NAV_LABELS = {
    "Dashboard": "📊 Home",
    "Stock Detail": "🔍 Akcie",
    "Portfolio": "💼 Portf.",
    "Screener": "🔎 Screener",
    "Makro": "🌍 Makro",
    "Alerty": "🔔 Alerty",
    "Settings": "⚙️ Nastav.",
}

def render_header():
    c1, c2, c3 = st.columns([2, 7, 3])
    with c1:
        st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;padding-top:6px;">
                <span style="font-size:1.8rem;">◆</span>
                <div>
                    <span class="grad" style="font-size:1.3rem;">FinAnalyzer Pro</span><br>
                    <span style="font-size:0.7rem;color:{C['t3']};">v{APP_VERSION} · Real Data · Real Decisions</span>
                </div>
                <span class="status-dot" style="margin-left:4px;"></span>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        cur = st.session_state.get("page", "Dashboard")
        advanced_pages = [p for p in PAGES if p not in CORE_PAGES]
        cols = st.columns(len(CORE_PAGES) + 1)
        for i, page in enumerate(CORE_PAGES):
            with cols[i]:
                kind = "primary" if page == cur else "secondary"
                if st.button(NAV_LABELS.get(page, EMOJIS[page]), key=f"nav_{page}", help=page, type=kind, use_container_width=True):
                    st.session_state["page"] = page
                    st.rerun()
        with cols[-1]:
            adv_default = "Další…"
            adv_choice = st.selectbox(
                "Další stránky",
                [adv_default] + advanced_pages,
                index=0,
                key="nav_more_select",
                label_visibility="collapsed",
            )
            if adv_choice != adv_default and adv_choice != cur:
                st.session_state["page"] = adv_choice
                st.rerun()
    with c3:
        if "header_ticker_input" not in st.session_state:
            st.session_state["header_ticker_input"] = st.session_state.get("ticker", "AAPL")
        ticker_raw = st.text_input(
            "Vyhledat ticker",
            key="header_ticker_input",
            placeholder="🔍 Ticker",
            label_visibility="collapsed",
        )
        ticker = sanitize_ticker_input(ticker_raw, default=st.session_state.get("ticker", "AAPL"))
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        go_search = st.button("Hledat", key="header_search_btn", use_container_width=True)
        if go_search and ticker:
            st.session_state["ticker"] = ticker
            st.session_state["page"] = "Stock Detail"
            st.rerun()

# ─────────────────────────────────────────────
#  PAGE: DASHBOARD
# ─────────────────────────────────────────────
def page_dashboard():
    st.markdown("<h2 class='grad' style='margin:0 0 1rem;'>📊 Market Dashboard</h2>", unsafe_allow_html=True)
    regime = fetch_market_regime()
    if regime:
        reg_col = C["green"] if regime.get("regime") == "RISK-ON" else C["orange"] if regime.get("regime") == "NEUTRAL" else C["red"]
        r1, r2, r3, r4, r5, r6 = st.columns(6)
        with r1: st.metric("Market režim", regime.get("regime", "N/A"))
        with r2: st.metric("Risk score", f"{regime.get('score', 0)}/4")
        with r3: st.metric("SPY 1M", f"{regime.get('SPY', {}).get('m1', 0):+.1f}%")
        with r4: st.metric("QQQ 1M", f"{regime.get('QQQ', {}).get('m1', 0):+.1f}%")
        with r5: st.metric("IWM 1M", f"{regime.get('IWM', {}).get('m1', 0):+.1f}%")
        with r6: st.metric("VIX 1M", f"{regime.get('VIX', {}).get('m1', 0):+.1f}%")
        st.markdown(f"<div style='height:3px;border-radius:10px;background:{with_alpha(reg_col,0.55)};margin-bottom:10px;'></div>", unsafe_allow_html=True)

    # ── Market indices ─────────────────────
    indices = {"S&P 500":"^GSPC","NASDAQ":"^IXIC","DOW":"^DJI","VIX":"^VIX","Russell":"^RUT"}
    cols = st.columns(6)
    for idx,(name,sym) in enumerate(indices.items()):
        with cols[idx]:
            try:
                h = yf.Ticker(sym).history(period="5d")
                if not h.empty and len(h)>=2:
                    cur  = h["Close"].iloc[-1]
                    prev = h["Close"].iloc[-2]
                    chg  = (cur-prev)/prev*100
                    col  = C["green"] if chg>=0 else C["red"]
                    icon = "▲" if chg>=0 else "▼"
                    fig  = mini_sparkline(h["Close"].values, col)
                    st.markdown(f"""
                        <div class="fa-card" style="text-align:center;border-color:{col}30;padding:14px 10px 6px;">
                            <div style="font-size:.7rem;color:{C['t2']};text-transform:uppercase;letter-spacing:.05em;">{name}</div>
                            <div class="mono" style="font-size:1.3rem;font-weight:700;color:{C['t1']};margin:4px 0;">{cur:,.0f}</div>
                            <div style="font-size:.85rem;font-weight:700;color:{col};">{icon} {abs(chg):.2f}%</div>
                        </div>
                    """, unsafe_allow_html=True)
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            except Exception:
                st.markdown(f"<div class='fa-card'><span style='color:{C['t3']};'>{name}</span></div>", unsafe_allow_html=True)

    # Fear & Greed mini tile
    with cols[5]:
        try:
            fg_mini = compute_fear_greed()
            fg_score = fg_mini["score"]; fg_col = fg_mini["color"]; fg_lbl = fg_mini["label"]
            st.markdown(f"""
                <div class="fa-card" style="text-align:center;border-color:{fg_col}30;padding:14px 10px 6px;">
                    <div style="font-size:.7rem;color:{C['t2']};text-transform:uppercase;letter-spacing:.05em;">Fear & Greed</div>
                    <div class="mono" style="font-size:1.3rem;font-weight:700;color:{fg_col};margin:4px 0;">{fg_score}/100</div>
                    <div style="font-size:.78rem;font-weight:700;color:{fg_col};">{fg_lbl}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("📊 Více", key="dash_fg_btn", use_container_width=True):
                st.session_state["page"] = "Sektor Mapa"
                st.rerun()
        except Exception:
            pass

    st.markdown("---")

    # ── Watchlist with live prices ─────────
    data = load_data()
    wl = data.get("watchlist", [])
    st.markdown(f"<h3 style='color:{C['t1']};margin-bottom:.8rem;'>⭐ Watchlist</h3>", unsafe_allow_html=True)

    if wl:
        mdata = fetch_multi(wl)
        sorted_tickers = sorted(mdata.items(), key=lambda x: abs(x[1]["change"]), reverse=True)

        for i in range(0, len(sorted_tickers), 4):
            row_items = sorted_tickers[i:i+4]
            cols = st.columns(4)
            for j,(t,info) in enumerate(row_items):
                with cols[j]:
                    chg   = info["change"]
                    col   = C["green"] if chg>=0 else C["red"]
                    icon  = "▲" if chg>=0 else "▼"
                    mc    = f"${info['market_cap']/1e9:.1f}B" if info['market_cap'] else "–"
                    st.markdown(f"""
                        <div class="fa-card" style="border-color:{col}25;cursor:pointer;">
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <span style="font-weight:700;font-size:1rem;color:{C['blue']};">{t}</span>
                                <span style="font-size:.75rem;color:{C['t3']};">{info.get('sector','')[:12]}</span>
                            </div>
                            <div class="mono" style="font-size:1.6rem;font-weight:800;color:{C['t1']};margin:6px 0;">${info['price']:,.2f}</div>
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <span style="color:{col};font-weight:700;font-size:.9rem;">{icon} {abs(chg):.2f}%</span>
                                <span style="color:{C['t3']};font-size:.75rem;">MC: {mc}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("🔍 Detail", key=f"det_{t}", use_container_width=True):
                            st.session_state["ticker"] = t
                            st.session_state["page"] = "Stock Detail"
                            st.rerun()
                    with c2:
                        if st.button("➕ Port.", key=f"port_{t}", use_container_width=True):
                            st.session_state["ticker"] = t
                            st.session_state["page"] = "Portfolio"
                            st.rerun()

    st.markdown("---")

    # ── Top Movers ────────────────────────
    st.markdown(f"<h3 style='color:{C['t1']};margin-bottom:.8rem;'>🔥 Top Movers</h3>", unsafe_allow_html=True)
    mover_tickers = ["TSLA","NVDA","AMD","PLTR","SOFI","COIN","HOOD","SNAP","RIVN","LCID","MARA","RIOT"]
    mdata2 = fetch_multi(mover_tickers)
    if mdata2:
        top = sorted(mdata2.items(), key=lambda x: abs(x[1]["change"]), reverse=True)[:6]
        cols = st.columns(6)
        for idx,(t,info) in enumerate(top):
            with cols[idx]:
                chg = info["change"]
                col = C["green"] if chg>=0 else C["red"]
                st.markdown(f"""
                    <div class="fa-card" style="text-align:center;border-color:{col}30;padding:12px 8px;">
                        <div style="font-weight:700;color:{C['blue']};font-size:.95rem;">{t}</div>
                        <div class="mono" style="font-size:1.2rem;font-weight:800;margin:4px 0;color:{col};">{chg:+.2f}%</div>
                        <div class="mono" style="font-size:.85rem;color:{C['t2']};">${info['price']:,.2f}</div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("🔍", key=f"mv_{t}", use_container_width=True):
                    st.session_state["ticker"] = t
                    st.session_state["page"] = "Stock Detail"
                    st.rerun()

# ─────────────────────────────────────────────
#  PAGE: STOCK DETAIL + BUY SCORE
# ─────────────────────────────────────────────
def page_stock_detail():
    ticker = sanitize_ticker_input(st.session_state.get("ticker","AAPL"))
    st.session_state["ticker"] = ticker
    st.markdown(f"<h2 class='grad' style='margin:0 0 1rem;'>🔍 {ticker} — Analýza</h2>", unsafe_allow_html=True)

    df, info = fetch_stock(ticker, period="1y")
    if df is None or df.empty:
        st.error(f"Nepodařilo se načíst data pro {ticker}. Zkontroluj ticker.")
        return

    df_ind = calc_indicators(df)
    analyst  = fetch_analyst_info(ticker)
    insider  = fetch_insider_sec(ticker)
    score_data = compute_buy_score(df_ind, info, analyst, insider)
    news     = fetch_news(ticker)

    cur   = df["Close"].iloc[-1]
    prev  = df["Close"].iloc[-2] if len(df)>1 else cur
    chg   = (cur-prev)/prev*100
    col   = C["green"] if chg>=0 else C["red"]
    risk_pack = compute_risk_pack(df, info, cur)

    # ── Hero header ──────────────────────
    mc    = info.get("marketCap",0)
    vol   = info.get("volume", df["Volume"].iloc[-1] if not df.empty else 0)
    pe    = info.get("trailingPE",0)
    eps   = info.get("trailingEps",0)
    h52   = info.get("fiftyTwoWeekHigh",0)
    l52   = info.get("fiftyTwoWeekLow",0)
    name  = info.get("shortName", ticker)
    sector= info.get("sector","")
    div_y = info.get("dividendYield",0) or 0

    st.markdown(f"""
        <div class="fa-card" style="border-color:{col}30;margin-bottom:1rem;">
            <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:16px;align-items:center;">
                <div>
                    <div style="font-size:.8rem;color:{C['t3']};text-transform:uppercase;letter-spacing:.08em;">{sector}</div>
                    <div style="font-size:1.8rem;font-weight:800;color:{C['t1']};">{name}</div>
                    <span style="background:{C['blue_d']};color:{C['blue']};padding:3px 10px;border-radius:20px;font-size:.8rem;font-weight:700;">{ticker}</span>
                </div>
                <div style="text-align:center;">
                    <div class="mono" style="font-size:3rem;font-weight:800;color:{C['t1']};">${cur:.2f}</div>
                    <div class="mono" style="font-size:1.3rem;font-weight:700;color:{col};">{'▲' if chg>=0 else '▼'} {abs(chg):.2f}%  (${abs(cur-prev):.2f})</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    kpi_cols = st.columns(6)
    kpis = [
        ("MC", f"${mc/1e9:.1f}B" if mc else "–"),
        ("P/E", f"{pe:.1f}" if pe else "–"),
        ("52W", f"${l52:.0f} – ${h52:.0f}" if h52 and l52 else "–"),
        ("Vol", f"{vol/1e6:.1f}M" if vol else "–"),
        ("EPS", f"${eps:.2f}" if eps else "–"),
        ("Div", f"{div_y*100:.2f}%" if div_y is not None else "–"),
    ]
    for i, (lbl, val) in enumerate(kpis):
        with kpi_cols[i]:
            st.markdown(f"""
                <div class="fa-card" style="padding:10px 12px;margin-bottom:10px;">
                    <div style="font-size:.70rem;color:{C['t3']};text-transform:uppercase;">{lbl}</div>
                    <div class="mono" style="font-size:1.05rem;font-weight:700;color:{C['t1']};white-space:nowrap;">{val}</div>
                </div>
            """, unsafe_allow_html=True)

    # Portfolio action buttons
    data = load_data()
    ba1, ba2, ba3, ba4 = st.columns(4)
    with ba1:
        if st.button("💰 Přidat do portfolia", use_container_width=True):
            st.session_state["page"] = "Portfolio"
            st.session_state["ticker"] = ticker
            st.rerun()
    with ba2:
        if st.button("⭐ Přidat do watchlistu", use_container_width=True):
            if ticker not in data["watchlist"]:
                data["watchlist"].append(ticker)
                save_data(data)
                st.toast(f"{ticker} přidán do watchlistu!")
    with ba3:
        if st.button("🔔 Nastavit alert", use_container_width=True):
            st.session_state["page"] = "Alerty"
            st.session_state["alert_ticker"] = ticker
            st.rerun()
    with ba4:
        if st.button("📅 Earnings", use_container_width=True):
            st.session_state["earnings_ticker"] = ticker
            st.toast("Zůstáváš na stránce analýzy akcie. Earnings detail najdeš v sekci Earnings bez automatického přepnutí.")

    with st.expander("📎 Detail o akcii", expanded=True):
        d1, d2 = st.columns(2)
        with d1:
            st.markdown(f"""
                <div style="font-size:.83rem;color:{C['t2']};line-height:1.7;">
                    <b>Odvětví:</b> {info.get("industry","–")}<br>
                    <b>Země:</b> {info.get("country","–")}<br>
                    <b>Beta:</b> {f"{info.get('beta'):.2f}" if isinstance(info.get('beta'), (int,float)) else "–"}<br>
                    <b>Průměrný objem:</b> {f"{info.get('averageVolume',0)/1e6:.1f}M" if info.get("averageVolume") else "–"}<br>
                </div>
            """, unsafe_allow_html=True)
        with d2:
            web = info.get("website", "–")
            st.markdown(f"""
                <div style="font-size:.83rem;color:{C['t2']};line-height:1.7;">
                    <b>Zaměstnanci:</b> {f"{info.get('fullTimeEmployees'):,}" if info.get("fullTimeEmployees") else "–"}<br>
                    <b>Forward EPS:</b> {f"{info.get('forwardEps'):.2f}" if isinstance(info.get('forwardEps'), (int,float)) else "–"}<br>
                    <b>Forward P/E:</b> {f"{info.get('forwardPE'):.2f}" if isinstance(info.get('forwardPE'), (int,float)) else "–"}<br>
                    <b>Web:</b> <a href="{web}" target="_blank" style="color:{C['blue']};">{web}</a><br>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Tabs ──────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(["📈 Graf", "🎯 Buy Score", "📊 Fundamenty", "📰 Zprávy", "👤 Insider", "💰 DCF Kalkulačka", "📅 Sezónnost", "📉 Rel. Síla", "🏦 Instituce & Opce"])

    # ── TAB 1: Chart ──────────────────────
    with tab1:
        if "tf" not in st.session_state:
            st.session_state["tf"] = "1Y"
        tf = st.session_state["tf"]
        tv_map = {"1D":"5", "5D":"30", "1M":"60", "3M":"240", "6M":"D", "1Y":"D", "MAX":"W"}
        c1,c2,c3,c4,c5,c6,c7,_ = st.columns([1,1,1,1,1,1,1,5])
        for col_obj, label in zip([c1,c2,c3,c4,c5,c6,c7],["1D","5D","1M","3M","6M","1Y","MAX"]):
            with col_obj:
                if st.button(label, key=f"tf_{label}", type="primary" if tf==label else "secondary"):
                    st.session_state["tf"] = label
                    st.rerun()

        render_tradingview_chart(ticker, info, interval=tv_map.get(tf, "D"), height=920)

    # ── TAB 2: Buy Score ──────────────────
    with tab2:
        sd = score_data
        if sd["score"] is None:
            st.warning("Nedostatek dat pro výpočet skóre (potřeba alespoň 50 svíček).")
        else:
            sc1, sc2 = st.columns([1, 2])
            with sc1:
                score = sd["score"]
                color = sd["color"]
                label = sd["label"]
                # Gauge chart
                fig_g = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    number={"font":{"size":48,"family":"JetBrains Mono","color":color},"suffix":""},
                    gauge={
                        "axis":{"range":[0,100],"tickfont":{"color":C["t2"]},"tickcolor":C["t2"]},
                        "bar":{"color":color,"thickness":0.25},
                        "bgcolor":"rgba(0,0,0,0)",
                        "bordercolor":C["border"],
                        "steps":[
                            {"range":[0,28],"color":"rgba(255,61,90,0.15)"},
                            {"range":[28,45],"color":"rgba(245,158,11,0.10)"},
                            {"range":[45,62],"color":"rgba(255,255,255,0.04)"},
                            {"range":[62,80],"color":"rgba(74,222,128,0.10)"},
                            {"range":[80,100],"color":"rgba(0,230,118,0.18)"},
                        ],
                        "threshold":{"line":{"color":color,"width":3},"thickness":0.8,"value":score},
                    },
                ))
                fig_g.update_layout(height=280, margin=dict(l=20,r=20,t=20,b=10),
                    paper_bgcolor="rgba(0,0,0,0)", font=dict(color=C["t1"]))
                st.plotly_chart(fig_g, use_container_width=True, config={"displayModeBar":False})
                st.markdown(f"""
                    <div style="text-align:center;margin-top:-10px;">
                        <div style="font-size:1.6rem;font-weight:800;color:{color};">{label}</div>
                        <div style="font-size:.8rem;color:{C['t3']};margin-top:4px;">Buy Score {score}/100</div>
                    </div>
                """, unsafe_allow_html=True)

            with sc2:
                st.markdown(f"<div style='font-size:.9rem;font-weight:600;color:{C['t2']};margin-bottom:8px;'>Složky skóre</div>", unsafe_allow_html=True)
                comp = sd["components"]
                weights = sd["weights"]
                if sd.get("confidence") is not None:
                    conf = sd["confidence"]
                    conf_col = C["green"] if conf >= 75 else C["orange"] if conf >= 55 else C["red"]
                    st.markdown(f"""
                        <div style="padding:8px 10px;margin-bottom:10px;border-radius:8px;background:{C['bg2']};border:1px solid {C['border']};">
                            <span style="font-size:.8rem;color:{C['t2']};">Spolehlivost modelu:</span>
                            <span class="mono" style="font-size:.9rem;font-weight:700;color:{conf_col};float:right;">{conf:.0f}%</span>
                        </div>
                    """, unsafe_allow_html=True)
                for name_c, val in comp.items():
                    w   = weights[name_c]
                    col_c = C["green"] if val>=65 else C["orange"] if val>=45 else C["red"]
                    st.markdown(f"""
                        <div style="margin-bottom:10px;">
                            <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                                <span style="font-size:.82rem;color:{C['t1']};font-weight:500;">{name_c}</span>
                                <span style="font-size:.82rem;color:{C['t3']};">váha {w}% &nbsp;·&nbsp; <span class="mono" style="color:{col_c};">{val:.0f}/100</span></span>
                            </div>
                            <div style="height:6px;background:{C['border']};border-radius:3px;">
                                <div style="height:100%;width:{val}%;background:{col_c};border-radius:3px;box-shadow:0 0 6px {col_c}44;"></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown(f"<div style='font-size:.9rem;font-weight:600;color:{C['t2']};margin-bottom:8px;'>Detailní signály</div>", unsafe_allow_html=True)
            ranked_signals = sorted(sd["signals"], key=lambda x: 0 if x[2] is not None else 1)
            visible_signals = ranked_signals
            hidden_signals = []

            for name_s, desc, bullish in visible_signals:
                if bullish is True:
                    icon, col_s = "✅", C["green"]
                elif bullish is False:
                    icon, col_s = "❌", C["red"]
                else:
                    icon, col_s = "⚪", C["t3"]
                st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:10px;padding:6px 10px;background:{C['card']};border-radius:8px;margin-bottom:4px;border:1px solid {C['border']};">
                        <span>{icon}</span>
                        <span style="font-size:.82rem;font-weight:600;color:{C['t2']};min-width:140px;">{name_s}</span>
                        <span style="font-size:.82rem;color:{col_s};">{desc}</span>
                    </div>
                """, unsafe_allow_html=True)
            if hidden_signals:
                with st.expander(f"Další signály ({len(hidden_signals)})"):
                    for name_s, desc, bullish in hidden_signals:
                        if bullish is True:
                            icon, col_s = "✅", C["green"]
                        elif bullish is False:
                            icon, col_s = "❌", C["red"]
                        else:
                            icon, col_s = "⚪", C["t3"]
                        st.markdown(f"""
                            <div style="display:flex;align-items:center;gap:10px;padding:6px 10px;background:{C['card']};border-radius:8px;margin-bottom:4px;border:1px solid {C['border']};">
                                <span>{icon}</span>
                                <span style="font-size:.82rem;font-weight:600;color:{C['t2']};min-width:140px;">{name_s}</span>
                                <span style="font-size:.82rem;color:{col_s};">{desc}</span>
                            </div>
                        """, unsafe_allow_html=True)

            st.markdown(f"""
                <div style="margin-top:14px;padding:10px 14px;background:{C['bg2']};border-radius:8px;border-left:3px solid {C['orange']};font-size:.78rem;color:{C['t3']};">
                ⚠️ Buy Score je analytický nástroj kombinující techniku, fundamenty, momentum, analytiky a insider data. 
                Není to investiční poradenství. Vždy proveď vlastní due diligence před investicí.
                </div>
            """, unsafe_allow_html=True)

    # ── TAB 3: Fundamenty ─────────────────
    with tab3:
        income = None
        balance = None
        try:
            s_obj = yf.Ticker(ticker)
            income  = s_obj.financials
            balance = s_obj.balance_sheet
        except Exception:
            pass

        fc1, fc2 = st.columns(2)
        with fc1:
            st.markdown(f"<div style='font-weight:600;color:{C['t2']};margin-bottom:8px;'>Valuace</div>", unsafe_allow_html=True)
            metrics = [
                ("P/E (TTM)",        info.get("trailingPE")),
                ("Forward P/E",      info.get("forwardPE")),
                ("PEG Ratio",        info.get("pegRatio")),
                ("P/B Ratio",        info.get("priceToBook")),
                ("P/S Ratio",        info.get("priceToSalesTrailing12Months")),
                ("EV/EBITDA",        info.get("enterpriseToEbitda")),
            ]
            for label, val in metrics:
                v = f"{val:.2f}" if val and isinstance(val, float) else (str(val) if val else "–")
                st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;padding:7px 10px;border-bottom:1px solid {C['border']};">
                        <span style="font-size:.83rem;color:{C['t2']};">{label}</span>
                        <span class="mono" style="font-size:.83rem;color:{C['t1']};font-weight:600;">{v}</span>
                    </div>
                """, unsafe_allow_html=True)

        with fc2:
            st.markdown(f"<div style='font-weight:600;color:{C['t2']};margin-bottom:8px;'>Profitabilita & Zdraví</div>", unsafe_allow_html=True)
            metrics2 = [
                ("ROE",              f"{info.get('returnOnEquity',0)*100:.1f}%" if info.get('returnOnEquity') else "–"),
                ("ROA",              f"{info.get('returnOnAssets',0)*100:.1f}%" if info.get('returnOnAssets') else "–"),
                ("Zisková marže",    f"{info.get('profitMargins',0)*100:.1f}%" if info.get('profitMargins') else "–"),
                ("Hrubá marže",      f"{info.get('grossMargins',0)*100:.1f}%" if info.get('grossMargins') else "–"),
                ("Dluh/Vlastní kap.",f"{info.get('debtToEquity',0):.1f}" if info.get('debtToEquity') else "–"),
                ("Current Ratio",    f"{info.get('currentRatio',0):.2f}" if info.get('currentRatio') else "–"),
            ]
            for label, val in metrics2:
                st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;padding:7px 10px;border-bottom:1px solid {C['border']};">
                        <span style="font-size:.83rem;color:{C['t2']};">{label}</span>
                        <span class="mono" style="font-size:.83rem;color:{C['t1']};font-weight:600;">{val}</span>
                    </div>
                """, unsafe_allow_html=True)

        # Analyst targets
        if analyst:
            st.markdown("---")
            st.markdown(f"<div style='font-weight:600;color:{C['t2']};margin-bottom:8px;'>Analytici ({analyst.get('num_analysts',0)} hodnotí)</div>", unsafe_allow_html=True)
            target = analyst.get("target_mean",0)
            upside = (target - cur)/cur*100 if target and cur else 0
            ac1, ac2, ac3, ac4 = st.columns(4)
            with ac1: st.metric("Průměrný target", f"${target:.2f}" if target else "–")
            with ac2: st.metric("Upside", f"{upside:+.1f}%" if target else "–")
            with ac3: st.metric("High target", f"${analyst.get('target_high',0):.2f}" if analyst.get('target_high') else "–")
            with ac4: st.metric("Low target", f"${analyst.get('target_low',0):.2f}" if analyst.get('target_low') else "–")

            # Rating bar
            rec = analyst.get("rec_summary",{})
            total_r = sum(rec.values())
            if total_r > 0:
                st.markdown(f"""
                    <div style="margin-top:12px;background:{C['card']};border-radius:8px;overflow:hidden;height:20px;display:flex;">
                        {"".join([
                            f'<div title="{k}: {v}" style="width:{v/total_r*100:.1f}%;background:{col2};"></div>'
                            for k, v, col2 in [
                                ("Strong Buy",  rec.get("strongBuy",0),  "#00e676"),
                                ("Buy",         rec.get("buy",0),        "#4ade80"),
                                ("Hold",        rec.get("hold",0),       "#f59e0b"),
                                ("Sell",        rec.get("sell",0),       "#fb923c"),
                                ("Strong Sell", rec.get("strongSell",0), "#ff3d5a"),
                            ] if v > 0
                        ])}
                    </div>
                    <div style="display:flex;gap:10px;margin-top:6px;flex-wrap:wrap;">
                        {"".join([f'<span style="font-size:.72rem;color:{C["t3"]};">{k}: {v}</span>' for k,v in [
                            ("Strong Buy",rec.get("strongBuy",0)),("Buy",rec.get("buy",0)),
                            ("Hold",rec.get("hold",0)),("Sell",rec.get("sell",0)),("Strong Sell",rec.get("strongSell",0))
                        ]])}
                    </div>
                """, unsafe_allow_html=True)

    # ── TAB 4: News ───────────────────────
    with tab4:
        if not news:
            st.info("Žádné zprávy nebyly nalezeny.")
        for n in news[:12]:
            title     = html.escape(str(n.get("title","")))
            publisher = html.escape(str(n.get("publisher","")))
            link      = str(n.get("link","#")) if str(n.get("link","#")).startswith("http") else "#"
            ts        = n.get("providerPublishTime", 0)
            try:
                dt_str = datetime.fromtimestamp(int(ts)).strftime("%d.%m.%Y %H:%M") if ts else ""
            except Exception:
                dt_str = ""
            st.markdown(f"""
                <a href="{link}" target="_blank" style="text-decoration:none;">
                <div class="fa-card" style="border-left:3px solid {C['blue']};border-radius:0 10px 10px 0;margin-bottom:8px;padding:12px 16px;">
                    <div style="font-size:.88rem;font-weight:600;color:{C['t1']};margin-bottom:4px;">{title}</div>
                    <div style="font-size:.75rem;color:{C['t3']};">{publisher} &nbsp;·&nbsp; {dt_str}</div>
                </div>
                </a>
            """, unsafe_allow_html=True)

    # ── TAB 5: Insider (SEC EDGAR) ────────
    with tab5:
        st.markdown(f"<div style='font-size:.82rem;color:{C['t3']};margin-bottom:8px;'>Reálná data ze SEC EDGAR — Form 4 podání za posledních 6 měsíců</div>", unsafe_allow_html=True)
        if not insider:
            st.info("Nenalezeny žádné Form-4 záznamy pro tento ticker za posledních 6 měsíců, nebo se nepodařilo spojit se SEC EDGAR.")
        else:
            st.markdown(f"""
                <div style="background:{C['card']};border-radius:10px;overflow:hidden;border:1px solid {C['border']};">
                    <div style="display:flex;gap:10px;padding:8px 14px;background:{C['bg2']};font-size:.72rem;color:{C['t3']};text-transform:uppercase;font-weight:600;letter-spacing:.05em;">
                        <span style="flex:1;">Datum</span>
                        <span style="flex:1;">Formulář</span>
                        <span style="flex:2;">Odkaz SEC</span>
                    </div>
            """, unsafe_allow_html=True)
            for tr in insider[:15]:
                acc_clean = tr["accession"].replace("-","")
                cik_c     = tr["cik"]
                sec_url   = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik_c}&type=4&dateb=&owner=include&count=40"
                st.markdown(f"""
                    <div style="display:flex;gap:10px;padding:8px 14px;border-bottom:1px solid {C['border']};align-items:center;">
                        <span class="mono" style="flex:1;font-size:.82rem;color:{C['t1']};">{tr['date']}</span>
                        <span style="flex:1;font-size:.82rem;color:{C['blue']};">Form 4</span>
                        <a href="{sec_url}" target="_blank" style="flex:2;font-size:.78rem;color:{C['t3']};text-decoration:none;">SEC EDGAR →</a>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:.75rem;color:{C['t3']};margin-top:8px;'>Celkem nalezeno {len(insider)} Form-4 podání. Data: SEC EDGAR (data.sec.gov)</div>", unsafe_allow_html=True)

    # ── TAB 6: DCF Kalkulačka ─────────────
    with tab6:
        st.markdown(f"<div style='font-size:.83rem;color:{C['t3']};margin-bottom:1rem;'>Discounted Cash Flow — odhadni fair value akcie na základě budoucích cash flow. Uprav předpoklady a zjisti, zda je akcie podhodnocená.</div>", unsafe_allow_html=True)
        dcf_c1, dcf_c2 = st.columns([1, 1])
        with dcf_c1:
            st.markdown(f"<div style='font-weight:600;color:{C['t2']};margin-bottom:8px;'>Parametry modelu</div>", unsafe_allow_html=True)
            dcf_growth   = st.number_input("Roční růst FCF (%)", min_value=0.0, max_value=40.0, value=10.0, step=0.1, format="%.1f") / 100
            dcf_terminal = st.number_input("Terminální růst (%)", min_value=0.0, max_value=5.0, value=3.0, step=0.1, format="%.1f") / 100
            dcf_discount = st.number_input("Diskontní sazba / WACC (%)", min_value=5.0, max_value=20.0, value=10.0, step=0.1, format="%.1f") / 100
            dcf_years    = st.slider("Projekční horizont (roky)", 5, 15, 10, 1)
            margin_of_safety = st.number_input("Požadovaný margin of safety (%)", min_value=0.0, max_value=80.0, value=20.0, step=1.0, format="%.0f") / 100
        with dcf_c2:
            fcf_payload = get_unlevered_fcf_ttm(ticker, info)
            fcf_raw = fcf_payload["value"]
            shares_payload = resolve_shares_outstanding(info, cur)
            shares_out = shares_payload["value"]
            st.markdown(f"<div style='font-weight:600;color:{C['t2']};margin-bottom:8px;'>Vstupní data ({ticker})</div>", unsafe_allow_html=True)
            st.markdown(f"""
                <div style="background:{C['card']};border-radius:8px;padding:12px 14px;border:1px solid {C['border']};">
                    <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid {C['border']};">
                        <span style="font-size:.82rem;color:{C['t2']};">Free Cash Flow (TTM, unlevered)</span>
                        <span class="mono" style="font-size:.82rem;color:{C['t1']};font-weight:600;">${fcf_raw/1e9:.2f}B</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid {C['border']};">
                        <span style="font-size:.82rem;color:{C['t2']};">Akcie v oběhu</span>
                        <span class="mono" style="font-size:.82rem;color:{C['t1']};font-weight:600;">{shares_out/1e9:.2f}B</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid {C['border']};">
                        <span style="font-size:.82rem;color:{C['t2']};">Cash & ekvivalenty</span>
                        <span class="mono" style="font-size:.82rem;color:{C['t1']};font-weight:600;">${info.get('totalCash',0)/1e9:.2f}B</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:5px 0;">
                        <span style="font-size:.82rem;color:{C['t2']};">Celkový dluh</span>
                        <span class="mono" style="font-size:.82rem;color:{C['t1']};font-weight:600;">${info.get('totalDebt',0)/1e9:.2f}B</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.caption(f"Zdroj FCF: {fcf_payload['source']}")
            st.caption(f"Zdroj počtu akcií: {shares_payload['source']}")
            if fcf_payload["fallback"]:
                st.warning("Nepodařilo se načíst OCF/CapEx z cash-flow výkazů, použit fallback z info.freeCashflow.")
            if shares_payload["fallback"]:
                st.warning("Počet akcií není přímo dostupný, byl použit fallback odhad.")

        dcf = compute_dcf(info, growth_rate=dcf_growth, terminal_growth=dcf_terminal,
                          discount_rate=dcf_discount, years=dcf_years, base_fcf=fcf_raw,
                          shares_outstanding=shares_out)
        st.markdown("---")
        if dcf["error"]:
            st.warning(f"DCF nelze spočítat: {dcf['error']}")
        else:
            fv    = dcf["fair_value"]
            upside_dcf = (fv - cur) / cur * 100 if fv and cur else 0
            entry_price = fv * (1 - margin_of_safety) if fv else None
            fv_col = C["green"] if upside_dcf > 10 else C["orange"] if upside_dcf > -10 else C["red"]
            d1, d2, d3, d4, d5 = st.columns(5)
            with d1:
                st.markdown(f"""
                    <div class="fa-card" style="text-align:center;border-color:{fv_col}40;">
                        <div style="font-size:.72rem;color:{C['t2']};text-transform:uppercase;">DCF Fair Value</div>
                        <div class="mono" style="font-size:2rem;font-weight:800;color:{fv_col};margin:6px 0;">${fv:.2f}</div>
                        <div style="font-size:.85rem;color:{fv_col};font-weight:700;">{'▲ Podhodnocená' if upside_dcf>10 else '▼ Nadhodnocená' if upside_dcf<-10 else '≈ Férová cena'}</div>
                    </div>
                """, unsafe_allow_html=True)
            with d2: st.metric("Aktuální cena", f"${cur:.2f}")
            with d3: st.metric("Upside / Downside", f"{upside_dcf:+.1f}%")
            with d4: st.metric("Enterprise Value", f"${dcf['enterprise_val']:.1f}B")
            with d5: st.metric("Discipl. nákupní cena", f"${entry_price:.2f}" if entry_price else "–")

            st.markdown(f"<div style='font-size:.85rem;font-weight:600;color:{C['t2']};margin:10px 0 6px;'>Scénáře fair value (Investor view)</div>", unsafe_allow_html=True)
            scenarios = [
                ("Bear", max(dcf_growth - 0.02, 0.0), max(dcf_terminal - 0.005, 0.0), min(dcf_discount + 0.01, 0.25)),
                ("Base", dcf_growth, dcf_terminal, dcf_discount),
                ("Bull", min(dcf_growth + 0.02, 0.60), min(dcf_terminal + 0.005, 0.08), max(dcf_discount - 0.01, 0.04)),
            ]
            rows = []
            for name_s, g_s, t_s, d_s in scenarios:
                out = compute_dcf(
                    info,
                    growth_rate=g_s,
                    terminal_growth=t_s,
                    discount_rate=d_s,
                    years=dcf_years,
                    base_fcf=fcf_raw,
                    shares_outstanding=shares_out,
                )
                fv_s = out["fair_value"] if out and out.get("fair_value") else None
                up_s = ((fv_s - cur) / cur * 100) if fv_s and cur else None
                rows.append({
                    "Scénář": name_s,
                    "Růst FCF": f"{g_s*100:.1f}%",
                    "Terminál": f"{t_s*100:.1f}%",
                    "WACC": f"{d_s*100:.1f}%",
                    "Fair Value": f"${fv_s:.2f}" if fv_s else "N/A",
                    "Upside": f"{up_s:+.1f}%" if up_s is not None else "N/A",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            # Waterfall: PV of each projected year
            st.markdown(f"<div style='font-size:.85rem;font-weight:600;color:{C['t2']};margin:12px 0 6px;'>Diskontované cash flow po letech ($B)</div>", unsafe_allow_html=True)
            yrs = [f"Rok {i+1}" for i in range(dcf_years)] + ["Terminal"]
            vals = dcf["projected_pvs"] + [dcf["terminal_pv"]]
            dcf_fig = go.Figure(go.Bar(
                x=yrs, y=vals,
                marker_color=[C["blue"]]*dcf_years + [C["purple"]],
                marker_opacity=0.85,
                text=[f"${v:.3f}B" for v in vals],
                textposition="outside", textfont=dict(color=C["t2"], size=10),
            ))
            dcf_fig.update_layout(**{**CHART_LAYOUT, "margin": dict(l=10,r=10,t=10,b=30)},
                height=280, showlegend=False)
            st.plotly_chart(dcf_fig, use_container_width=True, config={"displayModeBar":False})
            st.markdown(f"""
                <div style="padding:8px 12px;background:{C['bg2']};border-radius:8px;border-left:3px solid {C['orange']};font-size:.75rem;color:{C['t3']};">
                ⚠️ DCF je citlivý na vstupní předpoklady. Malá změna diskontní sazby nebo terminálního růstu může výrazně změnit výsledek.
                Tato kalkulačka je pouze orientační a není investičním doporučením.
                </div>
            """, unsafe_allow_html=True)

    # ── TAB 7: Sezónnost ─────────────────
    with tab7:
        st.markdown(f"<div style='font-size:.83rem;color:{C['t3']};margin-bottom:1rem;'>Průměrný měsíční výkon akcie za posledních 10 let. Pomáhá identifikovat sezónní vzory a optimální timing.</div>", unsafe_allow_html=True)
        with st.spinner("Počítám sezónnost…"):
            seas = compute_seasonality(ticker)
        if seas.empty:
            st.info("Nedostatek dat pro sezónní analýzu.")
        else:
            months = list(seas.index)
            avgs   = list(seas["avg"])
            pos_pct = list(seas["positive_pct"])
            bar_colors = [C["green"] if v >= 0 else C["red"] for v in avgs]
            sea_fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                    row_heights=[0.65, 0.35], vertical_spacing=0.04)
            sea_fig.add_trace(go.Bar(
                x=months, y=avgs, name="Průměrný výnos",
                marker_color=bar_colors, marker_opacity=0.85,
                text=[f"{v:+.1f}%" for v in avgs],
                textposition="outside", textfont=dict(color=C["t2"], size=10),
            ), row=1, col=1)
            sea_fig.add_hline(y=0, line_color=C["border"], row=1, col=1)
            sea_fig.add_trace(go.Bar(
                x=months, y=pos_pct, name="% pozitivních let",
                marker_color=C["blue"], marker_opacity=0.6,
                text=[f"{v:.0f}%" for v in pos_pct],
                textposition="outside", textfont=dict(color=C["t2"], size=9),
            ), row=2, col=1)
            sea_fig.add_hline(y=50, line_dash="dash", line_color=C["t3"], opacity=.5, row=2, col=1)
            sea_fig.update_layout(**CHART_LAYOUT, height=420, showlegend=True,
                legend=dict(orientation="h", y=1.02, bgcolor="rgba(0,0,0,0)"))
            sea_fig.update_yaxes(ticksuffix="%", row=1, col=1)
            sea_fig.update_yaxes(ticksuffix="%", row=2, col=1)
            st.plotly_chart(sea_fig, use_container_width=True, config={"displayModeBar":False})

            # Best / worst months highlight
            best_month  = seas["avg"].idxmax()
            worst_month = seas["avg"].idxmin()
            st.markdown(f"""
                <div style="display:flex;gap:12px;margin-top:8px;">
                    <div class="fa-card" style="flex:1;text-align:center;border-color:{C['green']}40;">
                        <div style="font-size:.72rem;color:{C['t2']};text-transform:uppercase;">Nejsilnější měsíc</div>
                        <div class="mono" style="font-size:1.6rem;font-weight:800;color:{C['green']};">{best_month}</div>
                        <div style="font-size:.9rem;color:{C['green']};font-weight:700;">{seas['avg'][best_month]:+.1f}% průměrně</div>
                        <div style="font-size:.75rem;color:{C['t3']};">{seas['positive_pct'][best_month]:.0f}% let v plusu</div>
                    </div>
                    <div class="fa-card" style="flex:1;text-align:center;border-color:{C['red']}40;">
                        <div style="font-size:.72rem;color:{C['t2']};text-transform:uppercase;">Nejslabší měsíc</div>
                        <div class="mono" style="font-size:1.6rem;font-weight:800;color:{C['red']};">{worst_month}</div>
                        <div style="font-size:.9rem;color:{C['red']};font-weight:700;">{seas['avg'][worst_month]:+.1f}% průměrně</div>
                        <div style="font-size:.75rem;color:{C['t3']};">{seas['positive_pct'][worst_month]:.0f}% let v plusu</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # ── TAB 8: Relativní síla ─────────────
    with tab8:
        st.markdown(f"<div style='font-size:.83rem;color:{C['t3']};margin-bottom:1rem;'>Relativní síla {ticker} vs. S&P 500. Hodnota nad 1.0 = outperformance. Rostoucí linka = akcelerující alpha.</div>", unsafe_allow_html=True)
        rs_period = st.selectbox("Období RS", ["3mo","6mo","1y","2y","5y"], index=2, key="rs_period")
        with st.spinner("Načítám…"):
            rs = compute_relative_strength(ticker, rs_period)
        if rs.empty or len(rs) < 5:
            st.info("Nedostatek dat pro výpočet relativní síly.")
        else:
            rs_start = rs.iloc[0]
            rs_end   = rs.iloc[-1]
            rs_delta = (rs_end - rs_start) / rs_start * 100
            rs_col   = C["green"] if rs_end > 1.0 else C["red"]

            rm1, rm2, rm3 = st.columns(3)
            with rm1: st.metric("Aktuální RS", f"{rs_end:.3f}", f"{'▲ Outperform' if rs_end>1.0 else '▼ Underperform'}")
            with rm2:
                t_ret  = (yf.Ticker(ticker).history(period=rs_period)["Close"])
                t_ret_pct = (t_ret.iloc[-1]/t_ret.iloc[0]-1)*100 if not t_ret.empty else 0
                st.metric(f"{ticker} výnos", f"{t_ret_pct:+.1f}%")
            with rm3:
                sp_ret = (yf.Ticker("^GSPC").history(period=rs_period)["Close"])
                sp_pct = (sp_ret.iloc[-1]/sp_ret.iloc[0]-1)*100 if not sp_ret.empty else 0
                st.metric("S&P 500 výnos", f"{sp_pct:+.1f}%")

            rs_fig = go.Figure()
            rs_fig.add_trace(go.Scatter(
                x=rs.index, y=rs.values, name=f"{ticker} / SPX",
                line=dict(color=rs_col, width=2.2),
                fill="tozeroy", fillcolor=with_alpha(rs_col, 0.09),
            ))
            rs_fig.add_hline(y=1.0, line_dash="dash", line_color=C["t3"], opacity=.6)
            rs_fig.update_layout(**CHART_LAYOUT, height=320, showlegend=False)
            rs_fig.update_yaxes(tickformat=".3f", gridcolor=C["grid"])
            st.plotly_chart(rs_fig, use_container_width=True, config={"displayModeBar":False})

            # RS moving average trend
            rs_ser = pd.Series(rs.values, index=rs.index)
            rs_ma  = rs_ser.rolling(20).mean()
            trend_up = rs_ser.iloc[-1] > rs_ma.iloc[-1] if not rs_ma.isna().iloc[-1] else None
            if trend_up is not None:
                trend_text = "Relativní síla je nad svým 20denním průměrem — momentum se zlepšuje" if trend_up else "Relativní síla je pod svým 20denním průměrem — momentum slábne"
                trend_col  = C["green"] if trend_up else C["red"]
                st.markdown(f"""
                    <div style="padding:10px 14px;background:{C['card']};border-radius:8px;border-left:3px solid {trend_col};font-size:.83rem;color:{trend_col};margin-top:8px;">
                    {"▲" if trend_up else "▼"} {trend_text}
                    </div>
                """, unsafe_allow_html=True)

    # ── TAB 9: Institutional + Options ─────────────────
    with tab9:
        st.caption("Reálná doplňková data: institucionální vlastnictví, short interest a snapshot opcí.")

        i1, i2, i3, i4 = st.columns(4)
        with i1:
            inst = info.get("heldPercentInstitutions", None)
            st.metric("Instituce drží", f"{inst*100:.1f}%" if isinstance(inst, (int, float)) else "N/A")
        with i2:
            insiders_h = info.get("heldPercentInsiders", None)
            st.metric("Insideři drží", f"{insiders_h*100:.1f}%" if isinstance(insiders_h, (int, float)) else "N/A")
        with i3:
            short_ratio = info.get("shortRatio", None)
            st.metric("Short ratio", f"{short_ratio:.2f}" if isinstance(short_ratio, (int, float)) else "N/A")
        with i4:
            short_pct = info.get("shortPercentOfFloat", None)
            st.metric("Short % float", f"{short_pct*100:.1f}%" if isinstance(short_pct, (int, float)) else "N/A")

        st.markdown("---")
        opt = fetch_options_snapshot(ticker)
        if not opt:
            st.info("Opční data nejsou pro tento ticker dostupná.")
        else:
            op1, op2, op3, op4, op5 = st.columns(5)
            with op1: st.metric("Expirace", opt["expiry"])
            with op2: st.metric("Spot", f"${opt['spot']:.2f}")
            with op3: st.metric("Put/Call OI", f"{opt['pcr_oi']:.2f}" if pd.notna(opt["pcr_oi"]) else "N/A")
            with op4: st.metric("Put/Call Vol", f"{opt['pcr_vol']:.2f}" if pd.notna(opt["pcr_vol"]) else "N/A")
            with op5: st.metric("Max pain", f"${opt['max_pain']:.2f}" if opt.get("max_pain") else "N/A")

            c_oi = opt.get("calls_top_oi", pd.DataFrame()).copy()
            p_oi = opt.get("puts_top_oi", pd.DataFrame()).copy()
            oc1, oc2 = st.columns(2)
            with oc1:
                st.markdown("**Top call strikes (OI)**")
                st.dataframe(c_oi, use_container_width=True, hide_index=True)
            with oc2:
                st.markdown("**Top put strikes (OI)**")
                st.dataframe(p_oi, use_container_width=True, hide_index=True)

        st.markdown("---")
        if not risk_pack:
            st.info("Risk engine nemá dostatek dat.")
        else:
            rc1, rc2, rc3, rc4 = st.columns(4)
            with rc1: st.metric("Roční volatilita", f"{risk_pack['vol_annual']*100:.1f}%")
            with rc2: st.metric("1D VaR 95%", f"{risk_pack['var_95_1d']*100:.2f}%")
            with rc3: st.metric("Max Drawdown", f"{risk_pack['max_drawdown']*100:.1f}%")
            with rc4: st.metric("Risk Score", f"{risk_pack['risk_score']:.0f}/100")
            if risk_pack.get("beta") is not None:
                st.caption(f"Beta vs trh: {risk_pack['beta']:.2f}")
        with st.expander("🧾 Investment memo (volitelné)", expanded=False):
            memo = generate_investment_memo(ticker, info, dcf if 'dcf' in locals() else {}, risk_pack, score_data)
            st.write(f"**Teze:** {memo['thesis']}")
            st.write("**Klíčová rizika:**")
            for r in memo.get("key_risks", []):
                st.write(f"- {r}")
            st.download_button(
                "⬇️ Stáhnout Investment Memo (JSON)",
                data=json.dumps(memo, indent=2, ensure_ascii=False),
                file_name=f"{ticker}_investment_memo_v{APP_VERSION}.json",
                mime="application/json",
                use_container_width=True,
            )

def page_portfolio():
    st.markdown("<h2 class='grad' style='margin:0 0 1rem;'>💼 Portfolio</h2>", unsafe_allow_html=True)
    data = load_data()
    portfolio = data.get("portfolio", {})

    # Add position
    with st.expander("➕ Přidat / upravit pozici", expanded=len(portfolio)==0):
        pc1,pc2,pc3,pc4 = st.columns(4)
        with pc1: p_ticker = normalized_ticker_input("Ticker", key="portfolio_ticker", default=st.session_state.get("ticker", "AAPL"), placeholder="AAPL")
        with pc2: p_shares = st.number_input("Počet akcií", min_value=0.001, value=10.0, step=1.0)
        with pc3: p_cost   = st.number_input("Průměrná cena ($)", min_value=0.01, value=100.0, step=0.01)
        with pc4: p_sector = st.selectbox("Sektor", ["Technology","Healthcare","Finance","Energy","Consumer","Industrial","Real Estate","Other"])
        if st.button("💾 Uložit pozici", use_container_width=True):
            if p_ticker:
                portfolio[p_ticker] = {"shares": p_shares, "avg_cost": p_cost, "sector": p_sector}
                data["portfolio"] = portfolio
                save_data(data)
                st.success(f"✅ {p_ticker} uložen")
                st.rerun()

    if not portfolio:
        st.info("Portfolio je prázdné. Přidej první pozici výše.")
        return

    # Fetch live prices
    total_val = total_cost = 0.0
    live = {}
    with st.spinner("Načítám živé ceny…"):
        for sym, pos in portfolio.items():
            try:
                h = yf.Ticker(sym).history(period="5d")
                if not h.empty:
                    cur  = h["Close"].iloc[-1]
                    prev = h["Close"].iloc[-2] if len(h)>1 else cur
                    mv   = pos["shares"] * cur
                    cb   = pos["shares"] * pos["avg_cost"]
                    live[sym] = {**pos, "price": cur, "day_chg": (cur-prev)/prev*100,
                                 "mv": mv, "cb": cb, "pl": mv-cb, "pl_pct": (cur-pos["avg_cost"])/pos["avg_cost"]*100}
                    total_val  += mv
                    total_cost += cb
            except Exception:
                continue

    total_pl     = total_val - total_cost
    total_pl_pct = (total_val/total_cost-1)*100 if total_cost else 0

    # Summary cards
    pl_col = C["green"] if total_pl>=0 else C["red"]
    sc1,sc2,sc3,sc4 = st.columns(4)
    for col_obj, label, val, extra in [
        (sc1, "Celková hodnota",  f"${total_val:,.0f}",  ""),
        (sc2, "Investováno",      f"${total_cost:,.0f}", ""),
        (sc3, "Nerealizovaný P&L",f"${total_pl:+,.0f}",  pl_col),
        (sc4, "Celkový výnos",    f"{total_pl_pct:+.2f}%", pl_col),
    ]:
        with col_obj:
            color_val = extra if extra else C["t1"]
            st.markdown(f"""
                <div class="fa-card" style="text-align:center;">
                    <div style="font-size:.72rem;color:{C['t2']};text-transform:uppercase;letter-spacing:.05em;">{label}</div>
                    <div class="mono" style="font-size:1.6rem;font-weight:800;color:{color_val};margin:6px 0;">{val}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Charts
    ch1, ch2 = st.columns([1.3,1])
    with ch1:
        pie_fig = go.Figure(go.Pie(
            labels=list(live.keys()),
            values=[p["mv"] for p in live.values()],
            hole=0.55,
            textinfo="label+percent",
            textfont=dict(color=C["t1"],size=12),
            marker=dict(colors=["#00b4d8","#00e676","#7c3aed","#f59e0b","#ff3d5a","#34d399","#f472b6","#60a5fa"],
                        line=dict(color=C["bg"],width=2))
        ))
        pie_fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False, margin=dict(l=0,r=0,t=20,b=0),
            annotations=[dict(text=f"${total_val/1000:.1f}K",x=0.5,y=0.5,
                font=dict(size=18,color=C["t1"],family="JetBrains Mono"),showarrow=False)])
        st.plotly_chart(pie_fig, use_container_width=True, config={"displayModeBar":False})

    with ch2:
        syms  = list(live.keys())
        pcts  = [live[s]["pl_pct"] for s in syms]
        bcols = [C["green"] if p>=0 else C["red"] for p in pcts]
        bar_fig = go.Figure(go.Bar(x=syms, y=pcts, marker_color=bcols, marker_opacity=0.85,
            text=[f"{p:+.1f}%" for p in pcts], textposition="outside",
            textfont=dict(color=C["t1"],size=11)))
        bar_fig.add_hline(y=0, line_color=C["border"])
        bar_fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, tickfont=dict(color=C["t2"])),
            yaxis=dict(showgrid=True, gridcolor=C["grid"], ticksuffix="%", tickfont=dict(color=C["t2"])),
            margin=dict(l=10,r=10,t=20,b=10), showlegend=False)
        st.plotly_chart(bar_fig, use_container_width=True, config={"displayModeBar":False})

    # Benchmark vs S&P 500
    st.markdown("---")
    st.markdown(f"<h3 style='color:{C['t1']};margin-bottom:.8rem;'>📊 Benchmark vs S&P 500</h3>", unsafe_allow_html=True)
    try:
        spy = yf.Ticker("^GSPC").history(period="1y")["Close"]
        spy_ret = (spy / spy.iloc[0] - 1) * 100

        # Portfolio weighted return (approximate using equal-weight for simplicity)
        port_returns = []
        for sym in live:
            h = yf.Ticker(sym).history(period="1y")["Close"]
            if not h.empty:
                port_returns.append((h / h.iloc[0] - 1) * 100)

        if port_returns:
            port_ret = pd.concat(port_returns, axis=1).mean(axis=1)
            bfig = go.Figure()
            bfig.add_trace(go.Scatter(x=port_ret.index, y=port_ret.values, name="Portfolio",
                line=dict(color=C["blue"],width=2)))
            bfig.add_trace(go.Scatter(x=spy_ret.index, y=spy_ret.values, name="S&P 500",
                line=dict(color=C["t3"],width=1.5,dash="dash")))
            bfig.update_layout(**CHART_LAYOUT, height=260,
                legend=dict(orientation="h",y=1.02,bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(bfig, use_container_width=True, config={"displayModeBar":False})
    except Exception:
        st.info("Benchmark srovnání není dostupné.")

    # Positions table
    st.markdown("---")
    st.markdown(f"<h3 style='color:{C['t1']};margin-bottom:.8rem;'>📋 Pozice</h3>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="background:{C['card']};border:1px solid {C['border']};border-radius:12px;overflow:hidden;">
        <div style="display:flex;padding:8px 14px;background:{C['bg2']};font-size:.72rem;color:{C['t3']};text-transform:uppercase;font-weight:600;letter-spacing:.05em;gap:8px;">
            <span style="flex:1.2">Symbol</span><span style="flex:1;text-align:right;">Akcie</span>
            <span style="flex:1;text-align:right;">Prům. cena</span><span style="flex:1;text-align:right;">Aktuální</span>
            <span style="flex:1;text-align:right;">Denn. změna</span><span style="flex:1.2;text-align:right;">Tržní hodnota</span>
            <span style="flex:1.2;text-align:right;">P&L</span><span style="flex:1;text-align:right;">Výnos</span>
        </div>
    """, unsafe_allow_html=True)

    for sym, p in live.items():
        pl_c   = C["green"] if p["pl"]>=0 else C["red"]
        day_c  = C["green"] if p["day_chg"]>=0 else C["red"]
        st.markdown(f"""
            <div style="display:flex;padding:9px 14px;border-bottom:1px solid {C['border']};gap:8px;align-items:center;font-family:'JetBrains Mono',monospace;font-size:.82rem;">
                <span style="flex:1.2;font-weight:700;color:{C['blue']};">{sym}</span>
                <span style="flex:1;text-align:right;color:{C['t1']};">{p['shares']:.2f}</span>
                <span style="flex:1;text-align:right;color:{C['t2']};">${p['avg_cost']:.2f}</span>
                <span style="flex:1;text-align:right;color:{C['t1']};">${p['price']:.2f}</span>
                <span style="flex:1;text-align:right;color:{day_c};">{p['day_chg']:+.2f}%</span>
                <span style="flex:1.2;text-align:right;color:{C['t1']};">${p['mv']:,.0f}</span>
                <span style="flex:1.2;text-align:right;color:{pl_c};">${p['pl']:+,.0f}</span>
                <span style="flex:1;text-align:right;color:{pl_c};font-weight:700;">{p['pl_pct']:+.1f}%</span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Buy Score for each position
    st.markdown("---")
    st.markdown(f"<h3 style='color:{C['t1']};margin-bottom:.8rem;'>🎯 Buy Score pozic — co dělat?</h3>", unsafe_allow_html=True)
    score_cols = st.columns(min(len(live), 4))
    for idx, sym in enumerate(live):
        with score_cols[idx % 4]:
            with st.spinner(f"Počítám {sym}…"):
                df_s, info_s = fetch_stock(sym, period="1y")
                if df_s is not None and not df_s.empty:
                    df_s = calc_indicators(df_s)
                    an_s = fetch_analyst_info(sym)
                    ins_s = fetch_insider_sec(sym)
                    sc_s = compute_buy_score(df_s, info_s, an_s, ins_s)
                    if sc_s["score"]:
                        col_s = sc_s["color"]
                        st.markdown(f"""
                            <div class="fa-card" style="text-align:center;border-color:{col_s}40;">
                                <div style="font-weight:700;color:{C['blue']};font-size:1rem;">{sym}</div>
                                <div style="font-size:2.2rem;font-weight:800;color:{col_s};font-family:'JetBrains Mono',monospace;">{sc_s['score']:.0f}</div>
                                <div style="font-size:.8rem;font-weight:700;color:{col_s};">{sc_s['label']}</div>
                                <div style="font-size:.72rem;color:{C['t3']};margin-top:4px;">P&L: <span style="color:{'#00e676' if live[sym]['pl']>=0 else '#ff3d5a'};">{live[sym]['pl_pct']:+.1f}%</span></div>
                            </div>
                        """, unsafe_allow_html=True)

    # Export CSV
    st.markdown("---")
    rows = []
    for sym, p in live.items():
        rows.append({"Symbol":sym,"Akcie":p["shares"],"Prům. cena":p["avg_cost"],
                     "Aktuální cena":p["price"],"Tržní hodnota":p["mv"],"P&L":p["pl"],"Výnos %":p["pl_pct"]})
    csv = pd.DataFrame(rows).to_csv(index=False).encode("utf-8")
    st.download_button("📤 Export portfolia do CSV", csv, f"portfolio_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")

    # Delete positions
    st.markdown(f"<div style='font-size:.8rem;color:{C['t3']};margin-top:.5rem;'>Smazat pozici:</div>", unsafe_allow_html=True)
    del_cols = st.columns(min(len(live), 6))
    for idx, sym in enumerate(list(live.keys())):
        with del_cols[idx % 6]:
            if st.button(f"🗑️ {sym}", key=f"del_{sym}", use_container_width=True):
                del data["portfolio"][sym]
                save_data(data)
                st.rerun()

    # ── Correlation Matrix ────────────────
    if len(live) >= 2:
        st.markdown("---")
        st.markdown(f"<h3 style='color:{C['t1']};margin-bottom:.4rem;'>🔗 Korelační matice — diverzifikace portfolia</h3>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:.8rem;color:{C['t3']};margin-bottom:.8rem;'>Hodnota blízká 1.0 = akcie se pohybují společně (nízká diverzifikace). Blízká 0 nebo záporná = dobré pro diverzifikaci.</div>", unsafe_allow_html=True)
        with st.spinner("Počítám korelace…"):
            corr_df = compute_correlation(tuple(live.keys()))
        if not corr_df.empty:
            ticks = list(corr_df.columns)
            z = corr_df.values
            text_vals = [[f"{v:.2f}" for v in row] for row in z]
            corr_fig = go.Figure(go.Heatmap(
                z=z, x=ticks, y=ticks,
                text=text_vals, texttemplate="%{text}",
                colorscale=[
                    [0.0, with_alpha(C["red"], 0.8)],
                    [0.5, C["card"]],
                    [1.0, with_alpha(C["green"], 0.8)],
                ],
                zmin=-1, zmax=1,
                showscale=True,
                colorbar=dict(
                    tickfont=dict(color=C["t2"]),
                    tickvals=[-1,-0.5,0,0.5,1],
                    title=dict(text="Korelace", font=dict(color=C["t2"])),
                ),
            ))
            corr_fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=max(300, len(ticks)*60),
                margin=dict(l=10,r=10,t=10,b=10),
                font=dict(color=C["t1"]),
                xaxis=dict(tickfont=dict(color=C["t2"])),
                yaxis=dict(tickfont=dict(color=C["t2"])),
            )
            st.plotly_chart(corr_fig, use_container_width=True, config={"displayModeBar":False})

            # Diversification score
            upper = corr_df.where(np.triu(np.ones(corr_df.shape), k=1).astype(bool))
            avg_corr = upper.stack().mean()
            div_score = max(0, min(100, (1 - avg_corr) * 100))
            div_col = C["green"] if div_score >= 60 else C["orange"] if div_score >= 40 else C["red"]
            st.markdown(f"""
                <div class="fa-card" style="display:flex;align-items:center;gap:16px;border-color:{div_col}40;">
                    <div>
                        <div style="font-size:.72rem;color:{C['t2']};text-transform:uppercase;">Skóre diverzifikace</div>
                        <div class="mono" style="font-size:2rem;font-weight:800;color:{div_col};">{div_score:.0f}/100</div>
                    </div>
                    <div style="font-size:.83rem;color:{C['t2']};">
                        {'✅ Dobře diverzifikované portfolio. Nízká průměrná korelace snižuje volatilitu.' if div_score>=60 else
                         '⚠️ Střední korelace — zvažte přidání nekorelujících aktiv (jiné sektory, dluhopisy, komodity).' if div_score>=40 else
                         '❌ Vysoká korelace — portfolio je koncentrované. Pokles jedné akcie táhne celé portfolio dolů.'}
                    </div>
                </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGE: CHARTS (Advanced Charting Studio)
# ─────────────────────────────────────────────
def page_charts():
    st.markdown("<h2 class='grad' style='margin:0 0 1rem;'>📉 Charting Studio</h2>", unsafe_allow_html=True)
    ticker = st.session_state.get("ticker","AAPL")

    cc1,cc2,cc3 = st.columns([2,1,1])
    with cc1: chart_ticker = normalized_ticker_input("Symbol", key="charts_symbol", default=ticker, placeholder="AAPL", label_visibility="collapsed")
    with cc2: chart_type   = st.selectbox("Typ grafu", ["Candlestick","Line","Area","OHLC"], label_visibility="collapsed")
    with cc3: period_sel   = st.selectbox("Období", ["1mo","3mo","6mo","1y","2y","5y","max"], index=3, label_visibility="collapsed")

    with st.expander("📐 Indikátory", expanded=True):
        ic1,ic2,ic3,ic4,ic5 = st.columns(5)
        with ic1:
            show_sma20  = st.checkbox("SMA 20",  value=True)
            show_sma50  = st.checkbox("SMA 50",  value=True)
            show_sma200 = st.checkbox("SMA 200", value=False)
        with ic2:
            show_bb      = st.checkbox("Bollinger Bands", value=True)
            show_vwap    = st.checkbox("VWAP (20d)", value=False)
            bb_std       = st.slider("BB Std", 1.0, 3.0, 2.0, 0.5)
        with ic3:
            show_rsi      = st.checkbox("RSI (14)",   value=True)
            show_stochrsi = st.checkbox("Stoch RSI",  value=False)
            show_macd     = st.checkbox("MACD",       value=True)
        with ic4:
            show_vol      = st.checkbox("Volume",     value=True)
            show_obv      = st.checkbox("OBV",        value=False)
            show_atr      = st.checkbox("ATR (14)",   value=False)
        with ic5:
            compare_sp    = st.checkbox("vs S&P 500", value=False)
            show_williams = st.checkbox("Williams %R", value=False)
            show_ichimoku = st.checkbox("Ichimoku",   value=False)

    df, info = fetch_stock(chart_ticker, period=period_sel)
    if df is None or df.empty:
        st.error(f"Nenalezena data pro {chart_ticker}")
        return
    df = calc_indicators(df)
    # Custom BB with user std
    df["BB_Upper_c"] = df["BB_Mid"] + bb_std * df["BB_Std"]
    df["BB_Lower_c"] = df["BB_Mid"] - bb_std * df["BB_Std"]

    rows  = 1 + (1 if show_rsi else 0) + (1 if show_macd else 0)
    hghts = [0.55] + [0.22 if show_rsi else None, 0.23 if show_macd else None]
    hghts = [h for h in hghts if h]
    fig   = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                          row_heights=hghts, vertical_spacing=0.02)
    rsi_row  = 2 if show_rsi else None
    macd_row = (2 if not show_rsi else 3) if show_macd else None

    # Main chart
    if chart_type == "Candlestick":
        fig.add_trace(go.Candlestick(
            x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
            name=chart_ticker,
            increasing=dict(line=dict(color=C["green"]), fillcolor=C["green"]),
            decreasing=dict(line=dict(color=C["red"]), fillcolor=C["red"]),
        ), row=1, col=1)
    elif chart_type == "Line":
        fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name=chart_ticker,
            line=dict(color=C["blue"],width=2.5)), row=1, col=1)
    elif chart_type == "Area":
        fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name=chart_ticker,
            line=dict(color=C["blue"],width=2.5),
            fill="tozeroy", fillcolor=with_alpha(C["blue"], 0.13)), row=1, col=1)
    elif chart_type == "OHLC":
        fig.add_trace(go.Ohlc(x=df.index, open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"], name=chart_ticker,
            increasing_line_color=C["green"], decreasing_line_color=C["red"]), row=1, col=1)

    # Overlays
    if show_sma20:
        fig.add_trace(go.Scatter(x=df.index,y=df["SMA20"],name="SMA20",
            line=dict(color="#f59e0b",width=1.2,dash="dot"),opacity=.85),row=1,col=1)
    if show_sma50:
        fig.add_trace(go.Scatter(x=df.index,y=df["SMA50"],name="SMA50",
            line=dict(color=C["blue"],width=1.2,dash="dot"),opacity=.85),row=1,col=1)
    if show_sma200:
        fig.add_trace(go.Scatter(x=df.index,y=df["SMA200"],name="SMA200",
            line=dict(color=C["purple"],width=1.2,dash="dash"),opacity=.85),row=1,col=1)
    if show_bb:
        fig.add_trace(go.Scatter(x=df.index,y=df["BB_Upper_c"],name="BB Upper",
            line=dict(color=C["purple"],width=1,dash="dash"),opacity=.6),row=1,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=df["BB_Lower_c"],name="BB Lower",
            line=dict(color=C["purple"],width=1,dash="dash"),opacity=.6,
            fill="tonexty",fillcolor=with_alpha(C["purple"], 0.07)),row=1,col=1)
    if show_vwap and "VWAP" in df.columns:
        fig.add_trace(go.Scatter(x=df.index,y=df["VWAP"],name="VWAP(20d)",
            line=dict(color="#f472b6",width=1.5,dash="dashdot"),opacity=.85),row=1,col=1)
    if show_ichimoku and "Ichimoku_Tenkan" in df.columns:
        fig.add_trace(go.Scatter(x=df.index,y=df["Ichimoku_Tenkan"],name="Tenkan(9)",
            line=dict(color="#34d399",width=1.2),opacity=.8),row=1,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=df["Ichimoku_Kijun"],name="Kijun(26)",
            line=dict(color="#fb923c",width=1.2),opacity=.8),row=1,col=1)
    if show_vol:
        vcols = [C["green"] if df["Close"].iloc[i]>=df["Open"].iloc[i] else C["red"] for i in range(len(df))]
        fig.add_trace(go.Bar(x=df.index,y=df["Volume"],name="Volume",
            marker_color=vcols,marker_opacity=0.35,yaxis="y2"),row=1,col=1)
    if compare_sp:
        spy_h = yf.Ticker("^GSPC").history(period=period_sel)["Close"]
        spy_norm = spy_h / spy_h.iloc[0] * df["Close"].iloc[0]
        fig.add_trace(go.Scatter(x=spy_norm.index,y=spy_norm.values,name="S&P 500 (scaled)",
            line=dict(color=C["t3"],width=1.5,dash="dash"),opacity=.7),row=1,col=1)
    if show_rsi:
        fig.add_trace(go.Scatter(x=df.index,y=df["RSI"],name="RSI",
            line=dict(color=C["purple"],width=1.8)),row=rsi_row,col=1)
        fig.add_hline(y=70,line_dash="dash",line_color=C["red"],opacity=.4,row=rsi_row,col=1)
        fig.add_hline(y=30,line_dash="dash",line_color=C["green"],opacity=.4,row=rsi_row,col=1)
        if show_stochrsi and "StochRSI_K" in df.columns:
            fig.add_trace(go.Scatter(x=df.index,y=df["StochRSI_K"],name="StochRSI K",
                line=dict(color=C["orange"],width=1.2,dash="dot"),opacity=.8),row=rsi_row,col=1)
            fig.add_trace(go.Scatter(x=df.index,y=df["StochRSI_D"],name="StochRSI D",
                line=dict(color=C["red"],width=1.2,dash="dot"),opacity=.8),row=rsi_row,col=1)
    if show_macd:
        hist_c = [C["green"] if v>=0 else C["red"] for v in df["MACD_Hist"].fillna(0)]
        fig.add_trace(go.Bar(x=df.index,y=df["MACD_Hist"],name="MACD Hist",
            marker_color=hist_c,marker_opacity=0.6),row=macd_row,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=df["MACD"],name="MACD",
            line=dict(color=C["blue"],width=1.5)),row=macd_row,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=df["MACD_Signal"],name="Signal",
            line=dict(color=C["orange"],width=1.5)),row=macd_row,col=1)

    fig.update_layout(**CHART_LAYOUT, height=700, showlegend=True,
        yaxis2=dict(showgrid=False,overlaying="y",side="right",showticklabels=False,
                    range=[0,df["Volume"].max()*4] if show_vol else [0,1]),
        legend=dict(orientation="h",y=1.02,bgcolor="rgba(0,0,0,0)"))
    fig.update_xaxes(rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":True,
        "modeBarButtonsToRemove":["lasso2d","select2d"]})

    # Signal summary
    sig_cols = []
    if show_rsi and not df["RSI"].isna().all():
        rsi_v = df["RSI"].iloc[-1]
        sig_cols.append(("RSI (14)", f"{rsi_v:.1f}", "Překoupený" if rsi_v>70 else "Přeprodaný" if rsi_v<30 else "Neutrální"))
    if show_macd and not df["MACD"].isna().all():
        macd_v, sig_v = df["MACD"].iloc[-1], df["MACD_Signal"].iloc[-1]
        sig_cols.append(("MACD vs Signal", f"{macd_v:.3f}", "Bullish" if macd_v>sig_v else "Bearish"))
    if show_bb and not df["BB_Lower_c"].isna().all():
        bp = (df["Close"].iloc[-1]-df["BB_Lower_c"].iloc[-1])/(df["BB_Upper_c"].iloc[-1]-df["BB_Lower_c"].iloc[-1])*100
        sig_cols.append(("BB pozice", f"{bp:.0f}%", "Horní pásmo" if bp>75 else "Dolní pásmo" if bp<25 else "Střed"))
    if show_williams and "Williams_R" in df.columns and not df["Williams_R"].isna().all():
        wr = df["Williams_R"].iloc[-1]
        sig_cols.append(("Williams %R", f"{wr:.1f}", "Překoupený" if wr>-20 else "Přeprodaný" if wr<-80 else "Neutrální"))
    if show_obv and "OBV" in df.columns:
        obv_trend = "Rostoucí ▲" if df["OBV"].iloc[-1] > df["OBV"].iloc[-20] else "Klesající ▼"
        sig_cols.append(("OBV trend", obv_trend, None))
    if sig_cols:
        cols_s = st.columns(len(sig_cols))
        for i,(lbl,val,delta) in enumerate(sig_cols):
            with cols_s[i]:
                st.metric(lbl, val, delta)
    if show_atr and not df["ATR"].isna().all():
        st.metric("ATR (14)", f"${df['ATR'].iloc[-1]:.2f}", help="Average True Range — průměrná denní volatilita")

# ─────────────────────────────────────────────
#  PAGE: MULTI-ASSET
# ─────────────────────────────────────────────
def page_multi_asset():
    st.markdown("<h2 class='grad' style='margin:0 0 1rem;'>🌐 Multi-Asset Universe</h2>", unsafe_allow_html=True)
    tab_c, tab_f, tab_k, tab_fut = st.tabs(["🪙 Crypto","💱 Forex","🥇 Komodity","📊 Futures"])

    asset_groups = {
        "crypto":  (["BTC-USD","ETH-USD","SOL-USD","ADA-USD","AVAX-USD","DOT-USD","LINK-USD","LTC-USD","MATIC-USD","UNI-USD"], 5),
        "forex":   (["EURUSD=X","GBPUSD=X","USDJPY=X","USDCHF=X","AUDUSD=X","USDCAD=X","NZDUSD=X","EURGBP=X"], 4),
        "komodity":(["GC=F","SI=F","CL=F","NG=F","HG=F","ZW=F","ZC=F","ZS=F"], 4),
        "futures": (["ES=F","NQ=F","YM=F","RTY=F","GC=F","CL=F"], 3),
    }
    names = {
        "GC=F":"Gold","SI=F":"Silver","CL=F":"Crude Oil","NG=F":"Nat. Gas",
        "HG=F":"Copper","ZW=F":"Wheat","ZC=F":"Corn","ZS=F":"Soybeans",
        "ES=F":"S&P 500","NQ=F":"NASDAQ","YM=F":"Dow Jones","RTY=F":"Russell",
    }
    fmt = {
        "forex":   lambda p,s: f"{p:.4f}",
        "komodity":lambda p,s: f"${p:.2f}",
        "futures": lambda p,s: f"{p:,.2f}",
        "crypto":  lambda p,s: f"${p:,.2f}",
    }

    for tab_obj, group_key in [(tab_c,"crypto"),(tab_f,"forex"),(tab_k,"komodity"),(tab_fut,"futures")]:
        with tab_obj:
            tickers, n_cols = asset_groups[group_key]
            mdata = fetch_multi(tickers)
            cols  = st.columns(n_cols)
            for idx, t in enumerate(tickers):
                if t not in mdata:
                    continue
                info = mdata[t]
                chg  = info["change"]
                col  = C["green"] if chg>=0 else C["red"]
                icon = "▲" if chg>=0 else "▼"
                label = names.get(t, t.replace("-USD","").replace("=X","").replace("=F",""))
                price_str = fmt[group_key](info["price"], t)
                with cols[idx % n_cols]:
                    st.markdown(f"""
                        <div class="fa-card" style="text-align:center;border-color:{col}25;padding:14px 10px;">
                            <div style="font-weight:700;color:{C['blue']};font-size:.9rem;">{label}</div>
                            <div class="mono" style="font-size:1.4rem;font-weight:800;color:{C['t1']};margin:6px 0;">{price_str}</div>
                            <div style="font-size:.85rem;font-weight:700;color:{col};">{icon} {abs(chg):.2f}%</div>
                        </div>
                    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGE: INSIDER (SEC EDGAR)
# ─────────────────────────────────────────────
def page_insider():
    st.markdown("<h2 class='grad' style='margin:0 0 1rem;'>👤 Insider Trades — SEC EDGAR</h2>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:.83rem;color:{C['t3']};margin-bottom:1rem;'>Reálné Form-4 záznamy ze SEC EDGAR (data.sec.gov). Pouze US akcie kótované na NYSE/NASDAQ.</div>", unsafe_allow_html=True)

    ticker = normalized_ticker_input("Ticker", key="insider_ticker", default=st.session_state.get("ticker","AAPL"), placeholder="AAPL")
    if st.button("🔍 Načíst insider data", use_container_width=True):
        st.session_state["ticker"] = ticker
        with st.spinner("Přistupuji k SEC EDGAR…"):
            trades = fetch_insider_sec(ticker)
        if not trades:
            st.warning("Žádné Form-4 záznamy za posledních 6 měsíců, nebo ticker nebyl nalezen v SEC databázi.")
        else:
            st.success(f"Nalezeno {len(trades)} Form-4 podání pro {ticker}")
            st.markdown(f"""
                <div style="background:{C['card']};border:1px solid {C['border']};border-radius:12px;overflow:hidden;margin-top:12px;">
                <div style="display:flex;padding:8px 14px;background:{C['bg2']};font-size:.72rem;color:{C['t3']};text-transform:uppercase;font-weight:600;letter-spacing:.05em;gap:10px;">
                    <span style="flex:1;">Datum podání</span><span style="flex:.5;">Formulář</span><span style="flex:2;">Odkaz na SEC</span>
                </div>
            """, unsafe_allow_html=True)
            for tr in trades[:20]:
                cik_c   = tr["cik"]
                sec_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik_c}&type=4&dateb=&owner=include&count=40"
                st.markdown(f"""
                    <div style="display:flex;padding:9px 14px;border-bottom:1px solid {C['border']};align-items:center;gap:10px;">
                        <span class="mono" style="flex:1;font-size:.82rem;color:{C['t1']};">{tr['date']}</span>
                        <span style="flex:.5;font-size:.82rem;color:{C['blue']};">Form 4</span>
                        <a href="{sec_url}" target="_blank" style="flex:2;font-size:.78rem;color:{C['t3']};text-decoration:none;">Zobrazit na SEC EDGAR →</a>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # Watchlist batch check
    st.markdown("---")
    st.markdown(f"<h3 style='color:{C['t1']};margin-bottom:.8rem;'>📋 Insider aktivita pro celý watchlist</h3>", unsafe_allow_html=True)
    data = load_data()
    wl   = data.get("watchlist", [])
    if st.button("🔄 Načíst pro watchlist", use_container_width=True):
        results = {}
        prog = st.progress(0)
        for i, t in enumerate(wl):
            trades = fetch_insider_sec(t)
            results[t] = len(trades)
            prog.progress((i+1)/len(wl))
        prog.empty()
        cols = st.columns(4)
        for idx, (t, cnt) in enumerate(sorted(results.items(), key=lambda x: x[1], reverse=True)):
            col = C["green"] if cnt >= 5 else C["orange"] if cnt >= 1 else C["t3"]
            with cols[idx % 4]:
                st.markdown(f"""
                    <div class="fa-card" style="text-align:center;border-color:{col}30;">
                        <div style="font-weight:700;color:{C['blue']};">{t}</div>
                        <div class="mono" style="font-size:1.4rem;font-weight:800;color:{col};margin:6px 0;">{cnt}</div>
                        <div style="font-size:.75rem;color:{C['t3']};">Form-4 za 6M</div>
                    </div>
                """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGE: EARNINGS
# ─────────────────────────────────────────────
def page_earnings():
    st.markdown("<h2 class='grad' style='margin:0 0 1rem;'>📅 Earnings Kalendář</h2>", unsafe_allow_html=True)
    ticker = normalized_ticker_input("Ticker", key="earnings_ticker", default=st.session_state.get("ticker","AAPL"))
    def _to_naive_utc_datetime(s):
        # Handles tz-aware and tz-naive values uniformly (always returns tz-naive UTC).
        dt = pd.to_datetime(s, errors="coerce", utc=True)
        if isinstance(dt, pd.DatetimeIndex):
            return dt.tz_convert(None)
        return dt.dt.tz_convert(None)

    def _normalize_earnings_df(df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame(columns=["Date", "EPS Estimate", "EPS Actual", "Surprise (%)"])
        w = df.copy()
        if isinstance(w.index, pd.DatetimeIndex):
            w["Date"] = _to_naive_utc_datetime(w.index)
        elif "Earnings Date" in w.columns:
            w["Date"] = _to_naive_utc_datetime(w["Earnings Date"])
        else:
            w["Date"] = _to_naive_utc_datetime(w.iloc[:, 0])
        col_map = {str(c).strip().lower().replace(" ", ""): c for c in w.columns}
        est_col = next((col_map[k] for k in ["epsestimate", "estimate"] if k in col_map), None)
        act_col = next((col_map[k] for k in ["reportedeps", "epsactual", "actual"] if k in col_map), None)
        sur_col = next((col_map[k] for k in ["surprise(%)", "surprisepercent", "surprise"] if k in col_map), None)
        out = pd.DataFrame()
        out["Date"] = w["Date"]
        out["EPS Estimate"] = pd.to_numeric(w[est_col], errors="coerce") if est_col else np.nan
        out["EPS Actual"] = pd.to_numeric(w[act_col], errors="coerce") if act_col else np.nan
        out["Surprise (%)"] = pd.to_numeric(w[sur_col], errors="coerce") if sur_col else np.nan
        out = out.dropna(subset=["Date"]).sort_values("Date", ascending=False)
        return out

    def _fetch_earnings_payload(t: str):
        payload = {"next_date": None, "earnings_hist": pd.DataFrame(columns=["Date", "EPS Estimate", "EPS Actual", "Surprise (%)"])}
        s_obj = yf.Ticker(t)
        try:
            edf = s_obj.get_earnings_dates(limit=24)
            payload["earnings_hist"] = _normalize_earnings_df(edf)
        except Exception as e:
            log_debug(f"get_earnings_dates failed for {t}: {e}")
            try:
                payload["earnings_hist"] = _normalize_earnings_df(getattr(s_obj, "earnings_dates", None))
            except Exception as e2:
                log_debug(f"earnings_dates fallback failed for {t}: {e2}")
                payload["earnings_hist"] = pd.DataFrame(columns=["Date", "EPS Estimate", "EPS Actual", "Surprise (%)"])

        if payload["earnings_hist"].empty:
            try:
                eh = getattr(s_obj, "earnings_history", None)
                payload["earnings_hist"] = _normalize_earnings_df(eh)
            except Exception as e3:
                log_debug(f"earnings_history fallback failed for {t}: {e3}")
                pass

        now_utc = pd.Timestamp.now(tz="UTC").tz_convert(None)
        future = payload["earnings_hist"][payload["earnings_hist"]["Date"] >= now_utc].copy()
        if not future.empty:
            payload["next_date"] = future.sort_values("Date", ascending=True)["Date"].iloc[0]
        else:
            try:
                cal = s_obj.calendar
                if isinstance(cal, dict):
                    ed_val = cal.get("Earnings Date")
                    if ed_val:
                        payload["next_date"] = pd.Timestamp(ed_val[0] if isinstance(ed_val, list) else ed_val)
                elif cal is not None and hasattr(cal, "empty") and not cal.empty and "Earnings Date" in cal.index:
                    payload["next_date"] = pd.Timestamp(cal.loc["Earnings Date"].iloc[0])
            except Exception:
                payload["next_date"] = None
        return payload

    load_click = st.button("📅 Načíst earnings data", use_container_width=True)
    state_key = f"earnings_payload_{ticker}"
    if load_click:
        st.session_state["ticker"] = ticker
        with st.spinner("Načítám earnings data..."):
            st.session_state[state_key] = _fetch_earnings_payload(ticker)
            st.session_state[f"earnings_info_{ticker}"] = fetch_stock(ticker, period="5y")[1]
    if state_key not in st.session_state:
        st.info("Klikni na „Načíst earnings data“ pro přesnou historii reportů EPS a datumy výsledků.")
        return

    payload = st.session_state.get(state_key, {})
    earnings_hist = payload.get("earnings_hist", pd.DataFrame())
    next_date = payload.get("next_date")
    info = st.session_state.get(f"earnings_info_{ticker}", {})

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='fa-card'>", unsafe_allow_html=True)
        st.subheader("📅 Příští earnings")
        if next_date is not None and pd.notna(next_date):
            try:
                ed = pd.Timestamp(next_date)
                if getattr(ed, "tzinfo", None) is not None:
                    ed = ed.tz_convert(None)
                days_left = (ed.normalize() - pd.Timestamp.now(tz="UTC").tz_convert(None).normalize()).days
                st.markdown(f"""
                    <div style='text-align:center;'>
                        <div class='mono' style='font-size:2rem;font-weight:800;color:{C['blue']};'>{ed.strftime('%d.%m.%Y')}</div>
                        <div style='color:{C['t2']};margin-top:6px;'>{ed.strftime('%A')} • za {days_left} dní</div>
                    </div>
                """, unsafe_allow_html=True)
            except Exception:
                st.write(str(next_date))
        else:
            st.info("Datum příštích earnings není k dispozici.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<div class='fa-card'>", unsafe_allow_html=True)
        st.subheader("🎯 Analyst Estimates")
        an = fetch_analyst_info(ticker)
        if an:
            e1,e2 = st.columns(2)
            with e1:
                st.metric("Avg. target", f"${an.get('target_mean',0):.2f}" if an.get('target_mean') else "–")
                st.metric("Rating", an.get("recommendation","–").replace("_"," ").title())
            with e2:
                st.metric("High target", f"${an.get('target_high',0):.2f}" if an.get('target_high') else "–")
                st.metric("Low target",  f"${an.get('target_low',0):.2f}"  if an.get('target_low')  else "–")
        st.markdown("</div>", unsafe_allow_html=True)

    if earnings_hist is not None and not earnings_hist.empty:
        hist = earnings_hist[earnings_hist["Date"] < pd.Timestamp.now(tz="UTC").tz_convert(None)].copy()
        hist = hist.sort_values("Date", ascending=True).tail(8)
        hist["Label"] = hist["Date"].dt.strftime("%b %Y")
        st.markdown("---")
        st.subheader("📈 Historie EPS — skutečný vs. odhadovaný")
        fig_e = go.Figure()
        fig_e.add_trace(go.Bar(
            x=hist["Label"], y=hist["EPS Estimate"],
            name="Odhad", marker_color=C["t3"], marker_opacity=0.6
        ))
        colors_e = [C["green"] if (a if pd.notna(a) else -np.inf) >= (e if pd.notna(e) else -np.inf) else C["red"]
                    for a, e in zip(hist["EPS Actual"], hist["EPS Estimate"])]
        fig_e.add_trace(go.Bar(
            x=hist["Label"], y=hist["EPS Actual"],
            name="Skutečný", marker_color=colors_e, marker_opacity=0.85
        ))
        fig_e.update_layout(**CHART_LAYOUT, height=340, barmode="group",
            legend=dict(orientation="h", bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig_e, use_container_width=True, config={"displayModeBar":False})

        tbl = hist.sort_values("Date", ascending=False).copy()
        tbl["Date"] = tbl["Date"].dt.strftime("%Y-%m-%d")
        tbl["Day"] = pd.to_datetime(tbl["Date"], errors="coerce").dt.strftime("%a")
        tbl["EPS Estimate"] = tbl["EPS Estimate"].map(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
        tbl["EPS Actual"] = tbl["EPS Actual"].map(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
        tbl["Surprise (%)"] = tbl["Surprise (%)"].map(lambda x: f"{x:+.2f}%" if pd.notna(x) else "N/A")
        st.dataframe(tbl[["Date", "Day", "EPS Estimate", "EPS Actual", "Surprise (%)"]], use_container_width=True, hide_index=True)
    else:
        st.warning("Historie earnings (EPS estimate vs actual) není pro tento ticker dostupná.")

    st.markdown("---")
    st.subheader("💰 Klíčová finanční data")
    if info:
        fc1,fc2,fc3,fc4 = st.columns(4)
        with fc1: st.metric("Revenue (TTM)", f"${info.get('totalRevenue',0)/1e9:.1f}B" if info.get('totalRevenue') else "–")
        with fc2: st.metric("Gross Profit",  f"${info.get('grossProfits',0)/1e9:.1f}B" if info.get('grossProfits') else "–")
        with fc3: st.metric("EBITDA",        f"${info.get('ebitda',0)/1e9:.1f}B" if info.get('ebitda') else "–")
        with fc4: st.metric("Free Cash Flow",f"${info.get('freeCashflow',0)/1e9:.1f}B" if info.get('freeCashflow') else "–")

# ─────────────────────────────────────────────
#  PAGE: ALERTY
# ─────────────────────────────────────────────
def page_alerts():
    st.markdown("<h2 class='grad' style='margin:0 0 1rem;'>🔔 Cenové & Score Alerty</h2>", unsafe_allow_html=True)
    data = load_data()
    alerts = data.get("alerts", [])

    # Add alert form
    with st.expander("➕ Přidat alert", expanded=True):
        ac1,ac2,ac3,ac4 = st.columns(4)
        with ac1:
            a_ticker = normalized_ticker_input("Ticker", key="alerts_ticker", default=st.session_state.get("alert_ticker", st.session_state.get("ticker","AAPL")))
        with ac2:
            a_type = st.selectbox("Typ alertu", ["Cena překročí", "Cena klesne pod", "Buy Score překročí", "Buy Score klesne pod"])
        with ac3:
            a_val = st.number_input("Hodnota", min_value=0.0, value=100.0, step=0.5)
        with ac4:
            a_note = st.text_input("Poznámka (volitelné)", placeholder="Proč tento alert?")
        if st.button("🔔 Přidat alert", use_container_width=True):
            if a_ticker:
                alerts.append({
                    "ticker": a_ticker,
                    "type":   a_type,
                    "value":  a_val,
                    "note":   a_note,
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "triggered": False,
                })
                data["alerts"] = alerts
                save_data(data)
                st.success(f"Alert přidán: {a_ticker} {a_type} {a_val}")
                st.rerun()

    if not alerts:
        st.info("Žádné alerty. Přidej svůj první alert výše.")
        return

    # Check alerts against live data
    st.markdown(f"<h3 style='color:{C['t1']};margin-bottom:.8rem;'>Aktivní alerty</h3>", unsafe_allow_html=True)

    triggered_count = 0
    for idx, alert in enumerate(alerts):
        t_sym  = alert["ticker"]
        a_type = alert["type"]
        a_val  = alert["value"]

        # Get current value
        try:
            h = yf.Ticker(t_sym).history(period="2d")
            cur_price = h["Close"].iloc[-1] if not h.empty else None
        except Exception:
            cur_price = None

        # Check trigger
        triggered = False
        cur_display = "–"
        if cur_price is not None:
            if "Score" in a_type:
                # Compute Buy Score
                df_a, info_a = fetch_stock(t_sym, period="1y")
                if df_a is not None and not df_a.empty:
                    df_a = calc_indicators(df_a)
                    an_a  = fetch_analyst_info(t_sym)
                    ins_a = fetch_insider_sec(t_sym)
                    sc_a  = compute_buy_score(df_a, info_a, an_a, ins_a)
                    cur_score = sc_a["score"] or 0
                    cur_display = f"Score: {cur_score:.0f}"
                    if "překročí" in a_type and cur_score > a_val:
                        triggered = True
                    elif "klesne" in a_type and cur_score < a_val:
                        triggered = True
            else:
                cur_display = f"${cur_price:.2f}"
                if "překročí" in a_type and cur_price > a_val:
                    triggered = True
                elif "klesne" in a_type and cur_price < a_val:
                    triggered = True

        status_col  = C["green"] if triggered else C["t3"]
        status_text = "🔴 SPUŠTĚN" if triggered else "⏳ Čeká"
        if triggered:
            triggered_count += 1

        st.markdown(f"""
            <div class="fa-card" style="border-color:{status_col}40;margin-bottom:8px;">
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                    <div>
                        <span style="font-weight:800;color:{C['blue']};font-size:1rem;">{t_sym}</span>
                        <span style="font-size:.82rem;color:{C['t2']};margin-left:10px;">{a_type} {a_val}</span>
                        {f'<span style="font-size:.75rem;color:{C["t3"]};margin-left:8px;">— {alert["note"]}</span>' if alert.get("note") else ""}
                    </div>
                    <div style="display:flex;align-items:center;gap:16px;">
                        <span class="mono" style="font-size:.9rem;color:{C['t1']};">Nyní: {cur_display}</span>
                        <span style="font-weight:700;color:{status_col};font-size:.9rem;">{status_text}</span>
                        <span style="font-size:.72rem;color:{C['t3']};">{alert.get('created','')}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        col_d1, col_d2, _ = st.columns([1,1,8])
        with col_d1:
            if st.button("🔍 Detail", key=f"al_det_{idx}", use_container_width=True):
                st.session_state["ticker"] = t_sym
                st.session_state["page"]   = "Stock Detail"
                st.rerun()
        with col_d2:
            if st.button("🗑️ Smazat", key=f"al_del_{idx}", use_container_width=True):
                alerts.pop(idx)
                data["alerts"] = alerts
                save_data(data)
                st.rerun()

    if triggered_count > 0:
        st.success(f"🔴 {triggered_count} alert(ů) bylo spuštěno!")

# ─────────────────────────────────────────────
#  PAGE: SCREENER
# ─────────────────────────────────────────────
def page_screener():
    st.markdown("<h2 class='grad' style='margin:0 0 1rem;'>🔎 Stock Screener</h2>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:.83rem;color:{C['t3']};margin-bottom:1rem;'>Filtruj akcie z watchlistu podle fundamentů a techniky. Pro screener celého trhu použij finviz.com nebo similar.</div>", unsafe_allow_html=True)

    # Filters
    with st.expander("🔧 Filtry", expanded=True):
        fc1,fc2,fc3 = st.columns(3)
        with fc1:
            min_pe = st.number_input("Max P/E", value=50.0, step=5.0)
            min_mc = st.number_input("Min Market Cap ($B)", value=0.0, step=1.0)
        with fc2:
            min_chg = st.number_input("Min. denní změna (%)", value=-100.0, step=0.5)
            max_chg = st.number_input("Max. denní změna (%)", value=100.0, step=0.5)
        with fc3:
            sector_filter = st.multiselect("Sektor", ["Technology","Healthcare","Finance","Energy","Consumer","Industrial","Real Estate","N/A"], default=[])
            sort_by = st.selectbox("Seřadit dle", ["Denní změna","Tržní cap.","P/E","Buy Score"])

    data = load_data()
    wl   = data.get("watchlist", [])

    # Expand watchlist with popular additions
    screen_pool = list(set(wl + ["AAPL","MSFT","NVDA","GOOGL","META","AMZN","TSLA","JPM","BAC","JNJ","UNH","XOM","CVX","WMT","HD"]))

    if st.button("🔍 Spustit screener", use_container_width=True):
        with st.spinner("Načítám data…"):
            mdata = fetch_multi(screen_pool)

        results = []
        for t, info in mdata.items():
            pe_val = info.get("pe") or 999
            mc_val = (info.get("market_cap") or 0) / 1e9
            chg    = info.get("change", 0)
            sec    = info.get("sector","N/A")

            if pe_val and pe_val > min_pe: continue
            if mc_val < min_mc: continue
            if chg < min_chg or chg > max_chg: continue
            if sector_filter and sec not in sector_filter: continue
            # Compute quick Buy Score for screener sorting
            score_val = 50
            if sort_by == "Buy Score":
                df_sc, info_sc = fetch_stock(t, period="1y")
                if df_sc is not None and not df_sc.empty:
                    df_sc = calc_indicators(df_sc)
                    an_sc  = fetch_analyst_info(t)
                    ins_sc = fetch_insider_sec(t)
                    sc_sc  = compute_buy_score(df_sc, info_sc, an_sc, ins_sc)
                    score_val = sc_sc.get("score") or 50
            results.append({**info, "ticker": t, "mc_b": mc_val, "pe_val": pe_val if pe_val<999 else None, "score": score_val})

        if not results:
            st.warning("Žádné akcie neodpovídají filtrům.")
            return

        # Sort
        sort_key = {"Denní změna": lambda x: abs(x["change"]),
                    "Tržní cap.":  lambda x: x["mc_b"],
                    "P/E":         lambda x: x["pe_val"] or 999,
                    "Buy Score":   lambda x: x.get("score",0)}.get(sort_by, lambda x: abs(x["change"]))
        results = sorted(results, key=sort_key, reverse=(sort_by != "P/E"))

        st.markdown(f"<div style='font-size:.85rem;color:{C['t2']};margin:8px 0;'>Nalezeno {len(results)} akcií</div>", unsafe_allow_html=True)

        # Table
        st.markdown(f"""
            <div style="background:{C['card']};border:1px solid {C['border']};border-radius:12px;overflow:hidden;">
            <div style="display:flex;padding:8px 14px;background:{C['bg2']};font-size:.72rem;color:{C['t3']};text-transform:uppercase;font-weight:600;letter-spacing:.05em;gap:8px;">
                <span style="flex:1;">Ticker</span><span style="flex:2;">Název</span>
                <span style="flex:1;text-align:right;">Cena</span><span style="flex:1;text-align:right;">Změna</span>
                <span style="flex:1;text-align:right;">P/E</span><span style="flex:1.5;text-align:right;">Tržní kap.</span>
                <span style="flex:1.5;">Sektor</span>
            </div>
        """, unsafe_allow_html=True)

        for r in results[:30]:
            chg = r["change"]
            col = C["green"] if chg>=0 else C["red"]
            pe_str = f"{r['pe_val']:.1f}" if r.get("pe_val") else "–"
            mc_str = f"${r['mc_b']:.1f}B" if r.get("mc_b") else "–"
            st.markdown(f"""
                <div style="display:flex;padding:8px 14px;border-bottom:1px solid {C['border']};gap:8px;align-items:center;font-size:.82rem;">
                    <span style="flex:1;font-weight:700;color:{C['blue']};">{r['ticker']}</span>
                    <span style="flex:2;color:{C['t2']};">{r.get('name','')[:20]}</span>
                    <span class="mono" style="flex:1;text-align:right;color:{C['t1']};">${r['price']:,.2f}</span>
                    <span class="mono" style="flex:1;text-align:right;color:{col};">{chg:+.2f}%</span>
                    <span class="mono" style="flex:1;text-align:right;color:{C['t2']};">{pe_str}</span>
                    <span class="mono" style="flex:1.5;text-align:right;color:{C['t2']};">{mc_str}</span>
                    <span style="flex:1.5;color:{C['t3']};font-size:.75rem;">{r.get('sector','')[:16]}</span>
                </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Detail buttons
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        btn_cols = st.columns(min(len(results), 6))
        for idx, r in enumerate(results[:6]):
            with btn_cols[idx]:
                if st.button(f"🔍 {r['ticker']}", key=f"sc_det_{r['ticker']}", use_container_width=True):
                    st.session_state["ticker"] = r["ticker"]
                    st.session_state["page"]   = "Stock Detail"
                    st.rerun()

# ─────────────────────────────────────────────
#  PAGE: SETTINGS
# ─────────────────────────────────────────────
def page_settings():
    st.markdown("<h2 class='grad' style='margin:0 0 1rem;'>⚙️ Nastavení</h2>", unsafe_allow_html=True)
    data = ensure_data_schema(load_data())

    st.subheader("🧭 Preference")
    pref1, pref2 = st.columns(2)
    prefs = data.get("preferences", {})
    with pref1:
        debug_mode = st.toggle("Debug mód (zobrazit technické chyby)", value=bool(prefs.get("debug_mode", False)))
    with pref2:
        language = st.selectbox("Jazyk UI", ["CZ", "EN"], index=0 if prefs.get("language", "CZ") == "CZ" else 1)
    if debug_mode != bool(prefs.get("debug_mode", False)) or language != prefs.get("language", "CZ"):
        data["preferences"]["debug_mode"] = debug_mode
        data["preferences"]["language"] = language
        save_data(data)
        st.success("Preference uloženy.")

    st.subheader("⭐ Watchlist")
    wl = data.get("watchlist", [])
    st.markdown(f"<div style='font-size:.83rem;color:{C['t3']};margin-bottom:8px;'>Aktuálně: {', '.join(wl)}</div>", unsafe_allow_html=True)

    wc1, wc2 = st.columns(2)
    with wc1:
        new_sym = normalized_ticker_input("Přidat symbol", key="settings_new_symbol", default="", placeholder="např. GOOG")
        if st.button("➕ Přidat"):
            if new_sym and new_sym not in wl:
                wl.append(new_sym)
                data["watchlist"] = wl
                save_data(data)
                st.success(f"{new_sym} přidán")
                st.rerun()
    with wc2:
        rem = st.selectbox("Odebrat symbol", ["—"] + wl)
        if st.button("🗑️ Odebrat") and rem != "—":
            wl.remove(rem)
            data["watchlist"] = wl
            save_data(data)
            st.success(f"{rem} odebrán")
            st.rerun()

    st.markdown("---")
    st.subheader("🗑️ Správa dat")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        if st.button("⚠️ Smazat portfolio", type="secondary"):
            data["portfolio"] = {}
            save_data(data)
            st.warning("Portfolio smazáno.")
    with col_d2:
        if st.button("⚠️ Smazat všechny alerty", type="secondary"):
            data["alerts"] = []
            save_data(data)
            st.warning("Alerty smazány.")

    # Export full data
    st.markdown("---")
    st.subheader("📤 Export")
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    st.download_button("📥 Stáhnout všechna data (JSON)",
                       json_str.encode("utf-8"),
                       f"finanalyzer_backup_{datetime.now().strftime('%Y%m%d')}.json",
                       "application/json")

    st.markdown("---")
    st.subheader("📥 Import")
    uploaded = st.file_uploader("Nahrát zálohu (JSON)", type=["json"])
    if uploaded is not None:
        try:
            imported = json.load(uploaded)
            imported = ensure_data_schema(imported)
            save_data(imported)
            st.success("Data byla úspěšně importována.")
            st.rerun()
        except Exception as e:
            st.error("Import se nezdařil. Zkontroluj prosím formát souboru.")
            log_debug(f"Import failed: {e}")

    st.markdown("---")
    st.markdown(f"""
        <div style="font-size:.78rem;color:{C['t3']};line-height:1.8;">
        <b style="color:{C['t2']};">Datové zdroje:</b><br>
        · Yahoo Finance (yfinance) — ceny, fundamenty, analytici, earnings, news<br>
        · SEC EDGAR (data.sec.gov) — Form-4 insider filings (bez API klíče)<br>
        · FRED (fred.stlouisfed.org) — makroekonomická data Fed, CPI, GDP, výnosy (bez API klíče)<br>
        · Buy Score algoritmus — vlastní vážený model (technická 25%, fundamenty 25%, momentum 20%, analytici 20%, insider 10%)<br>
        · Piotroski F-Score — 9-bodový fundamentální scoring model (Profitabilita + Zadluženost + Efektivita)<br>
        · Monte Carlo — log-normální simulace cenových trajektorií<br>
        · Backtesting — SMA/EMA/RSI/MACD crossover strategie s poplatky<br><br>
        <b style="color:{C['orange']};">⚠️ Disclaimer:</b> Tato aplikace je analytický nástroj. Veškerá data jsou zpožděná.
        Nic zde není investiční poradenství. Vždy proveď vlastní due diligence.
        </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGE: EKONOMICKÝ KALENDÁŘ (MAKRO)
# ─────────────────────────────────────────────
def _macro_series_map() -> dict:
    """Central mapping: label -> FRED series ID."""
    return {
        "CPI YoY (%)": "CPIAUCSL",
        "Unemployment Rate (%)": "UNRATE",
        "FED Funds Rate (%)": "FEDFUNDS",
        "GDP Growth QoQ (%)": "A191RL1Q225SBEA",
        "10Y Treasury Yield (%)": "DGS10",
        "Inflation Expectations 10Y (%)": "T10YIEM",
    }

def _fred_client():
    """
    Build FRED client via fredapi + st.secrets key.
    Returns (client_or_none, error_message_or_none).
    """
    api_key = os.getenv("FRED_API_KEY", None)
    if not api_key:
        try:
            # to_dict() is safer for optional lookup than direct indexing/get
            sec = st.secrets.to_dict() if hasattr(st.secrets, "to_dict") else {}
            api_key = sec.get("FRED_API_KEY", None)
        except Exception:
            api_key = None
    if not api_key:
        return None, None
    try:
        from fredapi import Fred
        return Fred(api_key=api_key), None
    except Exception as e:
        return None, f"Nepodařilo se inicializovat fredapi ({e})."

def _fetch_fred_series_public(series_id: str, months: int = 60) -> pd.Series:
    """
    Public fallback without API key (pandas_datareader -> FRED).
    """
    try:
        from pandas_datareader import data as web
        start = datetime.now() - timedelta(days=int(months * 31))
        df = web.DataReader(series_id, "fred", start, datetime.now())
        if df is None or df.empty:
            return pd.Series(dtype=float)
        s = pd.to_numeric(df.iloc[:, 0], errors="coerce").dropna()
        s.index = pd.to_datetime(s.index)
        return s.sort_index().iloc[-months:]
    except Exception as e:
        log_debug(f"_fetch_fred_series_public({series_id}) failed: {e}")
        return pd.Series(dtype=float)

@st.cache_data(ttl=1800)
def fetch_fred_series(series_id: str, months: int = 60) -> pd.Series:
    """Fetch one FRED series (fredapi with key, else public fallback)."""
    fred, err = _fred_client()
    if fred is not None:
        try:
            s = fred.get_series(series_id)
            if s is None or len(s) == 0:
                return pd.Series(dtype=float)
            s = pd.Series(s).dropna()
            s.index = pd.to_datetime(s.index)
            s = pd.to_numeric(s, errors="coerce").dropna()
            return s.sort_index().iloc[-months:]
        except Exception as e:
            log_debug(f"fetch_fred_series fredapi({series_id}) failed: {e}")
    # fallback path: no key or fredapi failed
    return _fetch_fred_series_public(series_id, months=months)

@st.cache_data(ttl=900)
def fetch_macro_snapshot() -> dict:
    """Fetch all key macro indicators used in the macro dashboard."""
    series_map = _macro_series_map()
    out = {}
    for label, sid in series_map.items():
        s = fetch_fred_series(sid, months=24)
        if len(s) >= 2:
            out[label] = {
                "series_id": sid,
                "value": float(s.iloc[-1]),
                "prev": float(s.iloc[-2]),
                "delta": float(s.iloc[-1] - s.iloc[-2]),
                "date": str(s.index[-1].date()),
                "series": s,
            }
    return out

@st.cache_data(ttl=3600)
def compute_sector_macro_corr(period: str = "1y") -> pd.DataFrame:
    """Rolling relevance matrix based on real historical correlations."""
    sector_map = {
        "Tech (XLK)": "XLK",
        "Finance (XLF)": "XLF",
        "Energy (XLE)": "XLE",
        "Consumer (XLY)": "XLY",
        "Healthcare (XLV)": "XLV",
        "Real Estate (XLRE)": "XLRE",
    }
    macro_map = {
        "S&P 500 (^GSPC)": "^GSPC",
        "DXY (DX-Y.NYB)": "DX-Y.NYB",
        "VIX (^VIX)": "^VIX",
        "10Y Yield (^TNX)": "^TNX",
    }
    prices = {}
    for label, sym in {**sector_map, **macro_map}.items():
        try:
            h = yf.Ticker(sym).history(period=period)["Close"]
            if h is not None and not h.empty:
                prices[label] = h
        except Exception as e:
            log_debug(f"compute_sector_macro_corr failed for {sym}: {e}")
    if len(prices) < 5:
        return pd.DataFrame()
    px = pd.DataFrame(prices).dropna(how="all").ffill().dropna()
    if px.empty:
        return pd.DataFrame()
    rets = px.pct_change().dropna()
    if rets.empty:
        return pd.DataFrame()
    sector_cols = [c for c in sector_map if c in rets.columns]
    macro_cols = [c for c in macro_map if c in rets.columns]
    if not sector_cols or not macro_cols:
        return pd.DataFrame()
    mat = pd.DataFrame(index=sector_cols, columns=macro_cols, dtype=float)
    for s in sector_cols:
        for m in macro_cols:
            mat.loc[s, m] = rets[s].corr(rets[m])
    return mat

def _parse_calendar_number(val) -> float:
    if val is None:
        return np.nan
    txt = str(val).strip()
    if txt in ("", "-", "N/A", "nan", "None"):
        return np.nan
    txt = txt.replace("%", "").replace("K", "").replace("M", "").replace("B", "")
    txt = txt.replace(",", "")
    try:
        return float(txt)
    except Exception:
        return np.nan

def _impact_rank(impact_txt: str) -> int:
    t = (impact_txt or "").lower()
    if "high" in t:
        return 3
    if "medium" in t:
        return 2
    if "low" in t:
        return 1
    return 0

@st.cache_data(ttl=1800)
def _fetch_economic_calendar_cached(from_date: str, to_date: str, countries: list, importances: list) -> pd.DataFrame:
    """
    Cached fetch wrapper for investpy economic calendar.
    `from_date`, `to_date` format: dd/mm/yyyy
    """
    try:
        import investpy
        df = investpy.economic_calendar(
            from_date=from_date,
            to_date=to_date,
            countries=countries if countries else None,
            importances=importances if importances else None,
        )
        if df is None:
            return pd.DataFrame()
        return df.copy()
    except Exception:
        return pd.DataFrame()

def _economic_calendar_placeholder() -> pd.DataFrame:
    rows = [
        ("2026-04-07", "08:30", "🇺🇸 US", "●●●", "US Nonfarm Payrolls", "212K", "190K", "176K"),
        ("2026-04-07", "08:30", "🇺🇸 US", "●●●", "US Unemployment Rate", "4.1%", "4.2%", "4.2%"),
        ("2026-04-07", "10:00", "🇺🇸 US", "●●", "ISM Services PMI", "53.1", "52.5", "52.2"),
        ("2026-04-08", "14:00", "🇺🇸 US", "●●●", "FOMC Interest Rate Decision", "5.25%", "5.25%", "5.25%"),
        ("2026-04-08", "08:30", "🇪🇺 EU", "●●●", "Eurozone CPI YoY", "2.3%", "2.4%", "2.5%"),
        ("2026-04-08", "05:00", "🇪🇺 EU", "●●", "Eurozone GDP QoQ", "0.3%", "0.2%", "0.2%"),
        ("2026-04-09", "02:00", "🇬🇧 UK", "●●", "UK CPI YoY", "2.9%", "3.0%", "3.1%"),
        ("2026-04-09", "02:00", "🇬🇧 UK", "●", "UK Retail Sales MoM", "0.2%", "-0.1%", "-0.3%"),
        ("2026-04-10", "21:30", "🇨🇳 CN", "●●", "China Manufacturing PMI", "50.6", "50.2", "49.9"),
        ("2026-04-10", "21:30", "🇨🇳 CN", "●", "China CPI YoY", "0.8%", "0.7%", "0.6%"),
        ("2026-04-11", "19:50", "🇯🇵 JP", "●", "Japan Industrial Production MoM", "0.4%", "0.2%", "-0.1%"),
        ("2026-04-11", "19:50", "🇯🇵 JP", "●●", "BoJ Core CPI", "2.1%", "2.0%", "2.0%"),
    ]
    ph = pd.DataFrame(rows, columns=["Date", "Time (GMT)", "Country", "Impact", "Event", "Actual", "Forecast", "Previous"])
    day_map = {"Mon": "Mon", "Tue": "Tue", "Wed": "Wed", "Thu": "Thu", "Fri": "Fri", "Sat": "Sat", "Sun": "Sun"}
    ph["Day"] = pd.to_datetime(ph["Date"], errors="coerce").dt.strftime("%a").map(day_map).fillna("N/A")
    a = ph["Actual"].map(_parse_calendar_number)
    f = ph["Forecast"].map(_parse_calendar_number)
    ph["Surprise"] = (a - f).map(lambda x: f"{x:+.2f}" if pd.notna(x) else "N/A")
    ph["_impact_rank"] = ph["Impact"].map(lambda x: 3 if x == "●●●" else 2 if x == "●●" else 1)
    return ph

def economic_calendar_tab():
    """Peak quality free Economic Calendar tab using investpy + styled fallback."""
    st.markdown("<h3 class='grad' style='margin:0 0 .6rem;'>📅 Economic Calendar</h3>", unsafe_allow_html=True)
    st.caption(f"Current Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} GMT")

    # Quick range filters
    q1, q2, q3, q4, q5 = st.columns(5)
    quick = None
    with q1:
        if st.button("Yesterday", use_container_width=True, key="ec_yesterday"): quick = "yesterday"
    with q2:
        if st.button("Today", use_container_width=True, key="ec_today"): quick = "today"
    with q3:
        if st.button("Tomorrow", use_container_width=True, key="ec_tomorrow"): quick = "tomorrow"
    with q4:
        if st.button("This Week", use_container_width=True, key="ec_week"): quick = "week"
    with q5:
        if st.button("This Month", use_container_width=True, key="ec_month"): quick = "month"

    today = datetime.utcnow().date()
    default_from, default_to = today, today + timedelta(days=7)
    if quick == "yesterday":
        default_from = default_to = today - timedelta(days=1)
    elif quick == "today":
        default_from = default_to = today
    elif quick == "tomorrow":
        default_from = default_to = today + timedelta(days=1)
    elif quick == "week":
        default_from, default_to = today, today + timedelta(days=6)
    elif quick == "month":
        default_from, default_to = today, today + timedelta(days=30)

    f1, f2, f3, f4 = st.columns([2, 1.3, 1.2, 1.2])
    with f1:
        date_range = st.date_input("Date range", value=(default_from, default_to), key="ec_date_range")
    with f2:
        country_ui = st.selectbox("Country", ["All", "USA", "Eurozone", "United Kingdom", "China", "Japan"], index=1, key="ec_country")
    with f3:
        impact_ui = st.selectbox("Impact", ["All", "High", "Medium", "Low"], index=0, key="ec_impact")
    with f4:
        sort_ui = st.selectbox("Sort by", ["Time", "Impact"], index=0, key="ec_sort")

    if isinstance(date_range, tuple) and len(date_range) == 2:
        d_from, d_to = date_range
    else:
        d_from = d_to = date_range
    if d_from > d_to:
        d_from, d_to = d_to, d_from

    country_map = {
        "All": [],
        "USA": ["united states"],
        "Eurozone": ["euro zone"],
        "United Kingdom": ["united kingdom"],
        "China": ["china"],
        "Japan": ["japan"],
    }
    impact_map = {"All": [], "High": ["high"], "Medium": ["medium"], "Low": ["low"]}
    country_flags = {
        "united states": "🇺🇸 US",
        "euro zone": "🇪🇺 EU",
        "united kingdom": "🇬🇧 UK",
        "china": "🇨🇳 CN",
        "japan": "🇯🇵 JP",
    }

    with st.spinner("Načítám ekonomický kalendář..."):
        raw_df = _fetch_economic_calendar_cached(
            d_from.strftime("%d/%m/%Y"),
            d_to.strftime("%d/%m/%Y"),
            country_map.get(country_ui, []),
            impact_map.get(impact_ui, []),
        )

    used_placeholder = False
    if raw_df.empty:
        used_placeholder = True
        st.warning("investpy momentálně nevrátil data. Zobrazuji realistický placeholder (duben 2026).")
        out = _economic_calendar_placeholder()
    else:
        df_cols = {c.lower(): c for c in raw_df.columns}
        col_time = df_cols.get("time", "time") if "time" in df_cols else None
        col_date = df_cols.get("date", "date") if "date" in df_cols else None
        col_country = df_cols.get("country", "country") if "country" in df_cols else None
        col_importance = df_cols.get("importance", "importance") if "importance" in df_cols else None
        col_event = df_cols.get("event", "event") if "event" in df_cols else None
        col_actual = df_cols.get("actual", "actual") if "actual" in df_cols else None
        col_forecast = df_cols.get("forecast", "forecast") if "forecast" in df_cols else None
        col_previous = df_cols.get("previous", "previous") if "previous" in df_cols else None

        out = pd.DataFrame()
        if col_date in raw_df.columns:
            dt_series = pd.to_datetime(raw_df[col_date], errors="coerce")
            out["Date"] = dt_series.dt.strftime("%Y-%m-%d").fillna(raw_df[col_date].astype(str))
            out["Day"] = dt_series.dt.strftime("%a").fillna("N/A")
        else:
            out["Date"] = d_from.strftime("%Y-%m-%d")
            out["Day"] = d_from.strftime("%a")
        out["Time (GMT)"] = raw_df[col_time].astype(str).fillna("N/A") if col_time in raw_df.columns else "N/A"
        if col_country in raw_df.columns:
            out["Country"] = raw_df[col_country].astype(str).str.lower().map(country_flags).fillna(raw_df[col_country].astype(str))
        else:
            out["Country"] = "N/A"
        imp_raw = raw_df[col_importance].astype(str) if col_importance in raw_df.columns else pd.Series([""] * len(raw_df))

        def impact_display(txt: str) -> str:
            t = (txt or "").lower()
            if "high" in t: return "●●●"
            if "medium" in t: return "●●"
            if "low" in t: return "●"
            return "·"

        out["Impact"] = imp_raw.map(impact_display)
        out["Event"] = raw_df[col_event].astype(str) if col_event in raw_df.columns else "N/A"
        out["Actual"] = raw_df[col_actual].astype(str) if col_actual in raw_df.columns else "N/A"
        out["Forecast"] = raw_df[col_forecast].astype(str) if col_forecast in raw_df.columns else "N/A"
        out["Previous"] = raw_df[col_previous].astype(str) if col_previous in raw_df.columns else "N/A"
        out["Surprise"] = (out["Actual"].map(_parse_calendar_number) - out["Forecast"].map(_parse_calendar_number)).map(
            lambda x: f"{x:+.2f}" if pd.notna(x) else "N/A"
        )
        out["_impact_rank"] = imp_raw.map(_impact_rank)

    if "_impact_rank" not in out.columns:
        out["_impact_rank"] = out["Impact"].map(lambda x: 3 if x == "●●●" else 2 if x == "●●" else 1 if x == "●" else 0)

    if sort_ui == "Impact":
        out = out.sort_values(["Date", "_impact_rank", "Time (GMT)"], ascending=[True, False, True])
    else:
        out = out.sort_values(["Date", "Time (GMT)", "_impact_rank"], ascending=[True, True, False])

    def row_style(row):
        if row["Impact"] == "●●●":
            return ["background-color: rgba(244,63,94,0.16)"] * len(row)
        if row["Impact"] == "●●":
            return ["background-color: rgba(245,158,11,0.10)"] * len(row)
        if row["Impact"] == "●":
            return ["background-color: rgba(34,197,94,0.08)"] * len(row)
        return [""] * len(row)

    def impact_style(v):
        if v == "●●●": return "color:#f43f5e;font-weight:800;"
        if v == "●●": return "color:#f59e0b;font-weight:800;"
        if v == "●": return "color:#22c55e;font-weight:800;"
        return "color:#94a3b8;"

    def surprise_style(v):
        if isinstance(v, str) and v.startswith("+"): return "color:#22c55e;font-weight:700;"
        if isinstance(v, str) and v.startswith("-"): return "color:#f43f5e;font-weight:700;"
        return "color:#94a3b8;"

    show_cols = ["Date", "Day", "Time (GMT)", "Country", "Impact", "Event", "Actual", "Forecast", "Previous", "Surprise"]
    styled = out[show_cols].style.apply(row_style, axis=1).applymap(impact_style, subset=["Impact"]).applymap(
        surprise_style, subset=["Surprise"]
    ).set_properties(subset=["Event"], **{"font-weight": "700"})
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.markdown(
        f"""
        <div class="fa-card" style="margin-top:10px;">
            <div style="font-weight:700;color:{C['t1']};margin-bottom:6px;">Legenda</div>
            <div style="font-size:.85rem;color:{C['t2']};line-height:1.7;">
                ● nízký impact (zelená) · ●● střední impact (oranžová) · ●●● vysoký impact (červená)<br>
                Surprise = Actual − Forecast (zeleně pozitivní, červeně negativní).
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if hasattr(st, "link_button"):
        st.link_button("Otevřít plný kalendář na Investing.com", "https://www.investing.com/economic-calendar/")
    else:
        st.markdown("[Otevřít plný kalendář na Investing.com](https://www.investing.com/economic-calendar/)")
    st.caption(
        "Placeholder data (duben 2026)." if used_placeholder
        else "Reálná data z investpy. V další verzi přejdeme na stabilnější API (FMP / Trading Economics)."
    )

def page_makro():
    st.markdown("<h2 class='grad' style='margin:0 0 1rem;'>🌍 Makroekonomický Dashboard</h2>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='font-size:.84rem;color:{C['t3']};margin-bottom:1rem;'>"
        "Makro data jsou načítána z Federal Reserve (FRED) přes <b>fredapi</b> nebo veřejný fallback bez API klíče."
        "</div>",
        unsafe_allow_html=True,
    )

    fred_client, fred_error = _fred_client()
    if fred_error:
        st.warning(f"fredapi nebyla inicializována ({fred_error}). Přepínám na veřejný FRED fallback bez API klíče.")
    elif fred_client is None:
        st.info("Běží veřejný FRED režim bez API klíče (přes pandas_datareader).")

    tab_live, tab_charts, tab_matrix, tab_yield, tab_calendar = st.tabs(
        ["📊 Live indikátory", "📈 Grafy trendů", "🎯 Sektor × Makro korelace", "📐 Yield Curve", "📅 Economic Calendar"]
    )

    # ── TAB 1: Live indikátory ───────────────────────────────
    with tab_live:
        with st.spinner("Načítám live makro indikátory z FRED…"):
            macro = fetch_macro_snapshot()
        if not macro:
            st.warning(
                "Nepodařilo se načíst makro data z FRED. "
                "Zkontrolujte API key (`st.secrets['FRED_API_KEY']`) nebo síťové připojení."
            )
        else:
            key_order = [
                "CPI YoY (%)",
                "Unemployment Rate (%)",
                "FED Funds Rate (%)",
                "GDP Growth QoQ (%)",
                "10Y Treasury Yield (%)",
                "Inflation Expectations 10Y (%)",
            ]
            cols = st.columns(3)
            for i, label in enumerate(key_order):
                d = macro.get(label)
                with cols[i % 3]:
                    if d:
                        st.metric(label, f"{d['value']:.2f}", f"{d['delta']:+.2f}")
                        st.caption(f"Poslední update: {d['date']}")
                    else:
                        st.metric(label, "N/A", "N/A")
                        st.caption("Data nedostupná")

    # ── TAB 2: Grafy trendů ──────────────────────────────────
    with tab_charts:
        series_map = _macro_series_map()
        indicator = st.selectbox("Vyber indikátor", list(series_map.keys()), key="macro_indicator_select")
        months = st.slider("Počet měsíců", 12, 120, 60, key="macro_months_slider")

        with st.spinner(f"Načítám trend: {indicator}…"):
            s = fetch_fred_series(series_map[indicator], months=months)

        if s.empty:
            st.warning("Data nedostupná pro vybraný indikátor.")
        else:
            df_plot = pd.DataFrame({"Date": s.index, "Value": s.values})
            fig = px.line(df_plot, x="Date", y="Value", title=indicator, template="plotly_dark")
            fig.update_layout(**CHART_LAYOUT, height=420)
            fig.update_traces(line=dict(width=2.5, color=C["blue"]))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── TAB 3: Sektor × Makro korelace (placeholder) ─────────
    with tab_matrix:
        st.info(
            "Pro reálnou matici korelací potřebujeme propojit výnosy sektorových ETF "
            "(např. XLK, XLF, XLE…) z yfinance s makro sériemi z FRED."
        )
        placeholder_df = pd.DataFrame(
            {
                "Sektor": ["Tech", "Finance", "Energy", "Healthcare"],
                "Korelace s CPI": [0.22, -0.08, 0.31, 0.05],
                "Korelace s 10Y výnosem": [-0.41, 0.27, 0.19, -0.11],
            }
        )
        st.dataframe(placeholder_df, use_container_width=True, hide_index=True)

    # ── TAB 4: Yield Curve ───────────────────────────────────
    with tab_yield:
        with st.spinner("Načítám Yield Curve data z FRED…"):
            yc_map = {
                "3M": "DGS3MO",
                "2Y": "DGS2",
                "5Y": "DGS5",
                "10Y": "DGS10",
                "30Y": "DGS30",
            }
            yc_data = {k: fetch_fred_series(v, months=24) for k, v in yc_map.items()}

        if not yc_data or yc_data["10Y"].empty or yc_data["2Y"].empty:
            st.warning("Yield Curve data nejsou dostupná.")
        else:
            latest_curve = pd.DataFrame(
                {
                    "Maturity": list(yc_map.keys()),
                    "Yield": [yc_data[k].iloc[-1] if len(yc_data[k]) else np.nan for k in yc_map.keys()],
                }
            ).dropna()
            fig_curve = px.line(
                latest_curve,
                x="Maturity",
                y="Yield",
                markers=True,
                title="US Treasury Yield Curve (latest)",
                template="plotly_dark",
            )
            fig_curve.update_layout(**CHART_LAYOUT, height=380)
            fig_curve.update_traces(line=dict(width=3, color=C["blue"]))
            st.plotly_chart(fig_curve, use_container_width=True, config={"displayModeBar": False})

            spread = float(yc_data["10Y"].iloc[-1] - yc_data["2Y"].iloc[-1])
            prev_spread = float(yc_data["10Y"].iloc[-2] - yc_data["2Y"].iloc[-2]) if len(yc_data["10Y"]) > 1 and len(yc_data["2Y"]) > 1 else spread
            st.metric("10Y - 2Y Spread", f"{spread:+.2f}%", f"{(spread - prev_spread):+.2f}")

    # ── TAB 5: Economic Calendar (placeholder) ───────────────
    with tab_calendar:
        economic_calendar_tab()


# ─────────────────────────────────────────────
#  PAGE: BACKTESTING ENGINE
# ─────────────────────────────────────────────
def _run_backtest(df: pd.DataFrame, strategy: str, fast: int, slow: int,
                  rsi_buy: int, rsi_sell: int, initial_capital: float,
                  commission_pct: float) -> dict:
    """Run a simple strategy backtest on OHLCV data."""
    df = df.copy().dropna(subset=["Close"])
    df["SMA_fast"] = df["Close"].rolling(fast).mean()
    df["SMA_slow"] = df["Close"].rolling(slow).mean()

    delta = df["Close"].diff()
    gain  = delta.where(delta > 0, 0).rolling(14).mean()
    loss  = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs    = gain / loss.replace(0, np.nan)
    df["RSI_bt"] = 100 - (100 / (1 + rs))

    df["EMA_fast"] = df["Close"].ewm(span=fast, adjust=False).mean()
    df["EMA_slow"] = df["Close"].ewm(span=slow, adjust=False).mean()
    df["MACD_bt"]  = df["EMA_fast"] - df["EMA_slow"]
    df["MACD_sig"] = df["MACD_bt"].ewm(span=9, adjust=False).mean()

    # Generate signals
    df["signal"] = 0
    if strategy == "SMA Crossover":
        df.loc[(df["SMA_fast"] > df["SMA_slow"]) & (df["SMA_fast"].shift(1) <= df["SMA_slow"].shift(1)), "signal"] = 1
        df.loc[(df["SMA_fast"] < df["SMA_slow"]) & (df["SMA_fast"].shift(1) >= df["SMA_slow"].shift(1)), "signal"] = -1
    elif strategy == "EMA Crossover":
        df.loc[(df["EMA_fast"] > df["EMA_slow"]) & (df["EMA_fast"].shift(1) <= df["EMA_slow"].shift(1)), "signal"] = 1
        df.loc[(df["EMA_fast"] < df["EMA_slow"]) & (df["EMA_fast"].shift(1) >= df["EMA_slow"].shift(1)), "signal"] = -1
    elif strategy == "RSI Mean Reversion":
        df.loc[df["RSI_bt"] < rsi_buy,  "signal"] = 1
        df.loc[df["RSI_bt"] > rsi_sell, "signal"] = -1
    elif strategy == "MACD Crossover":
        df.loc[(df["MACD_bt"] > df["MACD_sig"]) & (df["MACD_bt"].shift(1) <= df["MACD_sig"].shift(1)), "signal"] = 1
        df.loc[(df["MACD_bt"] < df["MACD_sig"]) & (df["MACD_bt"].shift(1) >= df["MACD_sig"].shift(1)), "signal"] = -1

    # Simulate trades
    cash     = initial_capital
    shares   = 0.0
    equity   = []
    trades   = []
    position = 0

    for i, row in df.iterrows():
        price = row["Close"]
        sig   = row["signal"]
        if sig == 1 and position <= 0:
            shares_to_buy = cash / price
            commission    = shares_to_buy * price * commission_pct
            shares        = shares_to_buy
            cash          = 0 - commission
            position      = 1
            trades.append({"date": str(i.date()), "type": "BUY", "price": price, "shares": shares})
        elif sig == -1 and position > 0:
            proceeds   = shares * price
            commission = proceeds * commission_pct
            cash       = proceeds - commission
            shares     = 0.0
            position   = 0
            trades.append({"date": str(i.date()), "type": "SELL", "price": price, "shares": 0})
        equity.append(cash + shares * price)

    # Buy & hold benchmark
    bh_shares = initial_capital / df["Close"].iloc[0]
    bh_equity = (bh_shares * df["Close"]).values

    final_equity = equity[-1] if equity else initial_capital
    total_return = (final_equity - initial_capital) / initial_capital * 100
    bh_return    = (bh_equity[-1] - initial_capital) / initial_capital * 100
    alpha        = total_return - bh_return

    eq_series = pd.Series(equity, index=df.index[-len(equity):])
    daily_ret = eq_series.pct_change().dropna()
    sharpe    = daily_ret.mean() / daily_ret.std() * np.sqrt(252) if daily_ret.std() > 0 else 0
    max_dd    = ((eq_series / eq_series.cummax()) - 1).min() * 100
    win_trades = [i for i in range(1, len(trades), 2)
                  if i < len(trades) and trades[i]["price"] > trades[i-1]["price"]]
    win_rate  = len(win_trades) / max(len(trades)//2, 1) * 100

    return {
        "equity":       equity,
        "bh_equity":    bh_equity.tolist(),
        "dates":        [str(d.date()) for d in df.index[-len(equity):]][:len(equity)],
        "total_return": round(total_return, 2),
        "bh_return":    round(bh_return, 2),
        "alpha":        round(alpha, 2),
        "sharpe":       round(sharpe, 3),
        "max_dd":       round(max_dd, 2),
        "n_trades":     len(trades),
        "win_rate":     round(win_rate, 1),
        "trades":       trades[:30],
    }

def page_backtesting():
    st.markdown("<h2 class='grad' style='margin:0 0 1rem;'>⚗️ Backtesting Engine</h2>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:.83rem;color:{C['t3']};margin-bottom:1rem;'>Otestuj svou strategii na historických datech s reálnými poplatky. Klíčový nástroj pro pochopení, co funguje.</div>", unsafe_allow_html=True)

    bc1, bc2, bc3, bc4 = st.columns(4)
    with bc1:
        bt_ticker = normalized_ticker_input("Ticker", key="bt_ticker", default="AAPL")
        bt_period = st.selectbox("Období", ["1y","2y","3y","5y","10y"], index=2)
    with bc2:
        strategy = st.selectbox("Strategie", ["SMA Crossover","EMA Crossover","RSI Mean Reversion","MACD Crossover"])
        bt_capital = st.number_input("Počáteční kapitál ($)", value=10000, step=1000)
    with bc3:
        fast_p = st.number_input("Rychlá MA / RSI buy", value=20 if "RSI" not in strategy else 30, step=1)
        slow_p = st.number_input("Pomalá MA / RSI sell", value=50 if "RSI" not in strategy else 70, step=1)
    with bc4:
        commission = st.number_input("Poplatek za obchod (%)", value=0.1, step=0.05, format="%.2f") / 100
        bt_btn = st.button("▶ Spustit backtest", use_container_width=True, type="primary")

    if bt_btn:
        with st.spinner(f"Načítám data a spouštím backtest pro {bt_ticker}…"):
            df_bt, _ = fetch_stock(bt_ticker, period=bt_period)
        if df_bt is None or df_bt.empty:
            st.error(f"Nelze načíst data pro {bt_ticker}")
            return

        rsi_b = int(fast_p) if "RSI" in strategy else 30
        rsi_s = int(slow_p) if "RSI" in strategy else 70
        fast_v = int(fast_p) if "RSI" not in strategy else 12
        slow_v = int(slow_p) if "RSI" not in strategy else 26

        result = _run_backtest(df_bt, strategy, fast_v, slow_v, rsi_b, rsi_s, bt_capital, commission)

        # Metrics
        alpha_col = C["green"] if result["alpha"] >= 0 else C["red"]
        ret_col   = C["green"] if result["total_return"] >= 0 else C["red"]
        r1,r2,r3,r4,r5,r6 = st.columns(6)
        metrics_bt = [
            (r1, "Výnos strategie",  f"{result['total_return']:+.1f}%", ret_col),
            (r2, "Buy & Hold",       f"{result['bh_return']:+.1f}%",    C["t2"]),
            (r3, "Alpha vs B&H",     f"{result['alpha']:+.1f}%",        alpha_col),
            (r4, "Sharpe Ratio",     f"{result['sharpe']:.2f}",         C["blue"]),
            (r5, "Max Drawdown",     f"{result['max_dd']:.1f}%",        C["red"]),
            (r6, "Win Rate",         f"{result['win_rate']:.0f}%",      C["orange"]),
        ]
        for col_o, lbl, val, clr in metrics_bt:
            with col_o:
                st.markdown(f"""
                    <div class="fa-card" style="text-align:center;border-color:{clr}30;">
                        <div style="font-size:.68rem;color:{C['t2']};text-transform:uppercase;">{lbl}</div>
                        <div class="mono" style="font-size:1.4rem;font-weight:800;color:{clr};margin:5px 0;">{val}</div>
                    </div>
                """, unsafe_allow_html=True)

        # Equity curve
        st.markdown("---")
        bt_fig = go.Figure()
        bt_fig.add_trace(go.Scatter(
            x=result["dates"], y=result["equity"], name=f"{strategy}",
            line=dict(color=C["blue"], width=2.2),
        ))
        bt_fig.add_trace(go.Scatter(
            x=result["dates"], y=result["bh_equity"], name="Buy & Hold",
            line=dict(color=C["t3"], width=1.5, dash="dash"), opacity=.7,
        ))
        bt_fig.update_layout(
            **CHART_LAYOUT,
            legend=dict(orientation="h", y=1.02, bgcolor="rgba(0,0,0,0)"),
            height=380, showlegend=True,
        )
        bt_fig.update_yaxes(tickprefix="$", tickfont=dict(color=C["t2"]))
        st.plotly_chart(bt_fig, use_container_width=True, config={"displayModeBar": False})

        # Drawdown chart
        eq_s = pd.Series(result["equity"])
        dd   = ((eq_s / eq_s.cummax()) - 1) * 100
        dd_fig = go.Figure(go.Scatter(
            x=result["dates"][:len(dd)], y=dd.values,
            fill="tozeroy", fillcolor=with_alpha(C["red"], 0.13),
            line=dict(color=C["red"], width=1.5), name="Drawdown",
        ))
        dd_layout = {**CHART_LAYOUT, "margin": dict(l=10,r=10,t=10,b=10)}
        dd_fig.update_layout(**dd_layout, height=180, showlegend=False)
        dd_fig.update_yaxes(ticksuffix="%", tickfont=dict(color=C["t2"]))
        st.plotly_chart(dd_fig, use_container_width=True, config={"displayModeBar": False})

        # Trade log
        if result["trades"]:
            st.markdown("---")
            st.markdown(f"<div style='font-weight:600;color:{C['t2']};margin-bottom:6px;'>📋 Obchodní log (prvních {len(result['trades'])} obchodů)</div>", unsafe_allow_html=True)
            st.markdown(f"""
                <div style="background:{C['card']};border:1px solid {C['border']};border-radius:10px;overflow:hidden;">
                <div style="display:flex;padding:7px 14px;background:{C['bg2']};font-size:.7rem;color:{C['t3']};text-transform:uppercase;font-weight:600;gap:8px;">
                    <span style="flex:1.5">Datum</span><span style="flex:1">Typ</span><span style="flex:1;text-align:right">Cena</span>
                </div>
            """, unsafe_allow_html=True)
            for tr in result["trades"]:
                tc = C["green"] if tr["type"] == "BUY" else C["red"]
                st.markdown(f"""
                    <div style="display:flex;padding:7px 14px;border-bottom:1px solid {C['border']};gap:8px;font-size:.82rem;">
                        <span class="mono" style="flex:1.5;color:{C['t1']};">{tr['date']}</span>
                        <span style="flex:1;font-weight:700;color:{tc};">{tr['type']}</span>
                        <span class="mono" style="flex:1;text-align:right;color:{C['t1']};">${tr['price']:.2f}</span>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
            <div style="padding:8px 14px;background:{C['bg2']};border-radius:8px;font-size:.75rem;color:{C['t3']};margin-top:10px;">
            ⚠️ Backtesting nepočítá s reálnými náklady jako bid-ask spread, market impact a liquidity rizika. Výsledky z minulosti nezaručují budoucí výnosy.
            Použij výsledky jako vodítko, ne jako jistotu.
            </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE: MONTE CARLO SIMULACE
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def run_monte_carlo(ticker: str, n_simulations: int, n_days: int, period: str = "2y") -> dict:
    """Monte Carlo price path simulation using historical returns."""
    try:
        df  = yf.Ticker(ticker).history(period=period)["Close"].dropna()
        if len(df) < 30:
            return {}
        returns      = df.pct_change().dropna()
        mu           = returns.mean()
        sigma        = returns.std()
        last_price   = df.iloc[-1]
        sims         = np.zeros((n_days, n_simulations))
        for s in range(n_simulations):
            prices = [last_price]
            for _ in range(n_days - 1):
                shock = np.random.normal(mu, sigma)
                prices.append(prices[-1] * (1 + shock))
            sims[:, s] = prices
        final_prices = sims[-1, :]
        percentiles  = np.percentile(final_prices, [5, 10, 25, 50, 75, 90, 95])
        var_95       = np.percentile(final_prices / last_price - 1, 5) * 100
        prob_profit  = (final_prices > last_price).mean() * 100
        prob_10pct   = (final_prices > last_price * 1.10).mean() * 100
        prob_loss10  = (final_prices < last_price * 0.90).mean() * 100
        return {
            "sims":         sims,
            "last_price":   last_price,
            "percentiles":  percentiles,
            "var_95":       round(var_95, 2),
            "prob_profit":  round(prob_profit, 1),
            "prob_10pct":   round(prob_10pct, 1),
            "prob_loss10":  round(prob_loss10, 1),
            "mu":           round(mu * 252 * 100, 2),
            "sigma":        round(sigma * np.sqrt(252) * 100, 2),
        }
    except Exception:
        return {}

def page_monte_carlo():
    st.markdown("<h2 class='grad' style='margin:0 0 1rem;'>🎲 Monte Carlo Simulace</h2>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:.83rem;color:{C['t3']};margin-bottom:1rem;'>Simuluje tisíce možných cenových trajektorií na základě historické volatility. Vizualizuj riziko a pravděpodobnost ziskovosti.</div>", unsafe_allow_html=True)

    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1: mc_ticker = normalized_ticker_input("Ticker", key="mc_ticker", default=st.session_state.get("ticker","AAPL"))
    with mc2: mc_sims   = st.select_slider("Počet simulací", options=[100, 500, 1000, 5000, 10000], value=1000)
    with mc3: mc_days   = st.slider("Horizont (dní)", 30, 365, 252)
    with mc4: mc_period = st.selectbox("Historická data (báze)", ["1y","2y","3y","5y"], index=1)

    if st.button("🎲 Spustit simulaci", use_container_width=True, type="primary"):
        with st.spinner(f"Spouštím {mc_sims:,} simulací pro {mc_ticker}…"):
            mc_res = run_monte_carlo(mc_ticker, mc_sims, mc_days, mc_period)

        if not mc_res:
            st.error("Nepodařilo se spustit simulaci. Zkontroluj ticker.")
            return

        # Summary cards
        lp = mc_res["last_price"]
        pcts = mc_res["percentiles"]
        p5, p10, p25, p50, p75, p90, p95 = pcts
        pp_col  = C["green"] if mc_res["prob_profit"] >= 50 else C["red"]
        var_col = C["red"]

        s1,s2,s3,s4,s5,s6 = st.columns(6)
        mc_cards = [
            (s1, "Median výsledek",    f"${p50:.0f}", f"{(p50/lp-1)*100:+.1f}%", C["blue"]),
            (s2, "P10 (bear case)",    f"${p10:.0f}", f"{(p10/lp-1)*100:+.1f}%", C["red"]),
            (s3, "P90 (bull case)",    f"${p90:.0f}", f"{(p90/lp-1)*100:+.1f}%", C["green"]),
            (s4, "VaR 95% (% loss)",   f"{mc_res['var_95']:.1f}%", None,         var_col),
            (s5, "P(profit)",          f"{mc_res['prob_profit']:.0f}%", None,     pp_col),
            (s6, "P(+10%)",            f"{mc_res['prob_10pct']:.0f}%", None,      C["green"]),
        ]
        for col_o, lbl, val, sub, clr in mc_cards:
            with col_o:
                st.markdown(f"""
                    <div class="fa-card" style="text-align:center;border-color:{clr}30;">
                        <div style="font-size:.65rem;color:{C['t2']};text-transform:uppercase;line-height:1.2;">{lbl}</div>
                        <div class="mono" style="font-size:1.3rem;font-weight:800;color:{clr};margin:5px 0;">{val}</div>
                        {f'<div style="font-size:.75rem;color:{clr};">{sub}</div>' if sub else ''}
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # Plot fan chart (sample 200 paths for performance)
        sims = mc_res["sims"]
        n_show = min(200, mc_sims)
        idx_show = np.random.choice(mc_sims, n_show, replace=False)
        x_axis = list(range(mc_days))

        fig_mc = go.Figure()
        for s in idx_show:
            fig_mc.add_trace(go.Scatter(
                x=x_axis, y=sims[:, s],
                mode="lines", line=dict(width=0.4, color=C["blue"]),
                opacity=0.08, showlegend=False,
            ))
        # Percentile bands
        for pct_val, pct_name, pct_color, pct_dash in [
            (5,  "P5",  C["red"],    "dash"),
            (25, "P25", C["orange"], "dot"),
            (50, "Medián", C["green"], "solid"),
            (75, "P75", C["orange"], "dot"),
            (95, "P95", C["green"],  "dash"),
        ]:
            pct_line = np.percentile(sims, pct_val, axis=1)
            fig_mc.add_trace(go.Scatter(
                x=x_axis, y=pct_line,
                mode="lines", name=pct_name,
                line=dict(width=2, color=pct_color, dash=pct_dash),
            ))
        fig_mc.add_hline(y=lp, line_dash="dot", line_color=C["t3"], opacity=.5,
                         annotation_text="Aktuální cena", annotation_position="bottom right")
        fig_mc.update_layout(
            **CHART_LAYOUT,
            legend=dict(orientation="h", y=1.02, bgcolor="rgba(0,0,0,0)"),
            height=420, showlegend=True,
        )
        fig_mc.update_xaxes(title="Dny", tickfont=dict(color=C["t2"]))
        fig_mc.update_yaxes(tickprefix="$", tickfont=dict(color=C["t2"]))
        st.plotly_chart(fig_mc, use_container_width=True, config={"displayModeBar": False})

        # Final price distribution histogram
        final_prices = sims[-1, :]
        hist_fig = go.Figure(go.Histogram(
            x=final_prices, nbinsx=80,
            marker_color=C["blue"], marker_opacity=0.7,
            name="Rozložení výsledků",
        ))
        hist_fig.add_vline(x=lp,  line_dash="dash", line_color=C["t3"],
                           annotation_text=f"Dnes ${lp:.0f}")
        hist_fig.add_vline(x=p50, line_dash="dash", line_color=C["green"],
                           annotation_text=f"Medián ${p50:.0f}")
        hist_fig.add_vline(x=p5,  line_dash="dash", line_color=C["red"],
                           annotation_text=f"P5 ${p5:.0f}")
        hist_layout = {**CHART_LAYOUT, "margin": dict(l=10,r=10,t=20,b=10)}
        hist_fig.update_layout(**hist_layout, height=250, showlegend=False)
        hist_fig.update_xaxes(tickprefix="$")
        hist_fig.update_yaxes(title="Četnost")
        st.plotly_chart(hist_fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown(f"""
            <div style="padding:8px 14px;background:{C['bg2']};border-radius:8px;font-size:.75rem;color:{C['t3']};margin-top:6px;">
            📌 Annualizovaný drift: <b style="color:{C['t1']};">{mc_res['mu']:+.1f}%</b> &nbsp;·&nbsp;
            Annualizovaná volatilita: <b style="color:{C['t1']};">{mc_res['sigma']:.1f}%</b> &nbsp;·&nbsp;
            P(ztráta &gt; 10%): <b style="color:{C['red']};">{mc_res['prob_loss10']:.0f}%</b><br>
            ⚠️ Simulace předpokládá log-normální rozdělení výnosů a konstantní volatilitu. Reálné trhy mají tučné ocasy a volatility clustering.
            </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE: PIOTROSKI F-SCORE + FUNDAMENTÁLNÍ SCREENER
# ─────────────────────────────────────────────
def compute_piotroski(info: dict, financials_df=None, balance_df=None) -> dict:
    """
    Piotroski F-Score (0–9). Každé kritérium = 1 bod.
    Skupiny: Profitabilita (4), Pákový efekt/likvidita (3), Provozní efektivita (2).
    Score 8-9 = silná koupě, 0-2 = varování.
    """
    score = 0
    details = []

    def add(name: str, condition: bool, desc_true: str, desc_false: str):
        nonlocal score
        val = 1 if condition else 0
        score += val
        details.append({"criterion": name, "score": val, "desc": desc_true if condition else desc_false})

    # ── PROFITABILITA ──────────────────────────
    roa = info.get("returnOnAssets", None)
    add("ROA > 0",
        roa is not None and roa > 0,
        f"ROA {roa*100:.1f}% — kladné (profitabilní)",
        f"ROA {roa*100:.1f}% — záporné (ztrátová)" if roa is not None else "ROA nedostupné")

    fcf_i = info.get("freeCashflow", None)
    add("Free Cash Flow > 0",
        fcf_i is not None and fcf_i > 0,
        f"FCF ${fcf_i/1e9:.1f}B — kladný",
        f"FCF ${fcf_i/1e9:.1f}B — záporný" if fcf_i is not None else "FCF nedostupné")

    # ROA change (proxy: compare ROA to forward ROA if available)
    roa_fwd = info.get("returnOnEquity", None)  # use as proxy
    add("ROA se zlepšuje (proxy: ROE > ROA)",
        roa is not None and roa_fwd is not None and roa_fwd > roa,
        "ROE > ROA — kapitál je efektivně páčen",
        "ROE ≤ ROA — pákový efekt nepřidává hodnotu")

    # Accruals: FCF > Net Income (quality of earnings)
    ni = info.get("netIncomeToCommon", None)
    add("FCF > Net Income (kvalita zisků)",
        fcf_i is not None and ni is not None and fcf_i > ni,
        "FCF > čistý zisk — zisky jsou reálné (cash-backed)",
        "FCF < čistý zisk — zisky zahrnují velké accruals (pozor!)")

    # ── ZADLUŽENOST & LIKVIDITA ────────────────
    de = info.get("debtToEquity", None)
    add("D/E se nezhoršil (D/E < 100)",
        de is not None and de < 100,
        f"D/E {de:.0f} — přijatelná zadluženost",
        f"D/E {de:.0f} — vysoká zadluženost" if de is not None else "D/E nedostupné")

    cr = info.get("currentRatio", None)
    add("Current Ratio > 1",
        cr is not None and cr > 1,
        f"Current Ratio {cr:.2f} — dobrá likvidita",
        f"Current Ratio {cr:.2f} — riziko likvidity" if cr is not None else "Current Ratio nedostupné")

    shares = info.get("sharesOutstanding", None)
    float_s = info.get("floatShares", None)
    add("Žádné nové emise akcií (float ≤ shares)",
        shares is not None and float_s is not None and float_s <= shares * 1.02,
        "Float ≤ shares outstanding — žádné ředění",
        "Možné ředění akcionářů (nové emise)")

    # ── PROVOZNÍ EFEKTIVITA ────────────────────
    gm = info.get("grossMargins", None)
    add("Hrubá marže > 20%",
        gm is not None and gm > 0.20,
        f"Hrubá marže {gm*100:.1f}% — silná",
        f"Hrubá marže {gm*100:.1f}% — slabá" if gm is not None else "Hrubá marže nedostupná")

    at = info.get("assetTurnover", None)
    # fallback: revenue / total assets
    rev    = info.get("totalRevenue", None)
    assets = info.get("totalAssets", None)
    if at is None and rev and assets:
        at = rev / assets
    add("Asset Turnover > 0.5",
        at is not None and at > 0.5,
        f"Asset Turnover {at:.2f} — efektivní využití aktiv",
        f"Asset Turnover {at:.2f} — neefektivní aktiva" if at is not None else "Asset Turnover nedostupný")

    if score >= 8:
        label, color = "SILNÝ FUNDAMENT", C["green"]
    elif score >= 6:
        label, color = "DOBRÝ FUNDAMENT", "#4ade80"
    elif score >= 4:
        label, color = "PRŮMĚRNÝ", C["orange"]
    elif score >= 2:
        label, color = "SLABÝ FUNDAMENT", "#fb923c"
    else:
        label, color = "VAROVÁNÍ", C["red"]

    return {"score": score, "label": label, "color": color, "details": details}

def page_piotroski():
    st.markdown("<h2 class='grad' style='margin:0 0 1rem;'>🏆 Piotroski F-Score + Fundamentální Screener</h2>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:.83rem;color:{C['t3']};margin-bottom:1rem;'>Piotroski F-Score (0–9) měří kvalitu fundamentů. Score 8–9 = silný fundament. Kombinuje profitabilitu, zadluženost a provozní efektivitu.</div>", unsafe_allow_html=True)
    st.caption("ℹ️ Některá kritéria používají proxy metriky (např. ROE vs ROA), pokud nejsou plná data dostupná.")

    tab_single, tab_screen = st.tabs(["🔍 Analýza jedné akcie", "📋 Batch screener"])

    with tab_single:
        ps_ticker = normalized_ticker_input("Ticker", key="ps_ticker", default=st.session_state.get("ticker","AAPL"))
        if st.button("📊 Spočítat F-Score", use_container_width=True):
            with st.spinner(f"Načítám fundamenty pro {ps_ticker}…"):
                _, ps_info = fetch_stock(ps_ticker, "1y")
            ps_result = compute_piotroski(ps_info)
            sc = ps_result["score"]
            clr = ps_result["color"]
            lbl = ps_result["label"]

            pr1, pr2 = st.columns([1, 2])
            with pr1:
                # Gauge
                fig_pf = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=sc,
                    number={"font": {"size": 56, "family": "JetBrains Mono", "color": clr}},
                    gauge={
                        "axis": {"range": [0, 9], "tickfont": {"color": C["t2"]}},
                        "bar":  {"color": clr, "thickness": 0.25},
                        "bgcolor": "rgba(0,0,0,0)",
                        "bordercolor": C["border"],
                        "steps": [
                            {"range": [0, 2],  "color": "rgba(255,61,90,0.18)"},
                            {"range": [2, 4],  "color": "rgba(245,158,11,0.12)"},
                            {"range": [4, 6],  "color": "rgba(255,255,255,0.04)"},
                            {"range": [6, 8],  "color": "rgba(74,222,128,0.10)"},
                            {"range": [8, 9],  "color": "rgba(0,230,118,0.20)"},
                        ],
                        "threshold": {"line": {"color": clr, "width": 3}, "thickness": 0.8, "value": sc},
                    },
                ))
                fig_pf.update_layout(height=260, margin=dict(l=20,r=20,t=20,b=10),
                    paper_bgcolor="rgba(0,0,0,0)", font=dict(color=C["t1"]))
                st.plotly_chart(fig_pf, use_container_width=True, config={"displayModeBar": False})
                st.markdown(f"""
                    <div style="text-align:center;margin-top:-10px;">
                        <div style="font-size:1.4rem;font-weight:800;color:{clr};">{lbl}</div>
                        <div style="font-size:.78rem;color:{C['t3']};margin-top:4px;">Piotroski F-Score {sc}/9</div>
                    </div>
                """, unsafe_allow_html=True)

            with pr2:
                groups = [
                    ("💰 Profitabilita", ps_result["details"][:4]),
                    ("🏦 Zadluženost & Likvidita", ps_result["details"][4:7]),
                    ("⚙️ Provozní efektivita", ps_result["details"][7:]),
                ]
                for grp_name, items in groups:
                    grp_score = sum(i["score"] for i in items)
                    grp_total = len(items)
                    st.markdown(f"<div style='font-size:.82rem;font-weight:700;color:{C['t2']};margin:10px 0 5px;'>{grp_name} ({grp_score}/{grp_total})</div>", unsafe_allow_html=True)
                    for item in items:
                        ic  = C["green"] if item["score"] else C["red"]
                        ico = "✅" if item["score"] else "❌"
                        st.markdown(f"""
                            <div style="display:flex;align-items:flex-start;gap:8px;padding:6px 10px;background:{C['card']};border-radius:6px;margin-bottom:3px;border:1px solid {C['border']};">
                                <span style="min-width:18px;">{ico}</span>
                                <div>
                                    <span style="font-size:.78rem;font-weight:600;color:{C['t2']};">{item['criterion']}</span><br>
                                    <span style="font-size:.75rem;color:{ic};">{item['desc']}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

    with tab_screen:
        st.markdown(f"<div style='font-size:.83rem;color:{C['t3']};margin-bottom:.8rem;'>Spočítej F-Score pro celý watchlist + vlastní akcie. Rychlý způsob jak najít akcie s nejsilnějšími fundamenty.</div>", unsafe_allow_html=True)
        data_ps = load_data()
        screen_pool_ps = list(set(data_ps.get("watchlist", []) +
            ["AAPL","MSFT","NVDA","GOOGL","META","AMZN","TSLA","JPM","BRK-B","JNJ","UNH","V","MA","HD","PG"]))
        extra = st.text_input("Přidat vlastní tickery (odděleny čárkou)", placeholder="ORCL, IBM, INTC")
        if extra:
            screen_pool_ps = list(set(screen_pool_ps + [t.strip().upper() for t in extra.split(",") if t.strip()]))

        min_fscore = st.slider("Minimální F-Score", 0, 9, 6)
        if st.button("🔍 Spustit batch F-Score screener", use_container_width=True):
            ps_results = []
            prog_ps = st.progress(0, text="Načítám fundamenty…")
            for pi, t_ps in enumerate(screen_pool_ps):
                try:
                    _, info_ps = fetch_stock(t_ps, "1y")
                    res_ps = compute_piotroski(info_ps)
                    if res_ps["score"] >= min_fscore:
                        ps_results.append({"ticker": t_ps, **res_ps})
                except Exception:
                    pass
                prog_ps.progress((pi+1)/len(screen_pool_ps), text=f"Načítám {t_ps}…")
            prog_ps.empty()

            if not ps_results:
                st.info(f"Žádná akcie nedosáhla F-Score ≥ {min_fscore}.")
            else:
                ps_results.sort(key=lambda x: x["score"], reverse=True)
                st.markdown(f"<div style='font-size:.85rem;color:{C['t2']};margin:8px 0;'>Nalezeno {len(ps_results)} akcií s F-Score ≥ {min_fscore}</div>", unsafe_allow_html=True)
                ps_cols = st.columns(min(len(ps_results), 4))
                for pi2, res_ps2 in enumerate(ps_results):
                    with ps_cols[pi2 % 4]:
                        clr2 = res_ps2["color"]
                        st.markdown(f"""
                            <div class="fa-card" style="text-align:center;border-color:{clr2}40;margin-bottom:8px;">
                                <div style="font-weight:800;color:{C['blue']};font-size:1.1rem;">{res_ps2['ticker']}</div>
                                <div class="mono" style="font-size:2.2rem;font-weight:800;color:{clr2};margin:6px 0;">{res_ps2['score']}/9</div>
                                <div style="font-size:.78rem;font-weight:700;color:{clr2};">{res_ps2['label']}</div>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"🔍 Detail {res_ps2['ticker']}", key=f"ps_det_{res_ps2['ticker']}", use_container_width=True):
                            st.session_state["ticker"] = res_ps2["ticker"]
                            st.session_state["page"]   = "Stock Detail"
                            st.rerun()




# ─────────────────────────────────────────────
#  v11: FEAR & GREED INDEX
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def compute_fear_greed() -> dict:
    try:
        scores = []; labels = []
        vix_h = yf.Ticker("^VIX").history(period="5d")
        if not vix_h.empty:
            vix = float(vix_h["Close"].iloc[-1])
            vix_score = max(0, min(100, 100 - (vix - 10) * 2.5))
            scores.append(vix_score); labels.append(("VIX", f"{vix:.1f}", round(vix_score)))
        spy_h = yf.Ticker("^GSPC").history(period="1y")
        if not spy_h.empty and len(spy_h) > 125:
            cur_spy = spy_h["Close"].iloc[-1]; ma125 = spy_h["Close"].iloc[-125:].mean()
            diff_pct = (cur_spy - ma125) / ma125 * 100
            mom_score = max(0, min(100, 50 + diff_pct * 3))
            scores.append(mom_score); labels.append(("S&P Momentum", f"{diff_pct:+.1f}%", round(mom_score)))
        hyg_h = yf.Ticker("HYG").history(period="30d"); lqd_h = yf.Ticker("LQD").history(period="30d")
        if not hyg_h.empty and not lqd_h.empty and len(hyg_h)>1 and len(lqd_h)>1:
            spread = (hyg_h["Close"].iloc[-1]/hyg_h["Close"].iloc[0]-1)*100 - (lqd_h["Close"].iloc[-1]/lqd_h["Close"].iloc[0]-1)*100
            junk_score = max(0, min(100, 50 + spread * 10))
            scores.append(junk_score); labels.append(("Junk Bond Demand", f"HYG-LQD: {spread:+.2f}%", round(junk_score)))
        if not spy_h.empty and len(spy_h) >= 10:
            up_days = int((spy_h["Close"].tail(10).diff() > 0).sum())
            breadth_score = max(0, min(100, up_days/10*100))
            scores.append(breadth_score); labels.append(("Market Breadth", f"{up_days}/10 up days", round(breadth_score)))
        gold_h = yf.Ticker("GC=F").history(period="30d")
        if not gold_h.empty and not spy_h.empty and len(spy_h)>=30:
            gold_ret = (gold_h["Close"].iloc[-1]/gold_h["Close"].iloc[0]-1)*100
            spy_ret  = (spy_h["Close"].iloc[-1]/spy_h["Close"].iloc[-30]-1)*100
            spread2  = spy_ret - gold_ret
            safe_score = max(0, min(100, 50 + spread2*2))
            scores.append(safe_score); labels.append(("Safe Haven", f"Stocks vs Gold: {spread2:+.1f}%", round(safe_score)))
        if not scores:
            return {"score":50,"label":"Neutrální","color":C["orange"],"components":[]}
        total = sum(scores)/len(scores)
        if total>=75:   fg_label,color="Extrémní chamtivost",C["green"]
        elif total>=55: fg_label,color="Chamtivost","#4ade80"
        elif total>=45: fg_label,color="Neutrální",C["orange"]
        elif total>=25: fg_label,color="Strach","#fb923c"
        else:           fg_label,color="Extrémní strach",C["red"]
        return {"score":round(total),"label":fg_label,"color":color,"components":labels}
    except Exception as e:
        return {"score":50,"label":"Neutrální","color":C["orange"],"components":[],"error":str(e)}


# ─────────────────────────────────────────────
#  v11: BLACK-SCHOLES
# ─────────────────────────────────────────────
def black_scholes(S,K,T,r,sigma,option_type="call"):
    import math
    if T<=0 or sigma<=0 or S<=0 or K<=0:
        intrinsic=max(0,S-K) if option_type=="call" else max(0,K-S)
        return {"price":intrinsic,"delta":0,"gamma":0,"theta":0,"vega":0,"rho":0}
    def _cdf(x): return 0.5*(1+math.erf(x/math.sqrt(2)))
    def _pdf(x): return math.exp(-0.5*x**2)/math.sqrt(2*math.pi)
    d1=(math.log(S/K)+(r+0.5*sigma**2)*T)/(sigma*math.sqrt(T)); d2=d1-sigma*math.sqrt(T)
    if option_type=="call":
        price=S*_cdf(d1)-K*math.exp(-r*T)*_cdf(d2); delta=_cdf(d1); rho=K*T*math.exp(-r*T)*_cdf(d2)/100
    else:
        price=K*math.exp(-r*T)*_cdf(-d2)-S*_cdf(-d1); delta=_cdf(d1)-1; rho=-K*T*math.exp(-r*T)*_cdf(-d2)/100
    gamma=_pdf(d1)/(S*sigma*math.sqrt(T))
    vega=S*_pdf(d1)*math.sqrt(T)/100
    theta=(-(S*_pdf(d1)*sigma)/(2*math.sqrt(T))-r*K*math.exp(-r*T)*(_cdf(d2) if option_type=="call" else _cdf(-d2)))/365
    return {"price":round(price,4),"delta":round(delta,4),"gamma":round(gamma,6),"theta":round(theta,4),"vega":round(vega,4),"rho":round(rho,4)}


# ─────────────────────────────────────────────
#  v11: DIVIDEND DATA
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_dividend_data(ticker):
    try:
        s=yf.Ticker(ticker); info=s.info or {}; div_hist=s.dividends
        if div_hist is None or div_hist.empty: return {"has_dividends":False,"info":info}
        div_hist=div_hist.copy(); div_hist.index=pd.to_datetime(div_hist.index).tz_localize(None)
        annual=div_hist.resample("YE").sum()
        cagr=None
        if len(annual)>=5:
            sv=float(annual.iloc[-5]); ev=float(annual.iloc[-1])
            if sv>0 and ev>0: cagr=(ev/sv)**(1/5)-1
        eps=info.get("trailingEps") or 0; div_rate=info.get("dividendRate") or 0
        payout_ratio=(div_rate/eps) if eps>0 else None
        growth_streak=0
        if len(annual)>=2:
            for i in range(len(annual)-1,0,-1):
                if annual.iloc[i]>annual.iloc[i-1]: growth_streak+=1
                else: break
        return {"has_dividends":True,"history":div_hist,"annual":annual,"yield":info.get("dividendYield") or 0,
                "rate":div_rate,"cagr":cagr,"payout_ratio":payout_ratio,"growth_streak":growth_streak,
                "ex_date":info.get("exDividendDate"),"info":info}
    except Exception as e:
        return {"has_dividends":False,"error":str(e)}


# ─────────────────────────────────────────────
#  v11: SEKTOR DATA
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_sector_performance():
    SECTORS={"Technology":"XLK","Healthcare":"XLV","Financials":"XLF","Energy":"XLE",
              "Consumer Disc.":"XLY","Consumer Stapl.":"XLP","Industrials":"XLI",
              "Materials":"XLB","Utilities":"XLU","Real Estate":"XLRE","Communication":"XLC"}
    results={}
    for name,etf in SECTORS.items():
        try:
            h=yf.Ticker(etf).history(period="30d")
            if h.empty or len(h)<5: continue
            d1=(h["Close"].iloc[-1]/h["Close"].iloc[-2]-1)*100
            w1=(h["Close"].iloc[-1]/h["Close"].iloc[min(-5,-len(h))]-1)*100
            m1=(h["Close"].iloc[-1]/h["Close"].iloc[0]-1)*100
            results[name]={"etf":etf,"1d":round(d1,2),"1w":round(w1,2),"1m":round(m1,2),"price":round(float(h["Close"].iloc[-1]),2)}
        except Exception: continue
    return results


# ─────────────────────────────────────────────
#  v11: PAGE — OPTIONS
# ─────────────────────────────────────────────
def page_options():
    st.markdown("<h2 class='grad' style='margin:0 0 .5rem;'>📐 Options Kalkulačka (Black-Scholes)</h2>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:.83rem;color:{C['t3']};margin-bottom:1rem;'>Fair value opcí a Greeks. Zadej parametry — výpočet okamžitě.</div>", unsafe_allow_html=True)
    tab_pricer, tab_payoff, tab_surface = st.tabs(["🧮 Pricer", "📊 Payoff Diagram", "🌊 Delta Povrch"])
    with tab_pricer:
        oc1,oc2 = st.columns([1,1])
        with oc1:
            opt_ticker = normalized_ticker_input("Ticker (auto načtení ceny)", "opt_ticker", default=st.session_state.get("ticker","AAPL"))
            opt_type = st.radio("Typ opce", ["Call","Put"], horizontal=True, key="opt_type_r")
            auto_price=None; auto_iv=30.0
            if opt_ticker:
                try:
                    h_opt=yf.Ticker(opt_ticker).history(period="2d")
                    if not h_opt.empty: auto_price=float(h_opt["Close"].iloc[-1])
                    _,oi=fetch_stock(opt_ticker,"1y"); beta=oi.get("beta") or 1.0
                    auto_iv=float(min(max(15.0,beta*22),90.0))
                except Exception: pass
            S=st.number_input("Aktuální cena (S)", value=auto_price or 150.0, step=1.0, format="%.2f")
            K=st.number_input("Strike cena (K)", value=round((auto_price or 150.0)*1.05,0), step=1.0, format="%.2f")
            T_days=st.number_input("Dny do expirace", min_value=1, max_value=730, value=30, step=1)
            T=T_days/365.0
            r=st.number_input("Bezriziková sazba (% p.a.)", 0.0, 20.0, 5.0, 0.1, format="%.1f")/100
            sigma=st.number_input("Implikovaná volatilita (%)", 1.0, 200.0, auto_iv, 0.5, format="%.1f")/100
        with oc2:
            result=black_scholes(S,K,T,r,sigma,opt_type.lower()); price=result["price"]
            is_itm=(S>K) if opt_type=="Call" else (S<K)
            itm_col=C["green"] if is_itm else C["red"]
            itm_lbl="IN THE MONEY ✅" if is_itm else "OUT OF THE MONEY ❌"
            intrinsic=max(0.0,S-K) if opt_type=="Call" else max(0.0,K-S)
            time_value=max(0.0,price-intrinsic)
            st.markdown(f"""
                <div class="fa-card" style="text-align:center;border-color:{itm_col}50;margin-bottom:14px;">
                    <div style="font-size:.75rem;color:{C['t3']};text-transform:uppercase;">{opt_type.upper()} OPTION PRICE</div>
                    <div class="mono" style="font-size:3rem;font-weight:800;color:{itm_col};">${price:.4f}</div>
                    <div style="font-size:.8rem;font-weight:700;color:{itm_col};margin-bottom:10px;">{itm_lbl}</div>
                    <div style="display:flex;justify-content:space-around;padding-top:10px;border-top:1px solid {C['border']};">
                        <div><div style="font-size:.7rem;color:{C['t3']};">Vnitřní hodnota</div><div class="mono" style="font-size:.95rem;color:{C['t1']};font-weight:700;">${intrinsic:.4f}</div></div>
                        <div><div style="font-size:.7rem;color:{C['t3']};">Časová hodnota</div><div class="mono" style="font-size:.95rem;color:{C['blue']};font-weight:700;">${time_value:.4f}</div></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            for lbl,val,desc,col in [
                ("Δ Delta",result["delta"],"Změna ceny na $1 pohyb podkladu",C["blue"]),
                ("Γ Gamma",result["gamma"],"Změna Delty na $1 pohyb",C["purple"]),
                ("Θ Theta",result["theta"],"Time decay za jeden den",C["red"]),
                ("V Vega",result["vega"],"Změna na 1% změnu volatility",C["green"]),
                ("ρ Rho",result["rho"],"Změna na 1% změnu sazby",C["orange"]),
            ]:
                st.markdown(f"""
                    <div style="display:flex;align-items:center;justify-content:space-between;padding:7px 10px;
                        background:{C['card']};border-radius:6px;margin-bottom:4px;border:1px solid {C['border']};">
                        <div>
                            <span style="font-size:.82rem;font-weight:700;color:{col};">{lbl}</span>
                            <span style="font-size:.72rem;color:{C['t3']};margin-left:8px;">{desc}</span>
                        </div>
                        <span class="mono" style="font-size:.9rem;font-weight:700;color:{C['t1']};">{val:+.4f}</span>
                    </div>
                """, unsafe_allow_html=True)
    with tab_payoff:
        try:
            price_range=np.linspace(S*0.5,S*1.5,200)
            payoff=np.maximum(0,price_range-K) if opt_type=="Call" else np.maximum(0,K-price_range)
            pnl=payoff-price
            fig_pay=go.Figure()
            fig_pay.add_trace(go.Scatter(x=price_range,y=pnl,name="P&L",
                line=dict(color=C["blue"],width=2.5),fill="tozeroy",fillcolor=with_alpha(C["blue"],0.10)))
            fig_pay.add_hline(y=0,line_color=C["border2"],line_dash="dash")
            fig_pay.add_vline(x=K,line_color=C["orange"],line_dash="dot",
                annotation_text=f"Strike ${K:.0f}",annotation_font_color=C["orange"])
            fig_pay.add_vline(x=S,line_color=C["green"],line_dash="dot",
                annotation_text=f"Spot ${S:.0f}",annotation_font_color=C["green"])
            fig_pay.update_layout(**CHART_LAYOUT,height=380,
                title=dict(text=f"{opt_type} Payoff Diagram",font=dict(color=C["t2"],size=13)),
                yaxis_title="P&L ($)",xaxis_title="Cena podkladu ($)")
            st.plotly_chart(fig_pay,use_container_width=True,config={"displayModeBar":False})
            breakeven=K+price if opt_type=="Call" else K-price
            be1,be2,be3=st.columns(3)
            with be1: st.metric("Breakeven",f"${breakeven:.2f}")
            with be2: st.metric("Max. ztráta (premium)",f"${abs(price):.4f}")
            with be3: st.metric("Max. zisk","Neomezený" if opt_type=="Call" else f"${K-price:.4f}")
        except Exception as e:
            st.warning(f"Nelze vykreslit payoff: {e}")
    with tab_surface:
        st.markdown(f"<div style='font-size:.83rem;color:{C['t3']};margin-bottom:.8rem;'>Delta povrch — jak se Delta mění s cenou podkladu a zbývajícím časem.</div>", unsafe_allow_html=True)
        try:
            spot_range=np.linspace(S*0.7,S*1.3,35); time_range=np.linspace(1/365,1.0,25)
            Z_delta=np.zeros((len(time_range),len(spot_range)))
            for ti,tv in enumerate(time_range):
                for si,sv in enumerate(spot_range):
                    Z_delta[ti,si]=black_scholes(sv,K,tv,r,sigma,opt_type.lower())["delta"]
            fig_surf=go.Figure(go.Surface(z=Z_delta,x=spot_range,y=time_range*365,
                colorscale="RdYlGn",colorbar=dict(title="Delta",tickfont=dict(color=C["t2"]))))
            fig_surf.update_layout(paper_bgcolor="rgba(0,0,0,0)",height=440,margin=dict(l=0,r=0,t=30,b=0),
                font=dict(color=C["t1"]),
                scene=dict(xaxis_title="Cena (S)",yaxis_title="Dny do exp.",zaxis_title="Delta",
                    xaxis=dict(backgroundcolor="rgba(0,0,0,0)",gridcolor=C["border"]),
                    yaxis=dict(backgroundcolor="rgba(0,0,0,0)",gridcolor=C["border"]),
                    zaxis=dict(backgroundcolor="rgba(0,0,0,0)",gridcolor=C["border"])))
            st.plotly_chart(fig_surf,use_container_width=True,config={"displayModeBar":False})
        except Exception as e:
            st.warning(f"Nelze vykreslit povrch: {e}")


# ─────────────────────────────────────────────
#  v11: PAGE — DIVIDENDY
# ─────────────────────────────────────────────
def page_dividendy():
    st.markdown("<h2 class='grad' style='margin:0 0 .5rem;'>💰 Dividend Tracker</h2>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:.83rem;color:{C['t3']};margin-bottom:1rem;'>Dividendové akcie, historie výplat, CAGR dividend a ex-dividend kalendář.</div>", unsafe_allow_html=True)
    tab_single,tab_screen,tab_calendar=st.tabs(["🔍 Analýza akcie","📋 Dividend Screener","📅 Ex-Div Kalendář"])
    with tab_single:
        div_ticker=normalized_ticker_input("Ticker","div_ticker",default=st.session_state.get("ticker","AAPL"))
        if st.button("📊 Načíst dividendová data",use_container_width=True,key="div_load"):
            with st.spinner("Načítám…"):
                ddata=fetch_dividend_data(div_ticker)
            st.session_state["div_data_cache"]=ddata; st.session_state["div_data_ticker"]=div_ticker
        ddata=st.session_state.get("div_data_cache") if st.session_state.get("div_data_ticker")==div_ticker else None
        if ddata is None:
            st.info("Klikni na tlačítko pro načtení.")
        elif not ddata.get("has_dividends"):
            st.warning(f"{div_ticker} nevyplácí dividendy nebo data nejsou dostupná.")
        else:
            dy=ddata.get("yield",0) or 0; rate=ddata.get("rate",0) or 0
            cagr=ddata.get("cagr"); pr=ddata.get("payout_ratio"); streak=ddata.get("growth_streak",0)
            m1,m2,m3,m4,m5=st.columns(5)
            with m1: st.metric("Dividendový výnos",f"{dy*100:.2f}%")
            with m2: st.metric("Roční dividenda",f"${rate:.2f}")
            with m3: st.metric("CAGR dividend (5Y)",f"{cagr*100:.1f}%" if cagr else "N/A")
            with m4: st.metric("Payout Ratio",f"{pr*100:.0f}%" if pr else "N/A")
            with m5: st.metric("Roky růstu za sebou",str(streak))
            st.markdown("---")
            annual=ddata.get("annual")
            if annual is not None and not annual.empty:
                years=[str(d.year) for d in annual.index]; values=annual.values.tolist()
                bar_colors=[C["green"] if i==len(values)-1 else with_alpha(C["blue"],0.6) for i in range(len(values))]
                fig_div=go.Figure(go.Bar(x=years,y=values,marker_color=bar_colors,
                    text=[f"${v:.2f}" for v in values],textposition="outside",textfont=dict(color=C["t2"],size=10)))
                fig_div.update_layout(**CHART_LAYOUT,height=300,
                    title=dict(text="Roční dividenda (USD/akcii)",font=dict(color=C["t2"],size=13)))
                st.plotly_chart(fig_div,use_container_width=True,config={"displayModeBar":False})
            hist=ddata.get("history")
            if hist is not None and not hist.empty:
                with st.expander("📋 Historie výplat (poslední 3 roky)"):
                    cutoff=pd.Timestamp.now()-pd.DateOffset(years=3)
                    recent=hist[hist.index>=cutoff].sort_index(ascending=False)
                    st.dataframe(recent.rename("Dividenda ($)").reset_index().rename(columns={"Date":"Datum"}),
                        use_container_width=True,hide_index=True)
    with tab_screen:
        div_pool_default=["AAPL","MSFT","JNJ","KO","PG","MCD","T","VZ","PEP","XOM","CVX","ABT","MMM","O","MAIN","SCHD","HDV","VYM","NOBL"]
        data_d=load_data(); div_pool=list(set(data_d.get("watchlist",[]) + div_pool_default))
        extra_d=st.text_input("Přidat vlastní tickery",placeholder="ENB, REALTY, …",key="div_extra")
        if extra_d: div_pool=list(set(div_pool+[t.strip().upper() for t in extra_d.split(",") if t.strip()]))
        min_yield=st.slider("Min. dividendový výnos (%)",0.0,15.0,2.0,0.5,key="div_miny")
        max_payout=st.slider("Max. payout ratio (%)",10,200,100,5,key="div_maxp")
        if st.button("🔍 Spustit dividend screener",use_container_width=True,key="div_screen"):
            screen_results=[]; prog=st.progress(0,text="Načítám…")
            for pi,tk in enumerate(div_pool):
                try:
                    dd=fetch_dividend_data(tk)
                    if not dd.get("has_dividends"): continue
                    dy_v=(dd.get("yield") or 0)*100; pr_v=(dd.get("payout_ratio") or 0)*100; cagr_v=(dd.get("cagr") or 0)*100
                    if dy_v<min_yield or pr_v>max_payout: continue
                    screen_results.append({"Ticker":tk,"Výnos %":round(dy_v,2),"Roční div $":round(dd.get("rate") or 0,2),
                        "CAGR 5Y %":round(cagr_v,1),"Payout %":round(pr_v,1),"Roky růstu":dd.get("growth_streak",0)})
                except Exception: pass
                prog.progress((pi+1)/len(div_pool),text=f"Kontroluji {tk}…")
            prog.empty()
            if not screen_results: st.info("Žádné akcie nesplňují kritéria.")
            else:
                screen_results.sort(key=lambda x:x["Výnos %"],reverse=True)
                st.dataframe(pd.DataFrame(screen_results),use_container_width=True,hide_index=True)
    with tab_calendar:
        data_cal=load_data()
        cal_pool=list(set(data_cal.get("watchlist",[]) + ["JNJ","KO","PG","MCD","T","VZ","XOM","CVX","MSFT","AAPL"]))
        cal_items=[]; prog_c=st.progress(0,text="Načítám kalendář…")
        for pi,tk in enumerate(cal_pool):
            try:
                info_cal=yf.Ticker(tk).info or {}
                ex_ts=info_cal.get("exDividendDate"); div_r=info_cal.get("dividendRate") or 0
                dy_c=(info_cal.get("dividendYield") or 0)*100
                if ex_ts and div_r>0:
                    ex_dt=datetime.fromtimestamp(int(ex_ts)).strftime("%Y-%m-%d")
                    days_to=(datetime.fromtimestamp(int(ex_ts))-datetime.now()).days
                    cal_items.append({"Ticker":tk,"Ex-Date":ex_dt,"Dny do ex-date":days_to,"Roční div $":round(div_r,2),"Výnos %":round(dy_c,2)})
            except Exception: pass
            prog_c.progress((pi+1)/len(cal_pool),text=f"Načítám {tk}…")
        prog_c.empty()
        if cal_items:
            cal_items.sort(key=lambda x:x["Dny do ex-date"])
            df_cal=pd.DataFrame(cal_items)
            upcoming=df_cal[df_cal["Dny do ex-date"]>=0].head(20)
            past=df_cal[df_cal["Dny do ex-date"]<0].tail(5)
            if not upcoming.empty:
                st.markdown(f"<div style='font-weight:600;color:{C['green']};margin-bottom:6px;'>📅 Nadcházející</div>", unsafe_allow_html=True)
                st.dataframe(upcoming,use_container_width=True,hide_index=True)
            if not past.empty:
                st.markdown(f"<div style='font-weight:600;color:{C['t3']};margin:10px 0 6px;'>⏮ Nedávné</div>", unsafe_allow_html=True)
                st.dataframe(past,use_container_width=True,hide_index=True)
        else:
            st.info("Žádné ex-dividend datum nenalezeno.")


# ─────────────────────────────────────────────
#  v11: PAGE — SEKTOR MAPA
# ─────────────────────────────────────────────
def page_sektor_mapa():
    st.markdown("<h2 class='grad' style='margin:0 0 .5rem;'>🗺️ Sektor Mapa & Rotace</h2>", unsafe_allow_html=True)
    tab_heat,tab_fg,tab_compare=st.tabs(["🌡️ Heatmapa sektorů","😱 Fear & Greed Index","📊 Srovnání sektorů"])
    with tab_heat:
        period_sm=st.radio("Zobrazit výkon za",["1d","1w","1m"],horizontal=True,index=1,key="sm_period")
        with st.spinner("Načítám sektor data…"):
            sdata=fetch_sector_performance()
        if not sdata:
            st.warning("Nelze načíst data sektorů.")
        else:
            sorted_sectors=sorted(sdata.items(),key=lambda x:x[1][period_sm],reverse=True)
            rows_sm=[sorted_sectors[i:i+4] for i in range(0,len(sorted_sectors),4)]
            for row in rows_sm:
                cols_sm=st.columns(4)
                for j,(sec_name,sec_data) in enumerate(row):
                    perf=sec_data[period_sm]; intensity=min(abs(perf)/3,1.0)
                    if perf>=0: bg=f"rgba(0,230,118,{0.08+intensity*0.28})"; col=C["green"]; icon="▲"
                    else:       bg=f"rgba(255,61,90,{0.08+intensity*0.28})";  col=C["red"];   icon="▼"
                    with cols_sm[j]:
                        st.markdown(f"""
                            <div class="fa-card" style="text-align:center;background:{bg};border-color:{col}30;padding:16px 10px;">
                                <div style="font-size:.72rem;color:{C['t2']};font-weight:600;text-transform:uppercase;">{sec_name}</div>
                                <div class="mono" style="font-size:1.6rem;font-weight:800;color:{col};margin:6px 0;">{icon} {abs(perf):.2f}%</div>
                                <div style="font-size:.72rem;color:{C['t3']};">{sec_data['etf']} · ${sec_data['price']:.2f}</div>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("🔍",key=f"sm_{sec_name}{j}",use_container_width=True):
                            st.session_state["ticker"]=sec_data["etf"]; st.session_state["page"]="Stock Detail"; st.rerun()
            st.markdown("---")
            labels_sm=[s[0] for s in sorted_sectors]; values_sm=[s[1][period_sm] for s in sorted_sectors]
            colors_sm=[C["green"] if v>=0 else C["red"] for v in values_sm]
            fig_sm=go.Figure(go.Bar(x=values_sm,y=labels_sm,orientation="h",marker_color=colors_sm,
                text=[f"{v:+.2f}%" for v in values_sm],textposition="outside",textfont=dict(color=C["t2"],size=10)))
            fig_sm.update_layout(**CHART_LAYOUT,height=360,
                title=dict(text=f"Výkon sektorů ({period_sm})",font=dict(color=C["t2"],size=13)),
                xaxis_title="Výkon (%)",yaxis=dict(showgrid=False,linecolor=C["border"],tickfont=dict(color=C["t2"])))
            st.plotly_chart(fig_sm,use_container_width=True,config={"displayModeBar":False})
    with tab_fg:
        st.markdown(f"<div style='font-size:.83rem;color:{C['t3']};margin-bottom:1rem;'>Vlastní Fear & Greed Index z VIX, S&P momentum, junk bondů, šíře trhu a safe haven demand.</div>", unsafe_allow_html=True)
        with st.spinner("Počítám Fear & Greed Index…"):
            fg=compute_fear_greed()
        score=fg["score"]; fg_label=fg["label"]; color=fg["color"]
        fg1,fg2=st.columns([1,2])
        with fg1:
            fig_fg=go.Figure(go.Indicator(mode="gauge+number",value=score,
                number={"font":{"size":52,"family":"JetBrains Mono","color":color}},
                gauge={"axis":{"range":[0,100],"tickfont":{"color":C["t2"]}},
                    "bar":{"color":color,"thickness":0.25},"bgcolor":"rgba(0,0,0,0)","bordercolor":C["border"],
                    "steps":[{"range":[0,25],"color":"rgba(255,61,90,0.20)"},{"range":[25,45],"color":"rgba(251,146,60,0.14)"},
                              {"range":[45,55],"color":"rgba(255,255,255,0.04)"},{"range":[55,75],"color":"rgba(74,222,128,0.12)"},
                              {"range":[75,100],"color":"rgba(0,230,118,0.22)"}],
                    "threshold":{"line":{"color":color,"width":3},"thickness":0.8,"value":score}}))
            fig_fg.update_layout(height=280,margin=dict(l=10,r=10,t=10,b=10),paper_bgcolor="rgba(0,0,0,0)",font=dict(color=C["t1"]))
            st.plotly_chart(fig_fg,use_container_width=True,config={"displayModeBar":False})
            st.markdown(f"""
                <div style="text-align:center;margin-top:-10px;">
                    <div style="font-size:1.4rem;font-weight:800;color:{color};">{fg_label}</div>
                    <div style="font-size:.75rem;color:{C['t3']};margin-top:4px;">Score {score}/100</div>
                </div>
            """, unsafe_allow_html=True)
        with fg2:
            st.markdown(f"<div style='font-weight:600;color:{C['t2']};margin-bottom:8px;'>Složky indexu</div>", unsafe_allow_html=True)
            for comp_name,comp_val,comp_score in fg.get("components",[]):
                bar_c=C["green"] if comp_score>=55 else C["orange"] if comp_score>=45 else C["red"]
                st.markdown(f"""
                    <div style="margin-bottom:10px;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                            <span style="font-size:.82rem;font-weight:600;color:{C['t2']};">{comp_name}</span>
                            <span style="display:flex;gap:14px;">
                                <span class="mono" style="font-size:.78rem;color:{C['t3']};">{comp_val}</span>
                                <span class="mono" style="font-size:.82rem;font-weight:700;color:{bar_c};">{comp_score}/100</span>
                            </span>
                        </div>
                        <div style="background:{C['bg2']};border-radius:4px;height:8px;overflow:hidden;">
                            <div style="width:{comp_score}%;background:{bar_c};height:100%;border-radius:4px;"></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    with tab_compare:
        with st.spinner("Načítám historická data…"):
            sdata2=fetch_sector_performance()
        if sdata2:
            selected_secs=st.multiselect("Vyber sektory ke srovnání",list(sdata2.keys()),default=list(sdata2.keys())[:5],key="sm_compare_sel")
            period_cmp=st.radio("Perioda",["1mo","3mo","6mo","1y"],horizontal=True,index=2,key="sm_cmp_per")
            if selected_secs:
                fig_cmp=go.Figure()
                palette=[C["blue"],C["green"],C["orange"],C["purple"],C["red"],"#f472b6","#34d399","#fb923c","#a78bfa","#60a5fa","#fbbf24"]
                for idx_s,sec_name in enumerate(selected_secs):
                    etf=sdata2[sec_name]["etf"]
                    try:
                        h_cmp=yf.Ticker(etf).history(period=period_cmp)["Close"]
                        if h_cmp.empty: continue
                        normed=h_cmp/h_cmp.iloc[0]*100
                        fig_cmp.add_trace(go.Scatter(x=normed.index,y=normed.values,name=f"{sec_name} ({etf})",
                            line=dict(color=palette[idx_s%len(palette)],width=2)))
                    except Exception: continue
                fig_cmp.add_hline(y=100,line_color=C["border2"],line_dash="dash",opacity=0.5)
                fig_cmp.update_layout(**CHART_LAYOUT,height=420,
                    title=dict(text="Normalizovaný výkon sektorů (báze=100)",font=dict(color=C["t2"],size=13)),
                    yaxis_title="Výkon (báze 100)",legend=dict(orientation="h",y=-0.15,bgcolor="rgba(0,0,0,0)"))
                st.plotly_chart(fig_cmp,use_container_width=True,config={"displayModeBar":False})


def main():
    if "page"   not in st.session_state: st.session_state["page"]   = "Dashboard"
    if "ticker" not in st.session_state: st.session_state["ticker"] = "AAPL"

    render_header()
    st.markdown("---")

    # Check alerts silently and show banner if any triggered
    data = load_data()
    triggered = [a for a in data.get("alerts",[]) if not a.get("triggered")]
    # (full check happens in alerts page to avoid slowing every page load)
    if triggered:
        st.warning(f"🔔 Máš {len(triggered)} aktivních alertů ke kontrole v záložce Alerty.")

    page = st.session_state["page"]
    ROUTER = {
        "Dashboard":    page_dashboard,
        "Stock Detail": page_stock_detail,
        "Portfolio":    page_portfolio,
        "Charts":       page_charts,
        "Multi-Asset":  page_multi_asset,
        "Insider":      page_insider,
        "Earnings":     page_earnings,
        "Alerty":       page_alerts,
        "Screener":     page_screener,
        "Makro":        page_makro,
        "Backtesting":  page_backtesting,
        "Monte Carlo":  page_monte_carlo,
        "Piotroski":    page_piotroski,
        "Options":      page_options,
        "Dividendy":    page_dividendy,
        "Sektor Mapa":  page_sektor_mapa,
        "Settings":     page_settings,
    }
    handler = ROUTER.get(page, page_dashboard)
    handler()

    st.markdown("---")
    st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:.72rem;color:{C['t3']};">◆ FinAnalyzer Pro v{APP_VERSION} · {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</span>
            <span style="font-size:.72rem;color:{C['t3']};">Data: Yahoo Finance · SEC EDGAR · Zpožděná data · v11 — Options · Dividendy · Sektor Mapa · Fear & Greed</span>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
