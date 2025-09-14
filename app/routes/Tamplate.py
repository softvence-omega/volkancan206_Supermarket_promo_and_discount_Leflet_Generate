from fastapi import APIRouter
from typing import List
from app.schemas.Campaign_Info import CampaignRequest
from app.services.campagin_page import campaign_generate
router = APIRouter()


@router.post("/create-campaign")
async def create_campaign(request: CampaignRequest):
    generated_files = campaign_generate(request.dict())

    return {"generated_files": generated_files}             