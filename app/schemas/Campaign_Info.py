from typing import List, Optional

from pydantic import BaseModel
from datetime import date
class Product(BaseModel):
    name: str
    secondary_name: str
    old_price: Optional[float] = None
    new_price: Optional[float] = None
    discount: Optional[float] = None
    image_url: Optional[str] = None
    currency: Optional[str] = "USD"      # currency field

class CampaignRequest(BaseModel):
    supermarket_name: str
    Why_this_campaign: str
    supermarket_address: str
    campaign_start_date: date
    campaign_end_date: date
    supermarket_logo_url: str

    products: List[Product]
    products_per_page: int = 9             # sensible default
    
    template_instruction: str              # e.g. "Discount Flyer", "Hero Banner"
    theme_style: Optional[str] = "modern"  # "festive", "minimal", "bold"

