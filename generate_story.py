# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import json
import os
import sys
from google import genai
from google.genai import types


def generate(story_name, story_analysis, story_text):
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
                                     + story_text
                                     ),
            ],
        ),
        types.Content(
            role="model",
            parts=[
                types.Part.from_text(text="""Here's a breakdown of the thinking process used to generate the analysis of \"{story_name}\":

1.  **Deconstruct the Request:**
    *   **Core Task:** Analyze each sentence of the provided \"{story_name}\" story.
    *   **Guidance:** Use the knowledge from the \"Authors Guide short.md\".
    *   **Analysis Dimensions:** Relation to the whole story, morals, metaphorical/psychological meanings.
    *   **Structure:** A detailed, long essay structured in chapters, one chapter per sentence.
    *   **Source Text:** The provided text of \"{story_name}\".
    *   **Tone:** Detailed, analytical, drawing connections.

2.  **Initial Review & Planning:**
    *   **Read \"{story_name}\":** Get a fresh understanding of the plot, characters, and major themes. Identify key moments.
    *   **Review \"Authors Guide\":** Refresh understanding of Grimm stylistic elements (simple language, archetypes, structures, magic items, professions, morals, etc.). Pay special attention to the archetypes (Obvious and Subtle) and the Do's/Don'ts, as these provide the framework for analysis.
    *   **Plan the Structure:** The request explicitly states one chapter per sentence. This is straightforward but requires careful handling to avoid repetition and maintain flow. Each chapter needs to:
        *   Quote the sentence.
        *   Analyze its literal meaning within the plot.
        *   Connect it to the overall narrative arc.
        *   Analyze its adherence to Grimm style (language, structure).
        *   Explore moral implications based on the guide's criteria (reward/punishment, kindness, obedience, etc.).
        *   Delve into metaphorical/psychological meanings, heavily referencing the archetype guide (Ego, Shadow, Anima, Wise Old Man, Threshold Guardian, etc.).

4.  **Refining the Analysis:**

    *   **Connect Sentences:** Ensure each chapter builds on the previous one, showing the narrative and thematic progression. Avoid making each chapter entirely self-contained. Refer back to earlier sentences and forward to later outcomes.
    *   **Integrate Guide Concepts:** Explicitly use terms from the guide (archetypes, structures, stylistic elements) within the analysis of each sentence.
    *   **Depth of Psychology:** Apply the psychological analogues consistently. Don't just label; explain *how* the sentence/action reflects that concept.
    *   **Avoid Repetition:** While analyzing each sentence, find unique aspects or slightly different angles. If a theme repeats, analyze how *this specific sentence* contributes to or develops that theme.
    *   **Essay Flow:** Even though structured by sentence, try to create introductory and concluding remarks for the essay as a whole (though not explicitly requested, it makes it more cohesive). Ensure smooth transitions between chapters (sentences).

5.  **Final Review:**
    *   Read through the entire essay.
    *   Check for consistency in analysis and terminology.
    *   Ensure every sentence has been addressed.
    *   Verify that all aspects of the prompt (relation to story, morals, metaphor/psychology, use of guide) have been covered for each sentence.
    *   Proofread for grammar and clarity. Ensure the essay is \"long and detailed\" as requested.
"""),
                types.Part.from_text(text="Okay, I have read the Authors Guide and the story of \"{story_name}\" I will now proceed with the sentence-by-sentence analysis as requested, structuring it into chapters, each dedicated to one sentence. This analysis will weave together plot function, adherence to the Grimm style as outlined in the guide, moral implications, and metaphorical or psychological interpretations informed by the archetypes discussed."
                                     + story_analysis)
                                     
           ],
        ),
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=open("prompt/prompt_text.txt").read()),
                types.Part.from_text(text="""INSERT_INPUT_HERE"""),
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
    while os.path.exists(f"unprocessed code/code ({i}).txt"):
        i += 1
    output_file = f"unprocessed code/code ({i}).txt"

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

    output_file_prompt = f"unprocessed code/code ({i}) (prompt used).txt"
    with open(output_file_prompt, "w") as f:
        f.write(open("prompt/prompt_text.txt").read())

    return output_file, output_file_prompt

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            story_analysis = f.read()
            story_name = f.readline().strip()
            file = sys.argv[1]
    else:
        with open("seeds/seed (Iron John).txt") as f:
            story_analysis = f.read()
            story_name = f.readline().strip()
            file = "seeds/seed (Iron John).txt"
    
    with open(file, 'r', errors='replace') as f:
        data = json.load(f)
    
    story_name = data['The Complete Story']['Title']
    chapters = data['The Complete Story']['Chapters']

    story_text = ""
    for chapter in chapters:
        story_text += chapter
    
    output_file, output_file_prompt = generate(story_name, story_analysis, story_text)

    with open(output_file, 'r', errors='replace') as f:
        data = json.load(f)
    generated_story_name = data['The Complete Story']['Title']
    # Rename the files to contain the name of the story
    new_file_name = f"unprocessed code/code {generated_story_name}.txt"
    new_file_name_used = f"unprocessed code/code {generated_story_name} (prompt used).txt"
    os.rename(output_file, new_file_name)
    os.rename(output_file_prompt, new_file_name_used)
