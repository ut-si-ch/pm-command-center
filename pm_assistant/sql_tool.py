import psycopg2
import os
from dotenv import load_dotenv
from decimal import Decimal
from psycopg2.extras import RealDictCursor

load_dotenv()

def query_project_risk_db(sql_query: str):
    """
    Executes a SQL query against the project_risk_data table.
    Safety: Automatically applies LIMIT 20 if not specified.
    """
    db_host = os.getenv("DB_HOST")
    db_pass = os.getenv("DB_PASS")
    
    # 1. Safety Limit Injection
    if "LIMIT" not in sql_query.upper():
        sql_query = sql_query.strip().rstrip(';') + " LIMIT 20;"

    try:
        conn = psycopg2.connect(
            host=db_host,
            database="postgres",
            user="postgres",
            password=db_pass
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql_query)
        results = cur.fetchall()
        
        # 2. Decimal to Float Conversion
        clean_results = []
        for row in results:
            clean_row = {k: (float(v) if isinstance(v, Decimal) else v) for k, v in row.items()}
            clean_results.append(clean_row)
        
        cur.close()
        conn.close()
        return clean_results
    except Exception as e:
        return f"Database error: {str(e)}"