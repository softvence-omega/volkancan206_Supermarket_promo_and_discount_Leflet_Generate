import os
import uuid
import requests
from fastapi import APIRouter
from typing import List
from app.schemas.Campaign_Info import CampaignRequest
from app.config import PRODUCT_UPLOAD_DIR, LOGO_UPLOAD_DIR, GENERATED_DIR
from app.services.campaign_service import campaign_generate
router = APIRouter()


@router.post("/create-campaign")
async def create_campaign(request: CampaignRequest):
    generated_files = campaign_generate(request)

    return {"generated_files": generated_files}             