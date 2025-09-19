
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
    
    prompt = f"""
    You are an expert supermarket flyer and leaflet designer.  
    Your task is to generate **visually attractive supermarket flyer pages** optimized for promotions, discounts, and seasonal campaigns. 
    - Auto Generating  background attractive for supermarket leaflet style.
    - **First flyer image defines the background** for all following pages.
    - No extra words; text must be clear and multilingual.
    Now design **flyer page** for **'{supermarket_info['supermarket_name']}'**:

    - Campaign: {supermarket_info['Why_this_campaign']}
    - Theme/Style: {supermarket_info['theme_style']} (STRICTLY MAINTAIN SAME STYLE across all pages)
    - Layout: {supermarket_info['template_instruction']} (DO NOT improvise outside these rules)
    - Campaign dates: {supermarket_info['campaign_start_date']} → {supermarket_info['campaign_end_date']}
    - Address: {supermarket_info['supermarket_address']} (MUST appear in footer, every page)
    Products to include exact as provide no more no less):  
    {product_lines}

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




# if __name__ == "__main__":
#     example_request = {
#         "supermarket_name": "Interfood",
#         "Why_this_campaign": "Massive Eid Discounts!",
#         "supermarket_address": "CAN Nürnberg,Ingolstädter Str. 53,90461 Nürnberg,Telefon 09 11/99 44 83 70,Mo. - Sa. 08.00 - 20.00 Uhr",
#         "campaign_start_date": "2025-09-10",
#         "campaign_end_date": "2025-09-25",
#         "supermarket_logo_url": "temp/logo/supermart.png",  #will be used
#         "products":   "products": [
#     {
#       "name": "cocacola",
#       "secondary_name": "تفاح",
#       "old_price": 5.0,
#       "new_price": 3.5,
#       "discount": 30,
#       "image_url": "https://media.cnn.com/api/v1/images/stellar/prod/gettyimages-2179849363.jpg?c=16x9&q=h_653,w_1160,c_fill/f_avif",
#       "currency": "$"
#     },
#     {
#       "name": "mango",
#       "secondary_name": "أرز",
#       "old_price": 20.0,
#       "new_price": 15.0,
#       "discount": 25,
#       "image_url": "https://foodal.com/wp-content/uploads/2015/06/Marvelous-Mangos-King-of-Fruits.jpg",
#       "currency": "$"
#     },
#     {
#       "name": "souce",
#       "secondary_name": "لحم",
#       "old_price": 200.0,
#       "new_price": 150.0,
#       "discount": 25,
#       "image_url": "https://5.imimg.com/data5/SELLER/Default/2024/3/398297040/RT/DM/KK/44772625/red-chilli-souce-650-ml-1000x1000.jpg",
#       "currency": "Tk"
#     },
#     {
#       "name": "pepsi",
#       "secondary_name": "عصير",
#       "old_price": 6.0,
#       "new_price": 4.0,
#       "discount": 33,
#       "image_url": "https://media.istockphoto.com/id/487787092/photo/can-and-glass-of-pepsi-cola.jpg?s=612x612&w=0&k=20&c=4Lqp4y8xCIF4IrV2a6DGkNhreCUwEAVfv3mEgb9aUJY=",
#       "currency": "$"
#     },
#     {
#       "name": "apple",
#       "secondary_name": "تفاح أحمر",
#       "old_price": 12.0,
#       "new_price": 9.0,
#       "discount": 25,
#       "image_url": "https://hips.hearstapps.com/hmg-prod/images/apples-at-farmers-market-royalty-free-image-1627321463.jpg?crop=0.796xw:1.00xh;0.103xw,0&resize=980:*",
#       "currency": "$"
#     },
#     {
#       "name": "rice",
#       "secondary_name": "أرز بسمتي",
#       "old_price": 50.0,
#       "new_price": 40.0,
#       "discount": 20,
#       "image_url": "https://c.ndtvimg.com/2023-08/brlp7gk_uncooked-rice-or-rice-grains_625x300_18_August_23.jpg?im=FaceCrop,algorithm=dnn,width=773,height=435",
#       "currency": "Tk"
#     },
#     {
#       "name": "chicken",
#       "secondary_name": "دجاج",
#       "old_price": 150.0,
#       "new_price": 120.0,
#       "discount": 20,
#       "image_url": "https://assets.farmison.com/images/recipe-detail-1380/76340-yorkshire-free-range-loose-birds-chicken3c3e9dd7-8edd-41fa-b35d-73f3cb951b8asquare900x900.jpg",
#       "currency": "Tk"
#     },
#     {
#       "name": "orange juice",
#       "secondary_name": "برتقال",
#       "old_price": 15.0,
#       "new_price": 10.0,
#       "discount": 33,
#       "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Orangejuice.jpg/800px-Orangejuice.jpg",
#       "currency": "$"
#     },
#     {
#       "name": "milk",
#       "secondary_name": "حليب",
#       "old_price": 25.0,
#       "new_price": 20.0,
#       "discount": 20,
#       "image_url": "https://mydiagnostics.in/cdn/shop/articles/img-1748326586409_1200x.jpg?v=1748327918",
#       "currency": "Tk"
#     },
#     {
#       "name": "bread",
#       "secondary_name": "خبز",
#       "old_price": 8.0,
#       "new_price": 6.0,
#       "discount": 25,
#       "image_url": "https://www.bhg.com/thmb/ix1jf9aUXcxyFtekIBlVCAIBW4w=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/BHG-milk-bread-4CdeIL1uKGyB5ryU8J_EED-aaa76729c86a413ca7500029edba79f0.jpg",
#       "currency": "$"
#     }

#         ],
#         "products_per_page": 2,
#         "template_instruction": "Clean modern layout, green eco theme",
#         "theme_style": "organic and minimal",
#     }

#     generate_flyer_pdf(example_request)
