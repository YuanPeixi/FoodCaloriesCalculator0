"""OpenRouter multi-modal model integration service.

Uses models like Qwen2.5-VL or Qwen-VL-Plus via the OpenRouter API
to analyze food images and estimate calories.
"""

from __future__ import annotations

import base64
import json
import re

import httpx

from ..config import settings
from ..models import ComparisonResult, FoodItem, RecognitionResult

SINGLE_PHOTO_PROMPT = """You are a professional food nutrition analyst. Analyze this food image and identify each food item visible.

For each food item, provide:
1. Name of the food
2. Estimated calories per 100g
3. Estimated weight in grams
4. Estimated total calories for that item

Respond ONLY with a valid JSON object in this exact format (no markdown, no code fences):
{
  "foods": [
    {
      "name": "food name",
      "calories_per_100g": 100,
      "estimated_grams": 150,
      "estimated_calories": 150
    }
  ],
  "description": "Brief description of the meal"
}"""

COMPARISON_PROMPT = """You are a professional food nutrition analyst. You are given two images:
- Image 1: Food BEFORE eating (the full meal)
- Image 2: Food AFTER eating (what remains)

By comparing these two images, determine what was actually consumed.

For each food category, provide:
1. Name of the food
2. Estimated calories per 100g
3. Estimated weight in grams
4. Estimated total calories

Respond ONLY with a valid JSON object in this exact format (no markdown, no code fences):
{
  "before_foods": [
    {"name": "food name", "calories_per_100g": 100, "estimated_grams": 200, "estimated_calories": 200}
  ],
  "after_foods": [
    {"name": "food name", "calories_per_100g": 100, "estimated_grams": 50, "estimated_calories": 50}
  ],
  "consumed_foods": [
    {"name": "food name", "calories_per_100g": 100, "estimated_grams": 150, "estimated_calories": 150}
  ],
  "description": "Brief description of what was consumed"
}"""

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


def _encode_image(image_bytes: bytes) -> str:
    """Encode image bytes to base64 string."""
    return base64.b64encode(image_bytes).decode("utf-8")


def _extract_json(text: str) -> str:
    """Extract JSON from text, handling markdown code fences."""
    # Try to find JSON in code fences first
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Try to find raw JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0).strip()
    return text.strip()


async def recognize_single(image_bytes: bytes) -> RecognitionResult:
    """Recognize food items from a single photo using OpenRouter API."""
    if not settings.openrouter_api_key:
        raise ValueError(
            "OpenRouter API key is not configured. "
            "Set OPENROUTER_API_KEY in your .env file."
        )

    b64_image = _encode_image(image_bytes)

    payload = {
        "model": settings.openrouter_model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": SINGLE_PHOTO_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64_image}"
                        },
                    },
                ],
            }
        ],
        "max_tokens": 1024,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            OPENROUTER_API_URL,
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()

    data = response.json()
    content = data["choices"][0]["message"]["content"]
    result = json.loads(_extract_json(content))

    foods = [FoodItem(**f) for f in result["foods"]]
    total = sum(f.estimated_calories for f in foods)

    return RecognitionResult(
        foods=foods,
        total_calories=total,
        model_used=settings.openrouter_model,
        description=result.get("description", ""),
    )


async def recognize_comparison(
    before_bytes: bytes, after_bytes: bytes
) -> ComparisonResult:
    """Compare before/after meal photos using OpenRouter API."""
    if not settings.openrouter_api_key:
        raise ValueError(
            "OpenRouter API key is not configured. "
            "Set OPENROUTER_API_KEY in your .env file."
        )

    b64_before = _encode_image(before_bytes)
    b64_after = _encode_image(after_bytes)

    payload = {
        "model": settings.openrouter_model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": COMPARISON_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64_before}"
                        },
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64_after}"
                        },
                    },
                ],
            }
        ],
        "max_tokens": 2048,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            OPENROUTER_API_URL,
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()

    data = response.json()
    content = data["choices"][0]["message"]["content"]
    result = json.loads(_extract_json(content))

    before_foods = [FoodItem(**f) for f in result["before_foods"]]
    after_foods = [FoodItem(**f) for f in result["after_foods"]]
    consumed_foods = [FoodItem(**f) for f in result["consumed_foods"]]
    total = sum(f.estimated_calories for f in consumed_foods)

    return ComparisonResult(
        before_foods=before_foods,
        after_foods=after_foods,
        consumed_foods=consumed_foods,
        total_consumed_calories=total,
        model_used=settings.openrouter_model,
        description=result.get("description", ""),
    )
