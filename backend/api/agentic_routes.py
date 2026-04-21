from fastapi import APIRouter
from pydantic import BaseModel
import sqlite3
import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
from database.db_config import DB_PATH

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

# Global session dictionary to hold context (in production use real sessions)
active_chats = {}

def get_db_schema():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        schema_str = ""
        for table in ['products', 'sales']:
            cursor.execute(f"PRAGMA table_info({table})")
            cols = [f"{r[1]} ({r[2]})" for r in cursor.fetchall()]
            schema_str += f"Table: {table}\nColumns: {', '.join(cols)}\n\n"
        conn.close()
        return schema_str
    except Exception:
        return "Table schemas unavailable."

def execute_query(query: str):
    if not query:
        return []
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query)
        res = cursor.fetchall()
        conn.close()
        return res
    except Exception as e:
        raise Exception(f"SQL Execution Error: {str(e)}")

def init_chat_session():
    schema = get_db_schema()
    system_instruction = f"""
    You are an intelligent data-analyst database agent.
    Your task is to convert the user's natural language questions into accurate SQL queries that will execute against a SQLite database to render explicit visualizations and answers.
    
    Current Database Schema:
    {schema}
    
    Rules for SQL Generation:
    1. For charts, your SQL query MUST return exactly TWO columns: a descriptive string label first (e.g. product_name, date, category), and a numerical metric second (e.g. SUM(sales_quantity)).
    2. Group By and Order By clauses should be used appropriately. Limit records if plotting many items so charts don't get cluttered (e.g., LIMIT 15 for top products).
    3. If the user asks a simple question requiring a single scalar number (e.g., "Total sales in electronics"), select just that scalar value.
    4. DATE FORMAT: The database dates are universally formatted as 'YYYY-MM-DD'. Always parse natural language dates or localized dates into 'YYYY-MM-DD' before querying.
    5. JOINS: If the user filters 'sales' (or demand) by a 'category' or 'product_name', you MUST explicitly JOIN the sales table and the products table ON product_id!
    6. AGGREGATES FOR CHARTS: If the user asks to generate a graph or chart, NEVER just return a single sum value! Even if they filter for a single date or category, you MUST `GROUP BY` product_name, category, or date to provide an array of multiple data points so the chart can physically be drawn.

    Output Rules:
    You MUST output incredibly strict, valid JSON ONLY. DO NOT wrap the output in markdown block like ```json ... ```. Output raw JSON object.
    
    JSON Format to strictly adhere to:
    {{
        "sql": "SELECT ...", // Provide valid SQL, or null if absolutely no query is possible.
        "chart_type": "bar", // Options: "line", "bar", "pie", "scatter", or "text" (if no chart is needed, just a scalar number).
        "text_reply": "A concise, conversational insight explaining the data or answering the question."
    }}
    """
    
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=system_instruction,
        generation_config={"response_mime_type": "application/json"}
    )
    return model.start_chat(history=[])

@router.post("/chat")
def chat_agent(req: ChatRequest):
    if not API_KEY:
        return {"reply": "LLM API Key missing in backend environment.", "action": "text", "data": None}
        
    try:
        # Initialize or fetch memory context
        if "default" not in active_chats:
            active_chats["default"] = init_chat_session()
            
        chat_session = active_chats["default"]
        
        # 1. Send Query to Gemini (Context Aware)
        response = chat_session.send_message(req.message)
        response_text = response.text.strip()
        
        # Strip potential markdown formatting if Gemini disobeys raw json rule
        if response_text.startswith("```json"):
            response_text = response_text[7:-3]
        elif response_text.startswith("```"):
            response_text = response_text[3:-3]
            
        llm_output = json.loads(response_text)
        
        sql_query = llm_output.get("sql")
        chart_type = llm_output.get("chart_type", "text")
        text_reply = llm_output.get("text_reply", "Processed your query.")
        
        # 2. Execute Extrapolated Database Query
        data = None
        if sql_query:
            raw_data = execute_query(sql_query)
            
            if chart_type in ["bar", "pie", "line", "scatter"]:
                # Map tuple matrix to rendering object
                data = [{"name": str(row[0]), "value": row[1] if row[1] is not None else 0} for row in raw_data]
            else:
                # Format a scalar value directly into the reply if chart_type is text
                if raw_data:
                    val = raw_data[0][0]
                    val = val if val is not None else 0 # Catch Null sums!
                    text_reply += f" \n**(Result: {val:,})**" if isinstance(val, (int, float)) else f" \n**(Result: {val})**"

        action_type = "render_chart" if data else "text"
        if not data and chart_type != "text":
            text_reply += " However, no underlying data segments were found mapping to this condition."
            action_type = "text"

        return {
            "reply": text_reply,
            "action": action_type,
            "chart_type": chart_type,
            "data": data,
            "sql_debug": sql_query # Provided for optional transparency
        }
        
    except json.JSONDecodeError:
        return {"reply": "Agent failed to construct valid analytical routing. Please rephrase.", "action": "text", "data": None}
    except Exception as e:
        return {"reply": f"Agent Encountered DB routing error: {str(e)}", "action": "text", "data": None}
