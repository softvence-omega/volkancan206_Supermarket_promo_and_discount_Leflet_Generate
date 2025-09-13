
import os
import time
from io import BytesIO
from PIL import Image
from google import genai
from google.genai.errors import ClientError
from app.services.upload import upload_image,upload_pdf

from app.config import GEMINI_API_KEY,GENERATED_DIR

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)


def generate_flyer_page(prompt: str, images: list, output_prefix="flyer_page"):
    """
    Generate one flyer page with Gemini.
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=[prompt] + images,
        )
    except ClientError as e:
        if e.status_code == 429:
            print(" Quota exceeded. Retrying in 60s...")
            time.sleep(60)
            return generate_flyer_page(prompt, images, output_prefix)
        else:
            raise

    saved_files = []
    i = 0
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print("Model text output:", part.text)
        elif part.inline_data is not None:
            image = Image.open(BytesIO(part.inline_data.data))
            filename = f"{output_prefix}_{i}.png"
            image.save(filename)
            saved_files.append(filename)
            print(f" Saved generated image: {filename}")
            i += 1

    return saved_files


def build_prompt(supermarket_info: dict, products: list):
    """
    Build flyer prompt dynamically for Gemini (leaflet style).
    """
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
    Design a supermarket **flyer / leaflet page** for '{supermarket_info['supermarket_name']}' and supermarket logo does not change.

    🔹 Campaign: {supermarket_info['Why_this_campaign']}
    🔹 Theme/Style: {supermarket_info['theme_style']}
    🔹 Layout: {supermarket_info['template_instruction']}
    🔹  Products (show multilingual text exactly as given): 
    🔹 Products per page: {len(products)} (STRICTLY exactly {len(products)} products shown in the grid)
    🔹 Address: {supermarket_info['supermarket_address']}
    🔹 Campaign dates: {supermarket_info['campaign_start_date']} → {supermarket_info['campaign_end_date']}
    🔹 Contact info: Must include supermarket LOGO (provided image), name, tagline.

    🛒 Products on this page:
    {product_lines}

    📌 Rules:
    - DO NOT add extra placeholders, empty grids, or additional products.
    - Show only {len(products)} product blocks in an organized leaflet style.
    - Text must be large, clear, and accurate.
    Important:
    - Always include the supermarket logo on every page (do not alter or redesign it).  
    - Render all product names and text exactly as provided (could be Chinese, Japanese, Turkish, Hindi, Bangla, Korean, Arabic, etc.).  
    - If the text is Right-to-Left (e.g. Arabic, Urdu, Hebrew), align it properly.  
    - Maintain clean professional design with the requested theme.  

    - Flyer should look like a real **printed leaflet** with logo and campaign theme.
    """
    return prompt



def generate_flyer_pdf(request: dict, output_pdf="flyer_campaign.pdf"):
    products = request["products"]
    per_page = request.get("products_per_page", 3)  # default 3 per page if not set
    flyer_images = []
    total_products = len(products)

    # Preload logo once
    with Image.open(request["logo_path"]) as img:
        logo_img = img.copy()
        
    output_path= os.path.join(GENERATED_DIR, request['supermarket_name'])
    os.makedirs(output_path, exist_ok=True)
    print("output path--------", output_path)
    
    for i in range(0, total_products, per_page):
        chunk = products[i:i + per_page]
        prompt = build_prompt(request, chunk) + f"\n(Total products in campaign: {total_products})"

        # Start with logo first
        imgs = [logo_img.copy()]

        # Add product images
        for p in chunk:
            with Image.open(p["product_path"]) as img:
                imgs.append(img.copy())

        img_path= os.path.join(output_path, f"flyer_page_{i//per_page}" )
        print("generated image file path-----------------", img_path)
        
        # Generate flyer page (logo is guaranteed to be the first image)
        page_files = generate_flyer_page(prompt, imgs, output_prefix=img_path)
        flyer_images.extend(page_files)

    # Merge all pages into a single PDF
    if flyer_images:
        pil_imgs = [Image.open(f).convert("RGB") for f in flyer_images]
        pil_imgs[0].save(output_pdf, save_all=True, append_images=pil_imgs[1:])
        print(f"Final flyer PDF saved: {output_pdf}")
    else:
        print("No flyer images generated.")
    
     # Upload images to Cloudinary
    uploaded_images = [upload_image(f) for f in flyer_images]

    # Upload PDF to Cloudinary
    uploaded_pdf = upload_pdf(output_pdf)
    # os.rmdir(output_path)

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
