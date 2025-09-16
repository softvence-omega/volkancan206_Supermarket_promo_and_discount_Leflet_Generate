
import os
import time
from io import BytesIO
from PIL import Image
from google import genai
from google.genai.errors import ClientError
from app.services.upload import upload_image,upload_pdf
import shutil

from app.config import GEMINI_API_KEY,GENERATED_DIR

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)


def generate_flyer_page(prompt: str, images: list, output_prefix="flyer_page"):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=[prompt] + images,
        )
    except ClientError as e:
        if e.status_code == 429:
            print("Quota exceeded. Retrying in 60s...")
            time.sleep(60)
            return generate_flyer_page(prompt, images, output_prefix)
        else:
            raise

    saved_files = []
    candidate = response.candidates[0]

    # Ensure candidate.content and parts exist
    if not getattr(candidate, "content", None) or not getattr(candidate.content, "parts", None):
        print("No image parts returned by Gemini.")
        return saved_files  # empty list

    i = 0
    for part in candidate.content.parts:
        if getattr(part, "inline_data", None):
            image = Image.open(BytesIO(part.inline_data.data))
            if image.mode in ("P", "RGBA"):
                image = image.convert("RGB")
            filename = f"{output_prefix}_{i}.png"
            image.save(filename)
            saved_files.append(filename)
            print(f" Saved generated image: {filename}")
            i += 1
        elif getattr(part, "text", None):
            print("Text output:", part.text)

    return saved_files


def build_prompt(supermarket_info: dict, products: list):
    """
    Build flyer prompt dynamically for Gemini (leaflet style).
    Max 6 products per flyer page with details.
    Each page must be unique but include the logo consistently.
    """
    page_product = supermarket_info['products_per_page']

    product_lines = "\n".join(
        [
            f"- {p['name']} ({p.get('secondary_name','')}) "
            f"| Old: {p['old_price']} {p['currency']} "
            f"| New: {p['new_price']} {p['currency']} "
            f"| Discount: {p['discount']}%"
            for p in products
        ]
    )
    
    prompt = f"""
    Build flyer prompt with consistency controls for multi-page generation
    """
    product_lines = "\n".join([
        f"- {p['name']} ({p.get('secondary_name','')}) "
        f"| Old: {p['old_price']} {p['currency']} "
        f"| New: {p['new_price']} {p['currency']} "
        f"| Discount: {p['discount']}%"
        for p in products
    ])
    
    # Enhanced prompt with strict consistency rules
    prompt = f"""
    CRITICAL CONSISTENCY RULES - MUST FOLLOW EXACTLY:
    🚫 DO NOT modify, redesign, or alter the supermarket logo in ANY way
    🚫 DO NOT change background colors, gradients, or design elements
    🚫 DO NOT substitute or modify product images
    🚫 USE IDENTICAL design layout as previous pages

    Design supermarket flyer page {page_product} for '{supermarket_info['supermarket_name']}'.
    
    VISUAL CONSISTENCY REQUIREMENTS:
    ✅ Use EXACT SAME logo placement and size as reference
    ✅ Maintain IDENTICAL background design and colors
    ✅ Keep SAME header/footer layout structure
    ✅ Use CONSISTENT typography and color scheme
    ✅ Product images must remain unchanged from original
    
    🔹 Campaign: {supermarket_info['Why_this_campaign']}
    🔹 Theme/Style: {supermarket_info['theme_style']} (MAINTAIN EXACTLY)
    🔹 Layout: {supermarket_info['template_instruction']}
    🔹 Campaign dates: {supermarket_info['campaign_start_date']} → {supermarket_info['campaign_end_date']}
    🔹 Address: {supermarket_info['supermarket_address']} (MUST appear in footer)
    
    🛒 Products on page {page_product} (EXACTLY {len(products)} products):
    {product_lines}
    
    📌 STRICT RULES:
    - Show EXACTLY {len(products)} products, no more, no less
    - DO NOT add placeholder products or empty grids
    - Preserve original product images without modification
    - Logo must be identical to previous pages
    - Background design must remain consistent
    - Text alignment for RTL languages (Arabic, Urdu, Hebrew)
    - Professional printed leaflet appearance
    
    REFERENCE CONSISTENCY: If this is page 2+, maintain IDENTICAL visual style to page 1.
    """
    return prompt


