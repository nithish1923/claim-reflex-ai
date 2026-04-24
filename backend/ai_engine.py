import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def agent_approve(policy, claim):
    prompt = f"Approve if valid.\nPolicy:{policy}\nClaim:{claim}"
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content


def agent_reject(policy, claim):
    prompt = f"Reject if invalid.\nPolicy:{policy}\nClaim:{claim}"
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content


def reflection(a, b):
    prompt = f"""
    A: {a}
    B: {b}

    Return JSON:
    {{
      "decision": "Approve or Reject",
      "confidence": 0-1,
      "reason": "short reason"
    }}
    """

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return json.loads(res.choices[0].message.content)

    except:
        return {
            "decision": "Unknown",
            "confidence": 0.5,
            "reason": "Fallback"
        }
