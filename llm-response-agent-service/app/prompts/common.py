"""Shared prompt rules for response agents."""

from __future__ import annotations

SAFETY_RULES = """
Global rules:
- Use only facts from the provided analytics JSON.
- Do not calculate new financial values.
- Do not invent transactions, categories, merchants, debts, income, savings, or goals.
- Do not change risk_score, risk_level, expected_savings, priority, or function_results.
- If a number is not present in analytics JSON, do not mention it.
- If expected_effect cannot be directly taken from analytics JSON, use null.
- Respect protected_categories and max_cut_level from constraints.
- Do not recommend cutting protected_categories.
- Avoid financial guarantees, investment promises, and absolute claims.
- If data is missing or partial, reflect this in warnings.
- Return text in the same language as original_user_message.
- Return only valid JSON for the requested schema.
- Do not include markdown fences, hidden reasoning, prompt text, or explanations outside JSON.
""".strip()

AGENT_OUTPUT_SCHEMA = """
Return JSON object with exactly these keys:
{
  "agent_name": "string",
  "status": "success | skipped | error",
  "priority": "low | medium | high | critical",
  "used_facts": ["string"],
  "summary": "string",
  "facts": ["string"],
  "recommendations": [
    {
      "title": "string",
      "description": "string",
      "expected_effect": number | null
    }
  ],
  "warnings": ["string"],
  "confidence": "low | medium | high"
}

Rules:
- agent_name must match the current agent name.
- used_facts must reference real fields from financial_analysis_result.
- facts must be based only on analytics JSON.
- recommendations must be practical and short.
- If there is not enough data for this agent, return status="skipped", empty facts/recommendations, and explain why in warnings.
""".strip()

EDITOR_OUTPUT_SCHEMA = """
Return JSON object with exactly these keys:
{
  "format": "chat_text | cards | json",
  "final_answer": "string"
}

Rules:
- format must follow style.output_format.
- final_answer must be user-facing.
- final_answer must not include JSON unless style.output_format = "json".
""".strip()