def generate_flyer_pdf(request: dict, output_pdf="flyer_campaign.pdf"):
    products = request["products"]
    per_page = request.get("products_per_page", 3)  # default 3 per page
    flyer_images = []
    total_products = len(products)

    # Preload logo once and convert to RGB
    with Image.open(request["logo_path"]) as img:
        logo_img = img.copy()
        if logo_img.mode in ("P", "RGBA"):
            logo_img = logo_img.convert("RGB")

    # Prepare output folder
    output_path = os.path.join(GENERATED_DIR, request['supermarket_name'])
    os.makedirs(output_path, exist_ok=True)
    print("output path--------", output_path)

    background_image = None  # Keep background fixed from first page

    for i in range(0, total_products, per_page):
        chunk = products[i:i + per_page]
        prompt = build_prompt(request, chunk) + f"\n(Total products in campaign: {total_products})"

        # Start building image input list (logo always first)
        img_inputs = [logo_img.copy()]

        # Add product images (convert each to RGB)
        for p in chunk:
            with Image.open(p["product_path"]) as img:
                img_copy = img.copy()
                if img_copy.mode in ("P", "RGBA"):
                    img_copy = img_copy.convert("RGB")
                img_inputs.append(img_copy)

        # Use the same background for all pages
        if background_image:
            img_inputs.insert(1, background_image.copy())
            print("Using fixed background for this page")

        img_path = os.path.join(output_path, f"flyer_page_{i//per_page}")
        print("generated image file path-----------------", img_path)

        # Generate flyer page
        page_files = generate_flyer_page(prompt, img_inputs, output_prefix=img_path)

        # Convert Gemini-generated images to RGB just in case
        for idx, f in enumerate(page_files):
            with Image.open(f) as gen_img:
                if gen_img.mode in ("P", "RGBA"):
                    gen_img = gen_img.convert("RGB")
                    gen_img.save(f)  # overwrite file
            # Save only the first background, and reuse later
            if i == 0 and idx == 0 and background_image is None:
                background_image = Image.open(f).copy().convert("RGB")
                print("Background fixed from first page")

        flyer_images.extend(page_files)

    # Merge all pages into a single PDF
    if flyer_images:
        pil_imgs = []
        for f in flyer_images:
            with Image.open(f) as img:
                if img.mode in ("P", "RGBA"):
                    img = img.convert("RGB")
                pil_imgs.append(img.copy())

        pil_imgs[0].save(output_pdf, save_all=True, append_images=pil_imgs[1:])
        print(f"Final flyer PDF saved: {output_pdf}")
    else:
        print("No flyer images generated.")

    # Upload images to Cloudinary
    uploaded_images = [upload_image(f) for f in flyer_images]

    # Upload PDF to Cloudinary
    uploaded_pdf = upload_pdf(output_pdf)

    shutil.rmtree(output_path, ignore_errors=True)

    return {
        "images": uploaded_images,
        "flyer_pdf": uploaded_pdf
    }




if __name__ == "__main__":
    example_request = {
        "supermarket_name": "Interfood",
        "Why_this_campaign": "Massive Eid Discounts!",
        "supermarket_address": "CAN Nürnberg,Ingolstädter Str. 53,90461 Nürnberg,Telefon 09 11/99 44 83 70,Mo. - Sa. 08.00 - 20.00 Uhr",
        "campaign_start_date": "2025-09-10",
        "campaign_end_date": "2025-09-25",
        "supermarket_logo_url": "temp/logo/supermart.png",  #will be used
        "products": [
            {
                "name": "cocacola",
                "secondary_name": "تفاح",
                "old_price": 5.0,
                "new_price": 3.5,
                "discount": 30,
                "image_url": "https://drive.google.com/file/d/1h_V076e89aEkT-qN-GzMKnoq_jR7ymPR/view?usp=drive_link",
                "currency": "$"
            },
            {
                "name": "mango",
                "secondary_name": "أرز",
                "old_price": 20.0,
                "new_price": 15.0,
                "discount": 25,
                "image_url": "https://drive.google.com/file/d/1jxkmc6RXSpbO3TYup0tiH7QK5qe8XuZC/view?usp=drive_link",
                "currency": "$"
            },
            {
                "name": "souce",
                "secondary_name": "لحم",
                "old_price": 200,
                "new_price": 150,
                "discount": 25,
                "image_url": "https://drive.google.com/file/d/1hyc90sjFnZ7As7QfdeZgtdNEp91VhwtU/view?usp=drive_link",
                "currency": "Tk"
            }

        ],
        "products_per_page": 2,
        "template_instruction": "Clean modern layout, green eco theme",
        "theme_style": "organic and minimal",
    }

    generate_flyer_pdf(example_request)
