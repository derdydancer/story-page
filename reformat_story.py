# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import os
import sys
from google import genai
from google.genai import types


def generate():
    client = genai.Client(
        api_key= open("prompt/api_key.txt").read(),
    )

    files = [
        # Please ensure that the file is available in local system working direrctory or change the file path.
        client.files.upload(file=sys.argv[1])
    ]
    model = "gemini-2.5-flash-preview-04-17"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_uri(
                    file_uri=files[0].uri,
                    mime_type=files[0].mime_type,
                ),
                types.Part.from_text(text="""
                    Reformat the attached story according to the provided schema.
                """),
            ],
        ),
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

    # Find next available code file number
    i = 1
    while os.path.exists(f"code ({i}).txt"):
        i += 1
    output_file = f"code ({i}).txt"

    # Open file for writing
    with open(output_file, "w", errors='ignore') as f:
        # Generate content
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            # Write to file and print to console
            f.write(chunk.text)
            print(chunk.text, end="")

if __name__ == "__main__":
    generate()
