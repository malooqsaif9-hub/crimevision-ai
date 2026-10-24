from __future__ import annotations

import os
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("CRIMEVISION_API_URL", "").strip().rstrip("/")


class ApiClientError(RuntimeError):
    """An API request failed or returned an unsuccessful response."""


def request_api(method: str, path: str, **kwargs: Any) -> httpx.Response:
    if not API_BASE_URL:
        raise ApiClientError(
            "CrimeVision API URL is not configured. "
            "Set CRIMEVISION_API_URL to your deployed FastAPI backend URL."
        )

    try:
        response = httpx.request(
            method,
            f"{API_BASE_URL}{path}",
            timeout=180.0,
            **kwargs,
        )
    except httpx.HTTPError as exc:
        raise ApiClientError(
            f"Could not reach the CrimeVision API at {API_BASE_URL}: {exc}"
        ) from exc

    if response.is_error:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text

        raise ApiClientError(
            f"API returned {response.status_code}: {detail}"
        )

    return response


def get_json(path: str) -> Any:
    return request_api("GET", path).json()


def post_json(path: str, **kwargs: Any) -> Any:
    return request_api("POST", path, **kwargs).json()


def list_cases() -> list[dict]:
    cases = get_json("/cases")
    return cases if isinstance(cases, list) else []


def case_label(case: dict) -> str:
    return f"{case['title']} ({case['case_id']})"
