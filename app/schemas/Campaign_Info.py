from typing import List, Optional

from pydantic import BaseModel, HttpUrl
from datetime import date
class Product(BaseModel):
    name: str
    description: Optional[str] = None      # short tagline for product
    old_price: Optional[float] = None
    new_price: Optional[float] = None
    discount: Optional[float] = None
    image: Optional[HttpUrl] = None
    currency: Optional[str] = "USD"        # currency field

class CampaignRequest(BaseModel):
    supermarket_name: str
    supermarket_address: str
    campaign_start_date: date
    campaign_end_date: date
    supermarket_logo: HttpUrl
    
    products: List[Product]   
    products_per_page: int = 9             # sensible default
    
    template_instruction: str              # e.g. "Discount Flyer", "Hero Banner"
    theme_style: Optional[str] = "modern"  # "festive", "minimal", "bold"
    background_image: Optional[HttpUrl] = None
    target_languages: Optional[List[str]] = ["en"]  # default English
