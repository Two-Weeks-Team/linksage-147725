import os
import json
import re
from typing import Any, Dict, List, Union
import httpx

_INFERENCE_URL = "https://inference.do-ai.run/v1/chat/completions"
_INFERENCE_KEY = os.getenv("DIGITALOCEAN_INFERENCE_KEY")
_MODEL = os.getenv("DO_INFERENCE_MODEL", "openai-gpt-oss-120b")

def _extract_json(text: str) -> str:
    """Extract JSON (or JSON code‑block) from a raw LLM response."""
    m = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?\s*```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()

def _coerce_unstructured_payload(raw_text: str) -> Dict[str, Any]:
    compact = raw_text.strip()
    tags = [part.strip(" -•\t") for part in re.split(r",|\\n", compact) if part.strip(" -•\t")]
    return {
        "note": "Model returned plain text instead of JSON",
        "raw": compact,
        "text": compact,
        "summary": compact,
        "tags": tags[:6],
    }


async def _call_inference(messages: List[Dict[str, str]], max_tokens: int = 512) -> Dict[str, Any]:
    """Core helper – makes the HTTP call, extracts JSON, and handles errors.
    Returns a dict; on error returns {'note': <reason>}.
    """
    headers = {
        "Authorization": f"Bearer {_INFERENCE_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": _MODEL,
        "messages": messages,
        "max_completion_tokens": max_tokens,
    }
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(_INFERENCE_URL, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            # Extract the content from the first choice
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            # Try to pull out a JSON block – many LLMs wrap the answer in markdown
            json_str = _extract_json(content)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                # Not JSON – return raw text under a generic key
                return {"summary": content.strip()}
    except Exception as exc:
        # Any failure falls back to a friendly note
        return {"note": f"AI service temporarily unavailable: {str(exc)}"}

# ---------------------------------------------------------------------------
# Public helpers used by route handlers
# ---------------------------------------------------------------------------
async def summarize_text(text: str) -> Dict[str, Any]:
    """Ask the model to produce a concise summary of *text*.
    Returns a dict that usually contains a ``summary`` key.
    """
    prompt = (
        "You are an expert summarizer. Produce a concise, factual summary of the following content.\n\n"
        f"Content:\n{text}\n\nSummary:"  
    )
    messages = [{"role": "user", "content": prompt}]
    return await _call_inference(messages, max_tokens=512)

async def generate_tags(text: str) -> Union[Dict[str, Any], List[str]]:
    """Ask the model for a JSON list of relevant tags for *text*.
    The model is encouraged to respond with a JSON array like ["tag1", "tag2"].
    """
    prompt = (
        "Extract up to 5 short, lowercase tags that best describe the following content. "
        "Return the tags as a JSON array.\n\n"
        f"Content:\n{text}\n\nTags:" 
    )
    messages = [{"role": "user", "content": prompt}]
    return await _call_inference(messages, max_tokens=256)
