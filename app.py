import streamlit as st
import os
import asyncio
import traceback
from dotenv import load_dotenv
from ai_agents import ProfitableTraderAgent, DoctorSystemAgent
from metaapi_cloud_sdk import MetaApi

load_dotenv()
st.set_page_config(page_title="Multi-Timeframe AI Engine", layout="centered")

if "trader" not in st.session_state:
    st.session_state.trader = ProfitableTraderAgent(account_balance=10000, risk_pct=0.01)
if "doctor" not in st.session_state:
    st.session_state.doctor = DoctorSystemAgent()
if "system_logs" not in st.session_state:
    st.session_state.system_logs = ["🔄 Live 24/7 scanning matrix activated."]

st.title("📱 Multi-Timeframe AI Sniper Engine")

st.markdown("### ⚙️ Automation Matrix Controls")
symbol_to_scan = st.text_input("Target Trading Pair Symbol", value="EURUSD").upper()
target_rrr = st.slider("Minimum Macro RRR Filter (1:X)", min_value=2.0, max_value=12.0, value=6.0, step=0.5)

uploaded_pdf = st.file_uploader("Upload Strategy Rules (Optional PDF)", type=["pdf"])
if uploaded_pdf:
    with open(f"temp_{uploaded_pdf.name}", "wb") as f:
        f.write(uploaded_pdf.getbuffer())
    msg = st.session_state.trader.absorb_pdf_strategy(f"temp_{uploaded_pdf.name}")
    st.success(msg)
    os.remove(f"temp_{uploaded_pdf.name}")

if st.button("🔍 Execute Automated Multi-Timeframe Scan Live", use_container_width=True):
    async def fetch_and_scan_market():
        api = MetaApi(token=os.getenv("BROKER_GATEWAY_TOKEN"))
        account = await api.metatrader_account_api.get_account(account_id=os.getenv("BROKER_ACCOUNT_ID"))
        connection = account.get_rpc_connection()
        await connection.connect()
        await connection.wait_synchronized()
        
        results = []
        # Define structural scan map across separate market windows
        scan_matrix = [("M5", "Scalping Track"), ("H1", "Short-Term Track"), ("D1", "Long-Term Swing Track")]
        
        for tf, track_name in scan_matrix:
            # Live technical fetch from IC Markets data center
            candles = await connection.get_candles(symbol_to_scan, tf, 25)
            if candles:
                decision = st.session_state.trader.automatic_market_scanner(symbol_to_scan, tf, candles, min_rrr=target_rrr)
                decision["track"] = track_name
                results.append(decision)
        return results, connection

    try:
        with st.spinner("Analyzing multi-timeframe charts live via API..."):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            scan_results, active_connection = loop.run_until_complete(fetch_and_scan_market())
            
            for res in scan_results:
                st.markdown(f"#### 🛰️ {res['track']} ({res.get('timeframe', 'N/A')})")
                if res["status"] == "APPROVED":
                    st.success(f"🎯 **Setup Found! {res['direction']} {res['symbol']}**")
                    st.write(f"Parameters: Entry: {res['entry']} | SL: {res['sl']} | TP: {res['tp']} | RRR: 1:{res['rrr']}")
                    
                    # One-tap mobile execution confirmation
                    if st.button(f"Deploy {res['style']} Order to Live MT5 Terminal", key=f"btn_{res['timeframe']}"):
                        async def deploy_trade():
                            if res['direction'] == "BUY":
                                return await active_connection.create_market_buy_order(res['symbol'], res['lots'], res['sl'], res['tp'])
                            else:
                                return await active_connection.create_market_sell_order(res['symbol'], res['lots'], res['sl'], res['tp'])
                        
                        loop.run_until_complete(deploy_trade())
                        st.balloons()
                        st.session_state.system_logs.append(f"Deployed {res['style']} {res['direction']} {res['lots']} lots.")
                else:
                    st.warning(f"Skipped: {res['reason']}")
                    
    except Exception as err:
        st.error(f"Scanner halted: {err}")
        remediation = st.session_state.doctor.diagnose_and_heal(traceback.format_exc(), "Live API stream crash handler.")
        st.text_area("Doctor Remediation Patch Advice", value=remediation)

st.text_area("Live Event Stream Log", value="\n".join(st.session_state.system_logs[::-1]))
