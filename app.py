import streamlit as st
import os
import asyncio
import traceback
from dotenv import load_dotenv
from ai_agents import MultiPairNeuralBrain
from metaapi_cloud_sdk import MetaApi

load_dotenv()
st.set_page_config(page_title="Major Pairs Neural Matrix", layout="wide")

if "brain" not in st.session_state:
    st.session_state.brain = MultiPairNeuralBrain(account_balance=10000, risk_pct=0.01)
if "live_logs" not in st.session_state:
    st.session_state.live_logs = ["👁️ Fully Automated Core Online. Standing by to scan Major Networks."]

st.title("⚡ Multi-Pair Automated Consciousness Console")

# Layout configurations
col_ctrl, col_kb = st.columns([1, 1])

with col_ctrl:
    st.markdown("### ⚙️ Risk Matrix Core")
    balance_input = st.number_input("Trading Capital Base ($)", value=st.session_state.brain.balance)
    st.session_state.brain.balance = balance_input
    user_rrr = st.slider("Target Minimum Swing RRR (1:X)", min_value=3.0, max_value=12.0, value=6.0, step=0.5)

with col_kb:
    st.markdown("### 📚 Cognitive Textbook Integration")
    uploaded_file = st.file_uploader("Drop Strategy Books/PDF Text here", type=["pdf"])
    if uploaded_file:
        with open(f"temp_{uploaded_file.name}", "wb") as f:
            f.write(uploaded_file.getbuffer())
        with st.spinner("Processing deep semantic map..."):
            msg = st.session_state.brain.learn_from_textbook(f"temp_{uploaded_file.name}")
            st.success(msg)
        os.remove(f"temp_{uploaded_file.name}")

st.write("---")

if st.button("🛰️ Scan 4 Major Best Pairs Automatically (All Timeframes)", use_container_width=True):
    async def run_matrix_scan():
        api = MetaApi(token=os.getenv("BROKER_GATEWAY_TOKEN"))
        account = await api.metatrader_account_api.get_account(account_id=os.getenv("BROKER_ACCOUNT_ID"))
        connection = account.get_rpc_connection()
        await connection.connect()
        await connection.wait_synchronized()
        
        # The 4 Best Major Pairs
        majors = ["EURUSD", "GBPUSD", "AUDUSD", "USDCAD"]
        # Multi-Track Scanning Framework: M5 captures Quick Scalps, H4 captures Macro Swings
        timeframes = [("M5", "Quick Scalp Track"), ("H4", "Macro Swing Track")]
        
        scan_reports = []
        for symbol in majors:
            for tf, label in timeframes:
                try:
                    candles = await connection.get_candles(symbol, tf, 25)
                    if candles:
                        decision = await asyncio.to_thread(
                            st.session_state.brain.executive_reasoning, 
                            symbol, tf, candles, user_rrr
                        )
                        decision["track_label"] = f"{symbol} - {label} ({tf})"
                        scan_reports.append(decision)
                except Exception as e:
                    pass
        return scan_reports, connection

    try:
        with st.spinner("Running deep algorithmic analysis across 4 Major Pairs live..."):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            reports, active_connection = loop.run_until_complete(run_matrix_scan())
            
            # Group into clean grid layout arrays on your Android screen
            st.markdown("### 🛰️ Live Brain Analysis Feedback Matrix")
            
            for rep in reports:
                with st.expander(f"📊 {rep['track_label']} ── Status: {rep['status']}", expanded=(rep['status'] == "APPROVED")):
                    st.markdown("**Agent Deliberation Thoughts:**")
                    st.info(rep["analysis"])
                    
                    if rep["status"] == "APPROVED":
                        st.success(f"🎯 **Trade Signal Generated: {rep['direction']} {rep['symbol']}**")
                        st.write(f"Lots: {rep['lots']} | Entry: {rep['entry']} | SL: {rep['sl']} | TP: {rep['tp']} | RRR: 1:{rep['rrr']}")
                        
                        # Direct placement confirmation mapping unique keys
                        if st.button(f"Deploy Trade for {rep['symbol']} ({rep['style']})", key=f"btn_{rep['symbol']}_{rep['timeframe']}"):
                            async def execute_trade():
                                if rep['direction'] == "BUY":
                                    return await active_connection.create_market_buy_order(rep['symbol'], rep['lots'], rep['sl'], rep['tp'])
                                else:
                                    return await active_connection.create_market_sell_order(rep['symbol'], rep['lots'], rep['sl'], rep['tp'])
                            loop.run_until_complete(execute_trade())
                            st.balloons()
                            st.session_state.live_logs.append(f"Successfully Filled {rep['style']} {rep['direction']} on {rep['symbol']}")
                            
    except Exception as matrix_err:
        st.error(f"Matrix runtime exception occurred: {matrix_err}")

st.write("---")
st.markdown("### 💾 Core Memory Log")
st.text_area("Event Loop Memory Output", value="\n".join(st.session_state.live_logs[::-1]), height=150)
