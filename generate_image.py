from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64

def generate(output_file_name, folder_name, prompt_file):
    client = genai.Client(
        api_key= open("prompt/api_key.txt").read(),
    )
    
    # Read the prompt from the file
    with open(prompt_file, 'r') as file:
        prompt = file.read()

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp-image-generation",
        contents=prompt,
        config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE']
        )
    )

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = Image.open(BytesIO((part.inline_data.data)))
            image.save(os.path.join(folder_name, output_file_name))
            image.show()
            print("Image saved as", output_file_name)

def main(output_file_name, story_folder_name, prompt_file):
    generate(output_file_name, story_folder_name, prompt_file)

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 4:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print("Usage: python generate_image.py <output_file_name> <story_folder_name> <prompt_file>")

