from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


# products_example = [
#     {
#         "name": "Organic Bananas",
#         "secondary_name": "Fresh Ripe Bananas - 1kg",
#         "old_price": 5.0,
#         "new_price": 3.5,
#         "discount": 1.5,
#         "image_url": "https://e7.pngegg.com/pngimages/529/583/png-clipart-organic-food-banana-bread-grocery-store-banana-natural-foods-food.png",
#         "currency": "USD"
#     },
#     {
#         "name": "Almonds",
#         "secondary_name": "Raw California Almonds - 500g",
#         "old_price": 15.0,
#         "new_price": 12.0,
#         "discount": 3.0,
#         "image_url": "https://www.vhv.rs/dpng/d/416-4163473_almond-png-images-transparent-free-download-transparent-background.png",
#         "currency": "USD"
#     },
#     {
#         "name": "Whole Wheat Bread",
#         "secondary_name": "Freshly Baked Whole Wheat Bread - 400g",
#         "old_price": 4.0,
#         "new_price": 3.0,
#         "discount": 1.0,
#         "image_url": "https://w7.pngwing.com/pngs/467/548/png-transparent-pita-whole-wheat-bread-whole-grain-nutrition-bread-baked-goods-food-baking.png",
#         "currency": "USD"
#     },
#     {
#         "name": "Greek Yogurt",
#         "secondary_name": "Plain Low-Fat Greek Yogurt - 500g",
#         "old_price": 6.0,
#         "new_price": 5.0,
#         "discount": 1.0,
#         "image_url": "https://png.pngtree.com/png-vector/20240822/ourlarge/pngtree-greek-yogurt-with-fresh-berries-delight-creamy-topped-png-image_13581443.png",
#         "currency": "USD"
#     },
#     {
#         "name": "Cheddar Cheese",
#         "secondary_name": "Aged Cheddar Cheese - 200g",
#         "old_price": 8.0,
#         "new_price": 6.5,
#         "discount": 1.5,
#         "image_url": "https://w7.pngwing.com/pngs/205/499/png-transparent-cheddar-cheese-emmental-cheese-edam-gouda-cheese-cheddar-food-cheese-beyaz-peynir-thumbnail.png",
#         "currency": "USD"
#     },
#     {
#         "name": "Fresh Strawberries",
#         "secondary_name": "Juicy Fresh Strawberries - 1kg",
#         "old_price": 10.0,
#         "new_price": 8.0,
#         "discount": 2.0,
#         "image_url": "https://www.citypng.com/public/uploads/preview/falling-strawberries-fruit-hd-png-735811696673912okm7mf7t2t.png",
#         "currency": "USD"
#     },
#     {
#         "name": "Olive Oil",
#         "secondary_name": "Extra Virgin Olive Oil - 500ml",
#         "old_price": 12.0,
#         "new_price": 9.5,
#         "discount": 2.5,
#         "image_url": "https://w7.pngwing.com/pngs/473/711/png-transparent-olive-oil-cooking-oils-wine-olive-oil-food-olive-wine-thumbnail.png",
#         "currency": "USD"
#     },
#     {
#         "name": "Dark Chocolate",
#         "secondary_name": "Premium Belgian Dark Chocolate - 200g",
#         "old_price": 7.0,
#         "new_price": 5.5,
#         "discount": 1.5,
#         "image_url": "https://image.similarpng.com/file/similarpng/very-thumbnail/2020/08/Dark-chocolate-on-transparent-PNG.png",
#         "currency": "USD"
#     }
# ]



class Product(BaseModel):
    currency: str
    discount: float
    image_url: HttpUrl
    name: str
    new_price: float
    old_price: float
    secondary_name: str

class FlyerRequest(BaseModel):
    supermarket_name: str
    why_this_campaign: str
    supermarket_address: str
    campaign_start_date: str
    campaign_end_date: str
    supermarket_logo_url: HttpUrl
    products: List[Product]
    products_per_page: int = 4
    template_instruction: str
    theme_style: str
    phone_number: Optional[str] = "01700000000"
    email: Optional[str] = "info@supermarket.com"

class FlyerResponse(BaseModel):
    success: bool
    message: str
    flyers_generated: int
    pdf_url: Optional[HttpUrl] = None
    img_urls: Optional[List[HttpUrl]] = None