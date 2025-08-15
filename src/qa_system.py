import os
from openai import OpenAI
from typing import List

# Use the same client setup as in the extractor
LLM_API_KEY = os.environ.get("LLM_API_KEY", "sk-af3e7e69cc3848669167549d79318d94")
LLM_API_BASE_URL = os.environ.get("LLM_API_BASE_URL", "https://api.deepseek.com")

client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_API_BASE_URL)

def get_recommendation(station: str, flow: float, level: float, rules: List[str]) -> str:
    """
    Uses an LLM to get a dispatch recommendation based on conditions and a list of rules.
    """
    if not rules:
        return "No dispatch rules found for this station in the knowledge graph."

    # Construct the prompt for the LLM
    prompt = f"""
    You are an expert hydropower dispatch engineer. Your task is to provide a clear and concise recommendation for operating a hydropower station based on the current conditions and a list of available operational rules.

    **Current Conditions:**
    - Hydropower Station: {station}
    - Inflow/Flow: {flow} m³/s
    - Water Level: {level} m

    **Available Operational Rules:**
    Please analyze the following rules extracted from the knowledge base:
    ---
    {chr(10).join(f"- {rule}" for rule in rules)}
    ---

    **Your Task:**
    1.  Carefully evaluate the current conditions against the available rules.
    2.  Identify the most applicable rule or set of rules.
    3.  Provide a direct recommendation on what action to take.
    4.  If no rule seems to apply, state that and explain why.
    5.  Your response should be direct, actionable, and easy for an operator to understand.

    **Recommendation:**
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are an expert hydropower dispatch engineer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2, # Lower temperature for more deterministic, factual answers
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling LLM API: {e}")
        return "Error: Could not get a recommendation from the AI model."
