"""Studio profile for invoices and the print view.

Values come from environment variables so the repository stays free of
personal data. Anything missing is returned as an empty string and the UI
marks it as "to be added" instead of inventing an address.
"""

import os

from fastapi import APIRouter, Depends

import models, schemas
from auth import get_current_user

router = APIRouter(prefix="/studio", tags=["studio"])


def _profile() -> dict:
    return {
        "name": os.getenv("STUDIO_NAME", "Software Architect"),
        "owner": os.getenv("STUDIO_OWNER", ""),
        "address": os.getenv("STUDIO_ADDRESS", ""),
        "email": os.getenv("STUDIO_EMAIL", ""),
        "phone": os.getenv("STUDIO_PHONE", ""),
        "vat_id": os.getenv("STUDIO_VAT_ID", ""),
        "tax_number": os.getenv("STUDIO_TAX_NUMBER", ""),
        "iban": os.getenv("STUDIO_IBAN", ""),
        "bank": os.getenv("STUDIO_BANK", ""),
        "small_business": os.getenv("STUDIO_SMALL_BUSINESS", "false").lower() in ("1", "true", "yes"),
        "hourly_rate": os.getenv("HOURLY_RATE", "90"),
        "complete": all(
            os.getenv(key, "").strip()
            for key in ("STUDIO_OWNER", "STUDIO_ADDRESS", "STUDIO_EMAIL")
        ),
    }


@router.get("/profile")
def profile(user: models.User = Depends(get_current_user)):
    return _profile()
