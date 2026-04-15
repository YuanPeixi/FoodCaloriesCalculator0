"""Pydantic data models for the Food Calories Calculator API."""

from __future__ import annotations

from pydantic import BaseModel


class FoodItem(BaseModel):
    """A single recognized food item with calorie information."""

    name: str
    calories_per_100g: float
    estimated_grams: float
    estimated_calories: float


class RecognitionResult(BaseModel):
    """Result from food recognition on a single photo."""

    foods: list[FoodItem]
    total_calories: float
    model_used: str
    description: str


class ComparisonResult(BaseModel):
    """Result from comparing before-meal and after-meal photos."""

    before_foods: list[FoodItem]
    after_foods: list[FoodItem]
    consumed_foods: list[FoodItem]
    total_consumed_calories: float
    model_used: str
    description: str
