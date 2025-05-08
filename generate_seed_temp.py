
import base64
import os
from google import genai
from google.genai import types


def generate(story_name, story_text):
    client = genai.Client(
        api_key= open("prompt/api_key.txt").read(),
    )

    files = [
        # Please ensure that the file is available in local system working direrctory or change the file path.
        client.files.upload(file="prompt/Authors guide short.md"),
    ]
    model = "gemini-2.5-pro-exp-03-25"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_uri(
                    file_uri=files[0].uri,
                    mime_type=files[0].mime_type,
                ),
                types.Part.from_text(text="Read the authurs guide. With that knowledge, read the below atached story" 
                                     + story_name +  "Then I want you to analyze each sentence of the story one by one and write a detailed long essay structured in chapters where there is a chapter for each sentence in order. Analyze each sentence in relation to the whole story, morals, and metaphorical or psychological meanings (if there are any)." 
                                     + "Consider every line break in the attached story a new chapter, so the first line (other than the title if present) is chapter 1, and so on. When numbering the sentences, start at 1 and keep counting even when incrementing chapters. That is, do not ever reset the sentence count. "
                                     + story_text
                                     ),
            
    ]
        )
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type = genai.types.Type.OBJECT,
            required = ["Analysis", "The Complete Story"],
            properties = {
                "Analysis": genai.types.Schema(
                    type = genai.types.Type.ARRAY,
                    items = genai.types.Schema(
                        type = genai.types.Type.OBJECT,
                        required = ["Plot Function", "Grimm Style", "Moral Implication", "Metaphorical/Psychological Meaning", "Sentence", "Chapter Number", "Sentence Number"],
                        properties = {
                            "Plot Function": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "Grimm Style": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "Moral Implication": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "Metaphorical/Psychological Meaning": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "Sentence": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "Chapter Number": genai.types.Schema(
                                type = genai.types.Type.INTEGER,
                            ),
                            "Sentence Number": genai.types.Schema(
                                type = genai.types.Type.INTEGER,
                            ),
                        },
                    ),
                ),
                "The Complete Story": genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    required = ["Title", "Chapters"],
                    properties = {
                        "Title": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "Chapters": genai.types.Schema(
                            type = genai.types.Type.ARRAY,
                            items = genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                        ),
                    },
                ),
            },
        ),
    )

    output_file = f".\\unprocessed code\code {story_name}.txt"

    # Open file for writing
    with open(output_file, "w") as f:
        # Generate content
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            # Write to file and print to console
            f.write(chunk.text)
            print(chunk.text, end="")


def main(txt_file, story_name):
    # Load the content of the txt file
    
    with open(txt_file, 'r') as file:
        story_content = file.read()

    generate(story_name, story_content)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python generate_seed.py <txt_file> <story_name>")
    else:
        main(sys.argv[1], sys.argv[2])

