import os
import mimetypes
import logging
import requests
from google import genai
from google.genai import types
from app.schemas.Campaign_Info import CampaignRequest
from app.config import GENERATED_DIR,GEMINI_API_KEY


logger = logging.getLogger(__name__)


def save_binary_file(file_name, data):
    """Helper to save binary image data to file."""
    with open(file_name, "wb") as f:
        f.write(data)
    logger.info(f"File saved to: {file_name}")


def split_products(products, per_page):
    """Split products list into chunks of per_page size."""
    for i in range(0, len(products), per_page):
        yield products[i:i + per_page]


def generate_page_prompt(campaign: CampaignRequest, products_page, page_num):
    """Build text prompt for Gemini per page."""
    product_details = "\n".join([
        f"{p.name} ({p.secondary_name}): Old {p.currency}{p.old_price} → "
        f"New {p.currency}{p.new_price}"
        for p in products_page
    ])

    prompt = f"""
    Create a high-quality **{campaign.theme_style} discount flyer page**.
    Supermarket: {campaign.supermarket_name}
    Address: {campaign.supermarket_address}
    Campaign: {campaign.Why_this_campaign}
    Date: {campaign.campaign_start_date} - {campaign.campaign_end_date}
    Logo file: {campaign.supermarket_logo_url}

    Products on this page:
    {product_details}

    Design guideline: {campaign.template_instruction}
    This is page {page_num}.
    """
    return prompt



# def generate_leaflet(campaign: CampaignRequest, output_dir=GENERATED_DIR):
#     """Generate a multi-page leaflet using Gemini API and return PDF path."""
#     os.makedirs(output_dir, exist_ok=True)

#     client = genai.Client(api_key=GEMINI_API_KEY)
#     model = "gemini-2.5-flash-image-preview"

#     pages = list(split_products(campaign.products, campaign.products_per_page))
#     leaflet_images = []

#     for page_num, products_page in enumerate(pages, start=1):
#         prompt = generate_page_prompt(campaign, products_page, page_num)

#         contents = [
#             types.Content(
#                 role="user",
#                 parts=[types.Part.from_text(text=prompt)],
#             )
#         ]
#         generate_content_config = types.GenerateContentConfig(
#             response_modalities=["IMAGE"]
#         )

#         file_index = 0
#         image_path = None

#         logger.info(f"🔄 Generating flyer page {page_num} with {len(products_page)} products...")

#         for chunk in client.models.generate_content_stream(
#             model=model,
#             contents=contents,
#             config=generate_content_config,
#         ):
#             if (
#                 chunk.candidates
#                 and chunk.candidates[0].content
#                 and chunk.candidates[0].content.parts
#                 and chunk.candidates[0].content.parts[0].inline_data
#                 and chunk.candidates[0].content.parts[0].inline_data.data
#             ):
#                 inline_data = chunk.candidates[0].content.parts[0].inline_data
#                 data_buffer = inline_data.data
#                 file_extension = mimetypes.guess_extension(inline_data.mime_type) or ".png"
#                 image_path = os.path.join(output_dir, f"leaflet_page_{page_num}{file_extension}")
#                 save_binary_file(image_path, data_buffer)
#                 leaflet_images.append(image_path)
#                 file_index += 1

#         if not image_path:
#             raise RuntimeError(f"❌ Failed to generate image for page {page_num}")

#     # --- Merge images into PDF ---
#     pdf_path = os.path.join(output_dir, f"{campaign.supermarket_name}_leaflet.pdf")
#     pdf = FPDF()
#     for img in leaflet_images:
#         pdf.add_page()
#         pdf.image(img, x=0, y=0, w=210, h=297)  # A4 size
#     pdf.output(pdf_path, "F")

#     logger.info(f"✅ Leaflet PDF generated at: {pdf_path}")
#     return pdf_path
from PIL import Image, ImageDraw

def generate_leaflet(campaign: CampaignRequest, output_dir=GENERATED_DIR):
    """Generate a multi-page leaflet using Gemini API and return image paths only (A4 size)."""
    os.makedirs(output_dir, exist_ok=True)

    client = genai.Client(api_key=GEMINI_API_KEY)
    model = "gemini-2.5-flash-image-preview"

    pages = list(split_products(campaign.products, campaign.products_per_page))
    leaflet_images = []

    for page_num, products_page in enumerate(pages, start=1):
        prompt = generate_page_prompt(campaign, products_page, page_num)

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            )
        ]
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["IMAGE"]
        )

        image_path = None
        logger.info(f"🔄 Generating flyer page {page_num} with {len(products_page)} products...")

        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if (
                chunk.candidates
                and chunk.candidates[0].content
                and chunk.candidates[0].content.parts
                and chunk.candidates[0].content.parts[0].inline_data
                and chunk.candidates[0].content.parts[0].inline_data.data
            ):
                inline_data = chunk.candidates[0].content.parts[0].inline_data
                data_buffer = inline_data.data
                file_extension = mimetypes.guess_extension(inline_data.mime_type) or ".png"
                image_path = os.path.join(output_dir, f"leaflet_page_{page_num}{file_extension}")
                save_binary_file(image_path, data_buffer)

                # 🖼 Add supermarket logo on top of the generated image
                if campaign.supermarket_logo_url:
                    try:
                        flyer = Image.open(image_path).convert("RGBA")
                        logo = Image.open(requests.get(campaign.supermarket_logo_url, stream=True).raw).convert("RGBA")

                        # Resize logo (e.g., width 150px)
                        logo_width = 150
                        logo_height = int((logo_width / logo.width) * logo.height)
                        logo = logo.resize((logo_width, logo_height), Image.LANCZOS)

                        # Paste logo top-left corner with transparency
                        flyer.paste(logo, (20, 20), logo)

                        flyer.save(image_path)
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to overlay logo on page {page_num}: {e}")

                leaflet_images.append(image_path)

        if not image_path:
            raise RuntimeError(f"❌ Failed to generate image for page {page_num}")

    logger.info(f"✅ {len(leaflet_images)} leaflet pages generated at: {output_dir}")
    return leaflet_images


# ---------------- TEST ----------------
if __name__ == "__main__":
    from app.schemas.Campaign_Info import CampaignRequest

    example_request = CampaignRequest(
        supermarket_name="SuperMart",
        Why_this_campaign="Best prices for fresh produce!",
        supermarket_address="123 Main St",
        campaign_start_date="2024-06-01",
        campaign_end_date="2024-06-15",
        supermarket_logo_url="./app/temp/logo/shop_logo.png",
        products=[
            {
                "name": "Potato",
                "secondary_name": "بطاطس طازجة",
                "old_price": 3.5,
                "new_price": 2.8,
                "discount": 20,
                "image_url": "./app/temp/product_images/potato.png",
                "currency": "$"
            },
            {
                "name": "Tomato",
                "secondary_name": "طماطم طازجة",
                "old_price": 4.0,
                "new_price": 3.2,
                "discount": 20,
                "image_url": "./app/temp/product_images/tomato.png",
                "currency": "$"
            },
            {
                "name": "Onion",
                "secondary_name": "بصل طازج",
                "old_price": 2.0,
                "new_price": 1.5,
                "discount": 25,
                "image_url": "./app/temp/product_images/onion.png",
                "currency": "$"
            }
        ],
        products_per_page=2,
        template_instruction="Discount Flyer for green and organic products",
        theme_style="modern",
    )

    result = generate_leaflet(example_request)
    print("🎉 Leaflet generated:", result)
