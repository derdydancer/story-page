# Replace 'input.txt' with the path to your text file containing the stories
input_file = 'seeds\Grimm.txt'

# Read the input file
with open(input_file, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Extract story names from the first 63 lines
story_names = [line.strip() for line in lines[:63]]

# Create a dictionary to hold each story's content
stories = {name: [] for name in story_names}

# Iterate through the rest of the lines to extract story content
current_story = None
for line in lines[63:]:
    stripped_line = line.strip()
    if stripped_line in story_names:
        current_story = stripped_line
    elif current_story:
        stories[current_story].append(line)

# Write each story to its own file
for story_name, content in stories.items():
    # Replace invalid characters in filenames
    safe_story_name = "".join(c for c in story_name if c.isalnum() or c in " _-").strip()
    output_file = f"seeds\{safe_story_name}.txt"
    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(content)

print("Stories have been split into individual files.")