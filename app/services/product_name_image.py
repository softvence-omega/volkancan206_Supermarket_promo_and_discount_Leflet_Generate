from app.config import HF_TOKEN,PRODUCT_DIR
from huggingface_hub import InferenceClient
import os


# Initialize client once
client = InferenceClient(
    provider="auto",
    api_key=HF_TOKEN,
)

def generate_product_image(product_name: str, save_path: str = None) -> str:

    prompt = f"A high-quality product  {product_name} image for supermarket and grocery, transparent, professional lighting, centered, 4k resolution"

    # Generate image
    image = client.text_to_image(
        prompt,
        model="black-forest-labs/FLUX.1-dev",
    )
    
 
    # If no save_path provided, create one
    if save_path is None:
        safe_name = product_name.replace(" ", "_").lower()
        save_path = os.path.join(PRODUCT_DIR, f"{safe_name}.png")
    else:
        save_path = os.path.join(PRODUCT_DIR, save_path)
    
    image.save(save_path)
    print("Generated product image path------", save_path)
    return save_path

# Example usage
if __name__ == "__main__":
    file_path = generate_product_image("one woman hair")
    print(f"Image saved at: {file_path}")
