from fastapi import APIRouter
from typing import List
from app.schemas.Campaign_Info import CampaignRequest
from app.services.campagin_page import campaign_generate


router = APIRouter()


@router.post("/create-campaign")
async def create_campaign(request: CampaignRequest):
    flyer_paths = campaign_generate(request.model_dump())
    print("Generated Flyer Paths:", flyer_paths)

    return {"generated_files": flyer_paths}