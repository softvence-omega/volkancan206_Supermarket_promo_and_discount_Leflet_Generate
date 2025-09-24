from typing import List, Optional

from pydantic import BaseModel, Field
from datetime import date


products_example = [
    {
        "name": "Organic Bananas",
        "secondary_name": "Fresh Ripe Bananas - 1kg",
        "old_price": 5.0,
        "new_price": 3.5,
        "discount": 1.5,
        "image_url": "https://e7.pngegg.com/pngimages/529/583/png-clipart-organic-food-banana-bread-grocery-store-banana-natural-foods-food.png",
        "currency": "USD"
    },
    {
        "name": "Almonds",
        "secondary_name": "Raw California Almonds - 500g",
        "old_price": 15.0,
        "new_price": 12.0,
        "discount": 3.0,
        "image_url": "https://www.vhv.rs/dpng/d/416-4163473_almond-png-images-transparent-free-download-transparent-background.png",
        "currency": "USD"
    },
    {
        "name": "Whole Wheat Bread",
        "secondary_name": "Freshly Baked Whole Wheat Bread - 400g",
        "old_price": 4.0,
        "new_price": 3.0,
        "discount": 1.0,
        "image_url": "https://w7.pngwing.com/pngs/467/548/png-transparent-pita-whole-wheat-bread-whole-grain-nutrition-bread-baked-goods-food-baking.png",
        "currency": "USD"
    },
    {
        "name": "Greek Yogurt",
        "secondary_name": "Plain Low-Fat Greek Yogurt - 500g",
        "old_price": 6.0,
        "new_price": 5.0,
        "discount": 1.0,
        "image_url": "https://png.pngtree.com/png-vector/20240822/ourlarge/pngtree-greek-yogurt-with-fresh-berries-delight-creamy-topped-png-image_13581443.png",
        "currency": "USD"
    },
    {
        "name": "Cheddar Cheese",
        "secondary_name": "Aged Cheddar Cheese - 200g",
        "old_price": 8.0,
        "new_price": 6.5,
        "discount": 1.5,
        "image_url": "https://w7.pngwing.com/pngs/205/499/png-transparent-cheddar-cheese-emmental-cheese-edam-gouda-cheese-cheddar-food-cheese-beyaz-peynir-thumbnail.png",
        "currency": "USD"
    },
    {
        "name": "Fresh Strawberries",
        "secondary_name": "Juicy Fresh Strawberries - 1kg",
        "old_price": 10.0,
        "new_price": 8.0,
        "discount": 2.0,
        "image_url": "https://www.citypng.com/public/uploads/preview/falling-strawberries-fruit-hd-png-735811696673912okm7mf7t2t.png",
        "currency": "USD"
    },
    {
        "name": "Olive Oil",
        "secondary_name": "Extra Virgin Olive Oil - 500ml",
        "old_price": 12.0,
        "new_price": 9.5,
        "discount": 2.5,
        "image_url": "https://w7.pngwing.com/pngs/473/711/png-transparent-olive-oil-cooking-oils-wine-olive-oil-food-olive-wine-thumbnail.png",
        "currency": "USD"
    },
    {
        "name": "Dark Chocolate",
        "secondary_name": "Premium Belgian Dark Chocolate - 200g",
        "old_price": 7.0,
        "new_price": 5.5,
        "discount": 1.5,
        "image_url": "https://image.similarpng.com/file/similarpng/very-thumbnail/2020/08/Dark-chocolate-on-transparent-PNG.png",
        "currency": "USD"
    }
]


class Product(BaseModel):
    name: str
    secondary_name: str
    old_price: Optional[float] = None
    new_price: Optional[float] = None
    discount: Optional[float] = None
    image_url: Optional[str] = None
    currency: Optional[str] = "USD"      # currency field

class CampaignRequest(BaseModel):
    supermarket_name: str = Field(..., example="Brahmanbaria Online Bazar")
    why_this_campaign: str = Field(..., example="To promote seasonal discounts")
    supermarket_address: str = Field(..., example="123 Main St, Anytown, USA")
    campaign_start_date: date = Field(..., example="2025-10-01")
    campaign_end_date: date = Field(..., example="2025-10-31")
    supermarket_logo_url: str = Field(..., example="https://i.pinimg.com/564x/d2/bb/a5/d2bba5593e8cf32b198d203bd9ba9e74.jpg")

    products: List[Product] = Field(..., example=products_example)
    products_per_page: int = Field(..., example=4)  

    template_instruction: str = Field(..., example="Discount Flyer")           
    theme_style: Optional[str] = Field(..., example="Durga Puja Theme") 

