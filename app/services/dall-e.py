import time
import requests
from app.config import OPENAI_API_KEY

def generate_leaflet_image(supermarket_name: str,
                           campaign_dates: str,
                           products: list,
                           logo_url: str = None,
                           languages: list = ["english"],
                           size: str = "1024x1024") -> str:
    """
    Generates a realistic, high-quality supermarket campaign leaflet image using OpenAI DALL-E 3.
    
    Args:
        supermarket_name: Name of the supermarket.
        campaign_dates: Campaign duration (e.g., "15 Aug 2025 - 25 Aug 2025").
        products: List of dicts with keys: name, unit, old_price, new_price, discount, image (optional).
        logo_url: Optional supermarket logo URL.
        languages: List of languages to include in the leaflet.
        size: Image size (default "1024x1024").
    
    Returns:
        URL of the generated image.
    """

    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    # Construct product list description
    product_lines = []
    for p in products:
        line = f"{p['name']} ({p.get('unit','unit')}): {p.get('new_price')} (was {p.get('old_price')})"
        if p.get('discount'):
            line += f", Discount: {p['discount']}"
        product_lines.append(line)
    product_text = "\n".join(product_lines)

    # Construct full prompt
    prompt = f"""
    Create a high-quality, realistic supermarket campaign leaflet.
    Supermarket: {supermarket_name}
    Campaign Dates: {campaign_dates}
    Products:
    {product_text}
    Logo URL: {logo_url or 'Not provided'}
    Languages: {', '.join(languages)}
    Include bold discount labels, modern layout, and professional design.
    Output should be suitable for printing and social media.
    """

    data = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": size
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        image_url = response.json()['data'][0]['url']
        return image_url
    else:
        print(f"[ERROR] OpenAI Image Generation Failed: {response.status_code} - {response.text}")
        return None


# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    start_time = time.time()

    products_example = [
        {"name": "Sugar", "unit": "kg", "old_price": 60, "new_price": 50, "discount": "16%"},
        {"name": "Rice", "unit": "kg", "old_price": 70, "new_price": 60, "discount": "14%"},
        {"name": "Powdered Sugar", "unit": "kg", "old_price": 55, "new_price": 48, "discount": "12%"}
    ]

    image_url = generate_leaflet_image(
        supermarket_name="Interfood Supermarket",
        campaign_dates="15 Aug 2025 - 25 Aug 2025",
        products=products_example,
        logo_url="https://drive.google.com/file/d/1TgcknezgDLQc7D7kA9Btamfz25WfNzoh/view?usp=sharing",
        languages=["english"]
    )

    print("Generated Leaflet Image URL:", image_url)

    end_time = time.time()
    print(f"Execution Time: {end_time - start_time:.2f} seconds")
