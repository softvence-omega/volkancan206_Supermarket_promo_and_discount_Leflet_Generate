from huggingface_hub import InferenceClient
from PIL import Image
import io

from app.config import HF_TOKEN

client = InferenceClient(model="Qwen/Qwen-Image-Edit", token=HF_TOKEN)

def car_wrap(image_path, prompt):
    print("Designing car wrap for:", image_path)
    
    # Open image as PIL Image
    img = Image.open(image_path)
    
    # Convert image to bytes (PNG) in memory
    img_bytes_io = io.BytesIO()
    img.save(img_bytes_io, format="PNG")
    image_bytes = img_bytes_io.getvalue()

    # Call HF image-to-image model
    result = client.image_to_image(image=image_bytes, prompt=prompt)
    print("Received result:", type(result))
    
    # Save edited image
    if isinstance(result, Image.Image):
        output_path = "edited_car.png"
        result.save(output_path, format="PNG")
        print("Edited image saved at:", output_path)
        return output_path
    else:
        raise ValueError("The model did not return a valid image.")

if __name__ == "__main__":
    image_path = "car.jpg"
    prompt = "JUST CAR COLOR CHANGE black color"
    output = car_wrap(image_path, prompt)
    print("Output image path:", output)