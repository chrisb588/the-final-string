from PIL import Image
import sys
import os

def upscale_spritesheet(input_path, output_path, scale_factor=2):
    img = Image.open(input_path)
    width, height = img.size

    # Check if input dimensions are divisible by 16
    if width % 16 != 0 or height % 16 != 0:
        raise ValueError("Image dimensions must be multiples of 16.")

    # Scale the entire image using nearest-neighbor
    upscaled_img = img.resize((width * scale_factor, height * scale_factor), Image.NEAREST)

    upscaled_img.save(output_path)
    print(f"Upscaled image saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python upscale.py <input_path> <output_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    upscale_spritesheet(input_path, output_path)
