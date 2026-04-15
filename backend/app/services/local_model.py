"""Local (self-trained) model integration service.

This module provides a placeholder for a self-trained food recognition model.
See docs/model_training.md for details on dataset acquisition, training, and
integration.

When no local model is available, this service returns a helpful error message
directing users to either configure OpenRouter or train a local model.
"""

from __future__ import annotations

from ..models import ComparisonResult, FoodItem, RecognitionResult

# ---------------------------------------------------------------------------
# Built-in food calorie reference table (used as fallback / demo mode)
# ---------------------------------------------------------------------------
FOOD_CALORIE_DB: dict[str, float] = {
    "rice": 130,
    "white rice": 130,
    "fried rice": 186,
    "noodles": 138,
    "bread": 265,
    "chicken breast": 165,
    "chicken": 239,
    "beef": 250,
    "pork": 242,
    "fish": 206,
    "salmon": 208,
    "shrimp": 99,
    "egg": 155,
    "fried egg": 196,
    "tofu": 76,
    "broccoli": 34,
    "carrot": 41,
    "tomato": 18,
    "potato": 77,
    "french fries": 312,
    "salad": 20,
    "apple": 52,
    "banana": 89,
    "orange": 47,
    "pizza": 266,
    "hamburger": 295,
    "sandwich": 252,
    "sushi": 143,
    "dumpling": 229,
    "steak": 271,
    "soup": 36,
    "milk": 42,
    "yogurt": 59,
    "cheese": 402,
    "cake": 257,
    "cookie": 502,
    "ice cream": 207,
    "chocolate": 546,
}


async def recognize_single(image_bytes: bytes) -> RecognitionResult:
    """Recognize food from a single photo using the local model.

    Currently returns a demo result since no trained model is loaded.
    Replace this implementation with actual model inference when a
    trained model is available.
    """
    # In a real implementation, this would:
    # 1. Preprocess the image (resize, normalize)
    # 2. Run inference through the trained model
    # 3. Map predictions to food items with calorie estimates
    #
    # For now, return a demo result to show the expected format.
    demo_foods = [
        FoodItem(
            name="(Demo) Rice",
            calories_per_100g=130,
            estimated_grams=200,
            estimated_calories=260,
        ),
        FoodItem(
            name="(Demo) Chicken",
            calories_per_100g=239,
            estimated_grams=150,
            estimated_calories=358.5,
        ),
    ]

    return RecognitionResult(
        foods=demo_foods,
        total_calories=sum(f.estimated_calories for f in demo_foods),
        model_used="local-demo",
        description=(
            "Demo result — no trained local model is loaded. "
            "See docs/model_training.md to learn how to train and "
            "integrate your own model, or use the OpenRouter model instead."
        ),
    )


async def recognize_comparison(
    before_bytes: bytes, after_bytes: bytes
) -> ComparisonResult:
    """Compare before/after meal photos using the local model.

    Currently returns a demo result since no trained model is loaded.
    """
    before_foods = [
        FoodItem(
            name="(Demo) Rice",
            calories_per_100g=130,
            estimated_grams=200,
            estimated_calories=260,
        ),
        FoodItem(
            name="(Demo) Chicken",
            calories_per_100g=239,
            estimated_grams=150,
            estimated_calories=358.5,
        ),
    ]

    after_foods = [
        FoodItem(
            name="(Demo) Rice",
            calories_per_100g=130,
            estimated_grams=50,
            estimated_calories=65,
        ),
        FoodItem(
            name="(Demo) Chicken",
            calories_per_100g=239,
            estimated_grams=20,
            estimated_calories=47.8,
        ),
    ]

    consumed_foods = [
        FoodItem(
            name="(Demo) Rice",
            calories_per_100g=130,
            estimated_grams=150,
            estimated_calories=195,
        ),
        FoodItem(
            name="(Demo) Chicken",
            calories_per_100g=239,
            estimated_grams=130,
            estimated_calories=310.7,
        ),
    ]

    return ComparisonResult(
        before_foods=before_foods,
        after_foods=after_foods,
        consumed_foods=consumed_foods,
        total_consumed_calories=sum(f.estimated_calories for f in consumed_foods),
        model_used="local-demo",
        description=(
            "Demo result — no trained local model is loaded. "
            "See docs/model_training.md to learn how to train and "
            "integrate your own model, or use the OpenRouter model instead."
        ),
    )
