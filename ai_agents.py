import os
import math
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

class MultiPairNeuralBrain:
    def __init__(self, account_balance=10000, risk_pct=0.01):
        self.balance = float(account_balance)
        self.risk_pct = float(risk_pct)
        self.cognitive_llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
        self.vector_db = None

    def learn_from_textbook(self, file_path):
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()
        embeddings = OpenAIEmbeddings()
        self.vector_db = Chroma.from_documents(pages, embeddings)
        return f"🧠 Cognitive Core initialized with knowledge from: {os.path.basename(file_path)}"

    def perceive_market_state(self, candles):
        """
        Translates raw data arrays into qualitative market trend structures.
        """
        closes = [float(c['close']) for c in candles]
        if len(closes) < 20:
            return "Consolidating Range"
            
        ma_fast = sum(closes[-8:]) / 8
        ma_slow = sum(closes[-20:]) / 20
        
        if ma_fast > ma_slow:
            return "Structural Bullish Expansion"
        elif ma_fast < ma_slow:
            return "Structural Bearish Distribution"
        return "Compression Range"

    def executive_reasoning(self, symbol, timeframe, candles, user_min_rrr):
        """
        Synthesizes perception with book memories to classify and calculate trades.
        """
        current_price = float(candles[-1]['close'])
        market_perception = self.perceive_market_state(candles)
        
        # Determine Trade Style profile based on structural attention window
        if timeframe in ["M1", "M5"]:
            style = "QUICK SCALP"
            sl_pips = 6.0  
            runtime_rrr = 2.5 # Scalps target rapid compounding exits
        elif timeframe in ["M15", "H1"]:
            style = "SHORT-TERM"
            sl_pips = 18.0
            runtime_rrr = max(4.0, user_min_rrr)
        else:
            style = "MACRO SWING"
            sl_pips = 45.0
            runtime_rrr = max(6.0, user_min_rrr)

        book_context = ""
        if self.vector_db:
            search_query = f"Trading parameters for {symbol} during {market_perception}"
            docs = self.vector_db.similarity_search(search_query, k=1)
            book_context = docs[0].page_content

        cognitive_prompt = f"""
        You are an advanced trading consciousness operating across the major FX matrix.
        
        [Asset Context]
        Pair Identity: {symbol}
        Trade Profile Category: {style} (Timeframe: {timeframe})
        Current Live Rate: {current_price}
        Perceived Trend Structure: {market_perception}
        Target Risk-to-Reward Ratio: 1:{runtime_rrr}
        
        [Learned Book Guidance]
        {book_context if book_context else "No custom strategy uploaded yet. Rely on baseline institutional liquidity guidelines."}
        
        Review this structure logically. If the pattern aligns with your knowledge, issue an order.
        You must output your internal thoughts first, then complete the analysis with this exact line:
        DECISION_STREAM | STATUS: APPROVED | DIRECTION: [BUY or SELL] | SL_PIPS: {sl_pips} | RRR: {runtime_rrr}
        
        If it is choppy, unaligned, or dangerous, close with:
        DECISION_STREAM | STATUS: HOLD | DIRECTION: NONE | SL_PIPS: 0 | RRR: 0
        """
        
        thought_stream = self.cognitive_llm.predict(cognitive_prompt)
        
        decision_line = [line for line in thought_stream.split("\n") if "DECISION_STREAM" in line]
        if not decision_line:
            return {"status": "HOLD", "analysis": thought_stream, "reason": "Cognitive fragmentation."}
            
        parts = decision_line[0].split(" | ")
        status = parts[1].split(": ")[1]
        direction = parts[2].split(": ")[1]
        
        if status == "HOLD":
            return {"status": "HOLD", "analysis": thought_stream}

        # Mathematical Price Engineering
        pip_multiplier = 0.00010 if "JPY" not in symbol else 0.01
        sl_distance = sl_pips * pip_multiplier
        
        if direction == "BUY":
            sl = current_price - sl_distance
            tp = current_price + (sl_distance * runtime_rrr)
        else:
            sl = current_price + sl_distance
            tp = current_price - (sl_distance * runtime_rrr)

        # Safety lot sizing calculation matching account equity allocations
        risk_capital = self.balance * self.risk_pct
        calculated_lots = round(risk_capital / (sl_pips * 10.0), 2)
        lots = max(0.01, calculated_lots)

        return {
            "status": "APPROVED",
            "analysis": thought_stream,
            "style": style,
            "direction": direction,
            "symbol": symbol,
            "timeframe": timeframe,
            "lots": lots,
            "entry": round(current_price, 5),
            "sl": round(sl, 5),
            "tp": round(tp, 5),
            "rrr": runtime_rrr
        }
