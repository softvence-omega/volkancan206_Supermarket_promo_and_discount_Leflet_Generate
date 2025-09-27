import os
from google import genai
from google.genai.errors import ClientError
from app.config import PRODUCT_DIR, GEMINI_API_KEY


# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

def generate_product_image(product_name: str, save_path: str = None) -> str:
    prompt = (
        f"High-quality supermarket product photo of {product_name}, "
        "fresh and realistic, transparent background, professional studio lighting, "
        "sharp details, vibrant colors, centered composition, 4k resolution"
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash-image-preview",
        contents=prompt
    )

    # Safely extract first image part
    try:
        if not response.candidates or not response.candidates[0].content.parts:
            raise RuntimeError("No image parts returned by Gemini API")
        
        # Loop through parts to find inline_data (image)
        image_bytes = None
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                image_bytes = part.inline_data.data
                break

        if image_bytes is None:
            raise RuntimeError("No image found in response parts")

    except Exception as e:
        raise RuntimeError(f"Could not extract image from response: {e}")

    # Prepare save path
    if save_path is None:
        safe_name = product_name.replace(" ", "_").lower()
        save_path = os.path.join(PRODUCT_DIR, f"{safe_name}.png")
    else:
        save_path = os.path.join(PRODUCT_DIR, save_path)

    # Save image
    with open(save_path, "wb") as f:
        f.write(image_bytes)

    return save_path

# Example usage
if __name__ == "__main__":
    file_path = generate_product_image("green cucumbers")
    print(f"Image saved at: {file_path}")
