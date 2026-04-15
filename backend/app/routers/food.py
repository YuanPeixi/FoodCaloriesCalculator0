"""Food calorie recognition API router."""

from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from starlette.exceptions import HTTPException as StarletteHTTPException

from ..models import ComparisonResult, RecognitionResult
from ..services import local_model, openrouter

router = APIRouter(prefix="/api/food", tags=["food"])


@router.post("/recognize", response_model=RecognitionResult)
async def recognize_food(
    image: UploadFile = File(..., description="Food photo to analyze"),
    model: str = Form("openrouter", description="Model to use: 'openrouter' or 'local'"),
) -> RecognitionResult:
    """Recognize food items and estimate calories from a single photo."""
    contents = await image.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty image file")

    if model not in ("openrouter", "local"):
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model '{model}'. Use 'openrouter' or 'local'.",
        )

    try:
        if model == "openrouter":
            return await openrouter.recognize_single(contents)
        else:
            return await local_model.recognize_single(contents)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except StarletteHTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Recognition failed: {exc}")


@router.post("/compare", response_model=ComparisonResult)
async def compare_meals(
    before_image: UploadFile = File(..., description="Photo BEFORE eating"),
    after_image: UploadFile = File(..., description="Photo AFTER eating"),
    model: str = Form("openrouter", description="Model to use: 'openrouter' or 'local'"),
) -> ComparisonResult:
    """Compare before-meal and after-meal photos to calculate consumed calories.

    By comparing what was on the plate before and after eating, the system
    can more accurately determine the actual amount of food consumed.
    """
    before_bytes = await before_image.read()
    after_bytes = await after_image.read()

    if not before_bytes:
        raise HTTPException(status_code=400, detail="Empty before-meal image")
    if not after_bytes:
        raise HTTPException(status_code=400, detail="Empty after-meal image")

    if model not in ("openrouter", "local"):
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model '{model}'. Use 'openrouter' or 'local'.",
        )

    try:
        if model == "openrouter":
            return await openrouter.recognize_comparison(before_bytes, after_bytes)
        else:
            return await local_model.recognize_comparison(before_bytes, after_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except StarletteHTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {exc}")
