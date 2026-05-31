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
        """Ingests user PDFs, maps knowledge tokens, and extracts key metrics."""
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()
        embeddings = OpenAIEmbeddings()
        self.vector_db = Chroma.from_documents(pages, embeddings)
        return f"Assimilated strategy parameters from: {os.path.basename(file_path)}"

    def evaluate_15m_setup(self, symbol, matrix_data):
        """Enforces 5-Point Confluence Checks and strict 1:2 RRR verification."""
        entry = float(matrix_data['entry'])
        sl = float(matrix_data['sl'])
        tp = float(matrix_data['tp'])

        # Risk-to-Reward Ratio Validation
        risk_dist = abs(entry - sl)
        reward_dist = abs(tp - entry)
        
        if risk_dist == 0:
            raise ZeroDivisionError("Structural Invalidity: Entry price cannot match Stop Loss level.")
            
        rrr = reward_dist / risk_dist
        if rrr < 2.0:
            return {"status": "REJECTED", "reason": f"Insufficient Risk-Reward Ratio (1:{round(rrr, 2)}). Must be >= 1:2."}

        # Calculate Lot Size based on precise risk parameters
        risk_capital = self.balance * self.risk_pct
        pips_at_risk = risk_dist * 10000  # Multiplier calibrated for major currency pairs
        pip_value_constant = 10.0
        calculated_lots = round(risk_capital / (pips_at_risk * pip_value_constant), 2)
        lots = max(0.01, calculated_lots)

        # Enforce Confluence Checklist Scoring Engine
        score = sum([
            matrix_data.get('trend_4h', False),
            matrix_data.get('sr_zone', False),
            matrix_data.get('candle_trigger', False),
            matrix_data.get('pdf_indicator', False),
            matrix_data.get('clean_runway', False)
        ])

        if score < 4:
            return {"status": "REJECTED", "reason": f"Low Confluence Score ({score}/5). Minimum 4/5 required."}

        return {
            "status": "APPROVED",
            "symbol": symbol,
            "lots": lots,
            "entry": entry,
            "sl": sl,
            "tp": tp,
            "score": f"{score}/5"
        }

class DoctorSystemAgent:
    def __init__(self):
        self.diagnostic_brain = ChatOpenAI(model="gpt-4o", temperature=0.1)

    def diagnose_and_heal(self, stack_trace, broken_logic_block):
        """Intercepts system crashes, optimizes error context, and generates software patches."""
        prompt = f"""
        You are the system Doctor Agent running inside a 24/7 trading cluster.
        A sub-module crash was encountered. Analyze the parameters below to determine the cause:
        
        [STACK TRACE ERROR]
        {stack_trace}
        
        [CRITICAL CODE SEGMENT]
        {broken_logic_block}
        
        Generate a concise 'KNOWLEDGE ASSIMILATION & PATCH REPORT'.
        State the operational cause of the failure, confirm how the logic is now adapted, 
        and provide an explicit structural rule to overwrite the error and preserve runtime uptime.
        """
        return self.diagnostic_brain.predict(prompt)