import os
import math
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

class ProfitableTraderAgent:
    def __init__(self, account_balance=10000, risk_pct=0.01):
        self.balance = float(account_balance)
        self.risk_pct = float(risk_pct)
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
        self.vector_db = None

    def absorb_pdf_strategy(self, file_path):
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()
        embeddings = OpenAIEmbeddings()
        self.vector_db = Chroma.from_documents(pages, embeddings)
        return f"📚 Knowledge Base Loaded: {os.path.basename(file_path)}"

    def calculate_technical_indicators(self, candles):
        """
        Processes raw candle data mathematically to derive key technical states.
        """
        closes = [float(c['close']) for c in candles]
        highs = [float(c['high']) for c in candles]
        lows = [float(c['low']) for c in candles]
        
        if len(closes) < 20:
            return {"trend": "NEUTRAL", "momentum": 50, "volatility": "LOW"}
            
        # Fast Moving Average (8-period) vs Slow Moving Average (20-period)
        ma_fast = sum(closes[-8:]) / 8
        ma_slow = sum(closes[-20:]) / 20
        trend = "BULLISH" if ma_fast > ma_slow else "BEARISH"
        
        # Simple Momentum Calculation (RSI approximation)
        gains = []
        losses = []
        for i in range(1, len(closes[-14:])):
            diff = closes[-14:][i] - closes[-14:][i-1]
            if diff > 0:
                gains.append(diff)
            else:
                losses.append(abs(diff))
        
        avg_gain = sum(gains)/14 if gains else 0
        avg_loss = sum(losses)/14 if losses else 0
        rs = avg_gain / avg_loss if avg_loss != 0 else 1
        rsi = 100 - (100 / (1 + rs))
        
        return {"trend": trend, "rsi": rsi, "current_price": closes[-1]}

    def automatic_market_scanner(self, symbol, timeframe, candles, min_rrr=6.0):
        """
        Scans current market conditions across multiple timeframes automatically.
        Calculates exact Entry, Stop Loss, and Take Profit based on trade classifications.
        """
        tech = self.calculate_technical_indicators(candles)
        current_price = tech["current_price"]
        
        # Define trade categories based on timeframe input
        if timeframe in ["M1", "M5"]:
            style = "SCALPING"
            sl_pips = 0.00050  # Tight 5 pip stop loss
            target_rrr = 2.5   # Scalping uses higher frequency, lower RRR targets
        elif timeframe in ["M15", "H1"]:
            style = "SHORT-TERM"
            sl_pips = 0.00150  # 15 pip day trading stop
            target_rrr = max(4.0, min_rrr)
        else:
            style = "LONG-TERM"
            sl_pips = 0.00400  # 40 pip macro swing trade stop
            target_rrr = max(6.0, min_rrr)

        # Apply technical logic based on detected trend
        if tech["trend"] == "BULLISH" and tech["rsi"] < 65:
            direction = "BUY"
            entry = current_price
            sl = entry - sl_pips
            tp = entry + (sl_pips * target_rrr)
        elif tech["trend"] == "BEARISH" and tech["rsi"] > 35:
            direction = "SELL"
            entry = current_price
            sl = entry + sl_pips
            tp = entry - (sl_pips * target_rrr)
        else:
            return {"status": "SKIPPED", "reason": f"Market consolidations on {timeframe}. Indicators flat."}

        # Cross-reference with your uploaded strategy PDF manual if available
        if self.vector_db:
            context = self.vector_db.similarity_search(f"Validate a {direction} setup on {timeframe} trend conditions", k=2)
            # AI reads the document context silently to approve or alter targets
            ai_opinion = self.llm.predict(f"Based on strategy text: {context}\nIs a {direction} order at {entry} structurally sound? Reply 'VALID' or 'INVALID'")
            if "INVALID" in ai_opinion:
                return {"status": "SKIPPED", "reason": "Filtered by custom PDF strategy rules."}

        # Math logic to calculate proper safety lot sizing
        risk_dist = abs(entry - sl)
        risk_capital = self.balance * self.risk_pct
        pips_at_risk = risk_dist * 10000
        calculated_lots = round(risk_capital / (pips_at_risk * 10.0), 2)
        lots = max(0.01, calculated_lots)

        return {
            "status": "APPROVED",
            "style": style,
            "direction": direction,
            "symbol": symbol,
            "timeframe": timeframe,
            "lots": lots,
            "entry": round(entry, 5),
            "sl": round(sl, 5),
            "tp": round(tp, 5),
            "rrr": target_rrr
        }

class DoctorSystemAgent:
    def __init__(self):
        self.diagnostic_brain = ChatOpenAI(model="gpt-4o", temperature=0.1)

    def diagnose_and_heal(self, stack_trace, broken_logic_block):
        prompt = f"System Error occurred inside multi-timeframe engine.\nTrace: {stack_trace}\nContext: {broken_logic_block}"
        return self.diagnostic_brain.predict(prompt)
