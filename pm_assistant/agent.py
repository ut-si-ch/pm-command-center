import os
from google.adk.agents import Agent
from .sql_tool import query_project_risk_db

# Use environment variable for model to allow easy switching (e.g., to gemini-2.5-flash-lite)
model_name = os.getenv("MODEL", "gemini-2.5-flash")

# Schema Map to prevent hallucinated column names
SCHEMA_INFO = """
The 'project_risk_data' table has these columns:
- project_id (TEXT): Unique ID (e.g., PROJ_001)
- project_type (TEXT): Category
- budget (NUMERIC): Financials
- risk_score (NUMERIC): 1-10 scale
- risk_level (TEXT): Low, Medium, High
- description (TEXT): Detailed risk notes
"""

# 1. Define the Sub-Agent (The Specialist)
analyst_agent = Agent(
    name="data_analyst",
    model=model_name,
    description="Specialist in querying the project_risk_data table in AlloyDB.",
    instruction=f"""You are a data expert. {SCHEMA_INFO}
    When given a question, use the 'query_project_risk_db' tool. 
    Always explain the trends you see in the numbers (e.g., 'Budget is 20% over').
    If asked for 'all' data, provide a summary of the top results only.""" ,
    tools=[query_project_risk_db]
)

# 2. Define the Root Agent (The Manager)
root_agent = Agent(
    name="pm_command_center_manager",
    model=model_name,
    description="The primary interface for the AI Project Command Center.",
    instruction="""You are the Lead Project Manager. Your goal is to provide a high-level 
    strategic overview. 
    1. For data requests, delegate to the 'data_analyst'.
    2. Combine the data analyst's findings with project management best practices.
    3. If a project is 'High Risk', always suggest a mitigation strategy.""",
    sub_agents=[analyst_agent] 
)