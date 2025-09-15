import os
from google import genai
from google.genai.errors import ClientError
from app.config import PRODUCT_DIR, GEMINI_API_KEY


# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)


def generate_product_image(product_name: str, save_path: str = None) -> str:
    # Gemini model for image generation
    prompt = (
        f"High-quality supermarket product photo of {product_name}, "
        f"shown as a group or pile, fresh and realistic, "
        f"transparent background, professional studio lighting, "
        f"sharp details, vibrant colors, centered composition, 4k resolution"
    )


    # Generate image
    response = client.models.generate_content(
        model="gemini-2.5-flash-image-preview",
        contents=prompt
    )
    print("---------------------", response)

    # Extract image bytes from response
    try:
        part = response.candidates[0].content.parts[1]  # second part is usually image
        image_bytes = part.inline_data.data
    except Exception as e:
        raise RuntimeError(f"Could not extract image from response: {e}")

    # If no save_path provided, create one
    if save_path is None:
        safe_name = product_name.replace(" ", "_").lower()
        save_path = os.path.join(PRODUCT_DIR, f"{safe_name}.png")
    else:
        save_path = os.path.join(PRODUCT_DIR, save_path)

    # Save image
    with open(save_path, "wb") as f:
        f.write(image_bytes)

    print("Generated product image path ------", save_path)
    return save_path


# Example usage
if __name__ == "__main__":
    file_path = generate_product_image("green cucumbers")
    print(f"Image saved at: {file_path}")
