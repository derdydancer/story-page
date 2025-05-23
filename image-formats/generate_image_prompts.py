import json
import re

# --- Helper function to parse time-sensitive fields ---
def get_time_specific_description(description, chapter_num_int, total_chapters=40):
    if not isinstance(description, str):
        return description

    # Pattern 1: "X at start, aging to Y" (e.g., King Peter's age, Elder Prince's age)
    # Example: "Mid-forties at start, aging to late sixties, face deeply lined with sorrow."
    # Example: "Around ten years old at start, aging to a young man of early twenties."
    match_aging = re.match(r"^(.*?) at start, aging to (.*?)$", description, re.IGNORECASE)
    if match_aging:
        start_desc = match_aging.group(1).strip()
        end_desc = match_aging.group(2).strip()
        # If chapter is early, show start_desc. Otherwise (middle/late), show end_desc.
        if chapter_num_int <= total_chapters / 3:  # Threshold for "early"
            return start_desc
        else:
            return end_desc

    # Pattern 2: "Description, initially X, later Y" (e.g., Queen Anna's hair)
    # Example: "Long, wavy auburn hair, initially worn in elaborate updos..., later hangs loose..."
    match_init_later = re.match(r"^(.*?), initially (.*?), later (.*?)$", description, re.IGNORECASE)
    if match_init_later:
        base_desc = match_init_later.group(1).strip()
        initial_specific = match_init_later.group(2).strip()
        later_specific = match_init_later.group(3).strip()
        if chapter_num_int <= total_chapters / 2: # Threshold for initial vs later
            return f"{base_desc}, initially {initial_specific}"
        else:
            return f"{base_desc}, later {later_specific}"

    # Pattern 3: "Description with 'initially X then Y'" (more general than above)
    match_init_then = re.match(r"^(.*?), initially (.*?) then (.*?)$", description, re.IGNORECASE)
    if match_init_then:
        base_desc = match_init_then.group(1).strip()
        initial_specific = match_init_then.group(2).strip()
        then_specific = match_init_then.group(3).strip()
        if chapter_num_int <= total_chapters / 2:
            return f"{base_desc}, initially {initial_specific}"
        else: # For "then" it implies a sequence, so later chapters use the "then" part.
            return f"{base_desc}, then {then_specific}"
            
    # Pattern 4: Standalone "Initially X, later Y" or "X initially, later Y" (e.g. some facial features)
    match_facial_simple = re.match(r"^(.*?) initially, later (.*?)$", description, re.IGNORECASE)
    if match_facial_simple:
        initial_facial = match_facial_simple.group(1).strip()
        later_facial = match_facial_simple.group(2).strip()
        if chapter_num_int <= total_chapters / 2:
            return f"{initial_facial} initially." # Appends "initially" for clarity
        else:
            return f"{later_facial} later." # Appends "later" for clarity

    # Pattern 5: "Base description, later Y" (e.g., King Peter's hair changing color)
    # Example: "Shoulder-length brown hair, later mostly white..."
    match_base_later = re.match(r"^(.*?), later (.*?)$", description, re.IGNORECASE)
    if match_base_later:
        base_desc = match_base_later.group(1).strip()
        later_specific = match_base_later.group(2).strip()
        if chapter_num_int <= total_chapters / 2: # Early/Mid implies the base description before "later" applies
            return base_desc 
        else: # Late
            return f"{base_desc}, later {later_specific}"

    # Default: return original if no specific time-based pattern matches strongly
    return description

# --- Main script functions (modified from previous) ---
def get_character_details_for_chapter(character_name_from_chapter, characters_data, chapter_number_str, total_chapters_count):
    chapter_num_int = int(chapter_number_str)
    base_char_name = character_name_from_chapter.split(' (')[0].strip() # "Elder Prince (child)" -> "Elder Prince"
    
    character_info = None
    for char_def in characters_data:
        # Check against 'Character Names/Aliases' which might contain multiple names/aliases
        defined_names = [name.strip() for name in char_def['Character Names/Aliases'].split(' / ')]
        if base_char_name in defined_names:
            character_info = char_def
            break
            
    if not character_info:
        # Handle cases where a character in "Chapter Images" might not have a full definition
        # (e.g., "Royal Physicians", "Courtier")
        if base_char_name in ["Royal Physicians", "Courtier"]: # Example of minor characters
             return f"  {character_name_from_chapter}: (Minor character, generic appearance as per art style, context of the scene, and role as {base_char_name.lower()}).\n"
        return f"    Details for {character_name_from_chapter} not found in character definitions.\n"

    details_str = f"  {character_name_from_chapter}:\n"
    
    age_desc = character_info.get('Age (exact)', 'N/A')
    details_str += f"    Age: {get_time_specific_description(age_desc, chapter_num_int, total_chapters_count)}\n"
    
    # Build: Assuming build changes are less explicitly patterned by "initially/later" in current data
    build_desc = character_info.get('Build (exact)', 'N/A')
    # Simple check for "becomes" or "develops" implies change over time.
    # For simplicity, the current get_time_specific_description doesn't parse this complex build change pattern
    # We will just use the full description as it often contains the full evolution.
    details_str += f"    Build: {build_desc}\n" 
    
    facial_desc = character_info.get('Facial features (exact)', 'N/A')
    details_str += f"    Facial features: {get_time_specific_description(facial_desc, chapter_num_int, total_chapters_count)}\n"
    
    hairstyle_desc = character_info.get('Hairstyle (exakt)', 'N/A') # Note: 'exakt' in input JSON
    details_str += f"    Hairstyle: {get_time_specific_description(hairstyle_desc, chapter_num_int, total_chapters_count)}\n"

    chosen_outfit_desc = "No specific outfit defined for this chapter or character state."
    if 'Outfits' in character_info:
        for outfit in character_info['Outfits']:
            worn_in_chapters_str = outfit.get('Worn in chapters', '')
            cleaned_worn_in_str = worn_in_chapters_str.split('(')[0].strip() # Remove "(implied)"
            chapter_list_for_outfit = [ch.strip() for ch in cleaned_worn_in_str.split(',') if ch.strip()]
            
            if chapter_number_str in chapter_list_for_outfit:
                chosen_outfit_desc = outfit.get('Visual description (detailed)', 'N/A')
                break
        # Fallback if no specific chapter match, and only one outfit, use it.
        if chosen_outfit_desc == "No specific outfit defined for this chapter or character state." and len(character_info['Outfits']) == 1:
             chosen_outfit_desc = character_info['Outfits'][0].get('Visual description (detailed)', 'N/A')

    details_str += f"    Outfit: {chosen_outfit_desc}\n"
    return details_str

def get_location_details(location_name_from_chapter, locations_data):
    location_info = None
    # Try exact match from 'Name' field in locations_data
    for loc_def in locations_data:
        if loc_def.get('Name') == location_name_from_chapter:
            location_info = loc_def
            break
    
    # If exact match not found, try partial match (e.g., "Royal Palace" for "Royal Palace courtyard")
    if not location_info:
        for loc_def in locations_data:
            if loc_def.get('Name') and loc_def['Name'] in location_name_from_chapter: 
                location_info = loc_def
                break 

    if not location_info:
        return (f"Detailed Description: Details for location '{location_name_from_chapter}' not found.\n"
                f"Props: N/A\n"
                f"Architectural Style: N/A\n")

    desc = location_info.get('Description', 'N/A')
    props = location_info.get('List of props present', 'N/A')
    arch_style = location_info.get('Architectural style (if any)', 'N/A')
    
    return (f"Detailed Description: {desc}\n"
            f"Props: {props}\n"
            f"Architectural Style: {arch_style}\n")

# Load the input JSON data
# In a real script, you would load from 'The_Sundered_Kingdom_and_the_Queens_Shadow_400_detailed.json'
# For this example, the JSON string is embedded directly
input_json_string = """
{
  "Chapter Images": [
    {
      "Chapter Number": "1",
      "Location": "Royal Palace courtyard",
      "Perspective": "Wide shot of the sunlit kingdom with the King, Queen, and their two young Princes standing together, smiling, suggesting peace and prosperity.",
      "Characters in image": [{"Character": "King Peter"}, {"Character": "Queen Anna"}, {"Character": "Elder Prince (child)"}, {"Character": "Younger Prince (child)"}]
    },
    {
      "Chapter Number": "2",
      "Location": "Palace Gardens",
      "Perspective": "Medium shot of Queen Anna walking alone in the lush palace gardens, her smile not reaching her eyes, a subtle shadow in her expression despite the beauty around her.",
      "Characters in image": [{"Character": "Queen Anna"}]
    },
    {
      "Chapter Number": "3",
      "Location": "Royal Court",
      "Perspective": "Interior shot of the royal court, where wise physicians are examining Queen Anna, who sits quietly. The King watches with a worried expression.",
      "Characters in image": [{"Character": "King Peter"}, {"Character": "Queen Anna"}, {"Character": "Royal Physicians"}]
    },
    {
      "Chapter Number": "4",
      "Location": "Queen's Chambers (Anna's)",
      "Perspective": "Close-up on Queen Anna's face as an old serving woman whispers to her, a flicker of desperate hope appearing in the Queen's eyes.",
      "Characters in image": [{"Character": "Queen Anna"}, {"Character": "Old Serving Woman"}]
    },
    {
      "Chapter Number": "5",
      "Location": "King's Study",
      "Perspective": "Evening scene in the King's study, lit by candlelight. Queen Anna stands before the King, her face pale but resolute, telling him of her plan.",
      "Characters in image": [{"Character": "King Peter"}, {"Character": "Queen Anna"}]
    },
    {
      "Chapter Number": "6",
      "Location": "Grand Council Chamber",
      "Perspective": "The King, with a heavy heart but clear resolve, grants Queen Anna's wish. She curtsies deeply, tears of relief in her eyes.",
      "Characters in image": [{"Character": "King Peter"}, {"Character": "Queen Anna"}]
    },
    {
      "Chapter Number": "7",
      "Location": "Shore / Quay",
      "Perspective": "Queen Anna, in plain travelling clothes, embraces her two young sons. The King watches with a heavy heart as she turns towards the waiting ship.",
      "Characters in image": [{"Character": "Queen Anna"}, {"Character": "King Peter"}, {"Character": "Elder Prince (child)"}, {"Character": "Younger Prince (child)"}]
    },
    {
      "Chapter Number": "8",
      "Location": "Desolate Shore",
      "Perspective": "Wide shot of the Queen's ship near a bleak, barren coastline with a single tall, black tower. Queen Anna is being rowed ashore in a small boat.",
      "Characters in image": [{"Character": "Queen Anna"}]
    },
    {
      "Chapter Number": "9",
      "Location": "Black Tower",
      "Perspective": "Queen Anna stands before the cloaked and hooded Sorcerer in a vast, dimly lit circular hall. His cold, keen eyes are visible.",
      "Characters in image": [{"Character": "Queen Anna"}, {"Character": "Sorcerer"}]
    },
    {
      "Chapter Number": "10",
      "Location": "Black Tower",
      "Perspective": "Close-up on Queen Anna's face as she feels a great weight lift from her spirit. Unseen by her, a thin thread of shadow unspools from her, tethering her to the tower.",
      "Characters in image": [{"Character": "Queen Anna"}, {"Character": "Sorcerer"}]
    },
    {
      "Chapter Number": "11",
      "Location": "Shore / Quay",
      "Perspective": "Queen Anna, radiant, holds a magnificent new crown. As she expresses delight, the crown's gems visibly dim. King Peter looks on with unease.",
      "Characters in image": [{"Character": "Queen Anna"}, {"Character": "King Peter"}, {"Character": "Elder Prince (child)"}, {"Character": "Younger Prince (child)"}, {"Character": "Courtier"}]
    },
    {
      "Chapter Number": "12",
      "Location": "Queen's Chambers (Anna's)",
      "Perspective": "Queen Anna gazes at a beloved silver locket, its surface clouding slightly. In another part of the palace, King Peter remembers tales of a Magic Mirror.",
      "Characters in image": [{"Character": "Queen Anna"}, {"Character": "King Peter"}]
    },
    {
      "Chapter Number": "13",
      "Location": "Castle Attics",
      "Perspective": "King Peter, in dusty, cobweb-filled attics, pulls a velvet cloth from a tall, narrow object, revealing a surface as dark as a midnight pool.",
      "Characters in image": [{"Character": "King Peter"}]
    },
    {
      "Chapter Number": "14",
      "Location": "Castle Attics",
      "Perspective": "King Peter speaks quietly to the dark mirror. Mists swirl within its depths, and an image of the desolate shore and black tower begins to form.",
      "Characters in image": [{"Character": "King Peter"}]
    },
    {
      "Chapter Number": "15",
      "Location": "Castle Attics",
      "Perspective": "Close-up on King Peter's horrified face as the mirror reveals Queen Anna's bargain with the Sorcerer. He staggers back, pale as ash.",
      "Characters in image": [{"Character": "King Peter"}]
    },
    {
      "Chapter Number": "16",
      "Location": "West Wing Chambers (Anna's initial confinement)",
      "Perspective": "Queen Anna in her comfortable but remote chambers, looking out a window. Her sons visit her, their faces showing distress at her distant manner.",
      "Characters in image": [{"Character": "Queen Anna"}, {"Character": "Elder Prince (youth)"}, {"Character": "Younger Prince (youth)"}]
    },
    {
      "Chapter Number": "17",
      "Location": "Royal Palace / Secluded Tower (Anna's final confinement)",
      "Perspective": "Split image: One side shows the Dark Forest of Thorns growing. The other shows the new Queen Petra suggesting the Royal Preserve be left undisturbed, while old Queen Anna watches the Elder Prince from her tower window.",
      "Characters in image": [{"Character": "King Peter"}, {"Character": "Queen Petra"}, {"Character": "Queen Anna"}, {"Character": "Elder Prince (young man)"}]
    },
    {
      "Chapter Number": "18",
      "Location": "Secluded Tower (Anna's final confinement)",
      "Perspective": "Old Queen Anna, frail but intense, whispers to her Elder Son about a secret in the Royal Preserve, her eyes gleaming faintly.",
      "Characters in image": [{"Character": "Queen Anna"}, {"Character": "Elder Prince (young man)"}]
    },
    {
      "Chapter Number": "19",
      "Location": "Royal Preserve (Moon-dappled Glade)",
      "Perspective": "The Elder Prince, in dark clothes, stands before a tall Wild Man clad in furs and leaves, near a great oak tree and mossy rock.",
      "Characters in image": [{"Character": "Elder Prince (young man)"}, {"Character": "Bard / Wild Man of the Preserve / Grove-King"}]
    },
    {
      "Chapter Number": "20",
      "Location": "Royal Preserve",
      "Perspective": "The Elder Prince sitting inside the dark hollow of an immense, gnarled oak tree, listening intently to the sounds of the forest.",
      "Characters in image": [{"Character": "Elder Prince (young man)"}]
    },
    {
      "Chapter Number": "21",
      "Location": "Royal Preserve",
      "Perspective": "The Elder Prince discovers the true source of a seemingly uphill-flowing stream: a small, hidden spring gushing from a rock cleft.",
      "Characters in image": [{"Character": "Elder Prince (young man)"}]
    },
    {
      "Chapter Number": "22",
      "Location": "Royal Preserve",
      "Perspective": "The Elder Prince kneels, a quiet joy on his face, looking at a tiny green shoot pushing up through cracked, dry earth where he planted a seed.",
      "Characters in image": [{"Character": "Elder Prince (young man)"}]
    },
    {
      "Chapter Number": "23",
      "Location": "Royal Preserve (Moon-dappled Glade)",
      "Perspective": "The Wild Man merges with an ancient oak tree and disappears, leaving the Elder Prince alone, pondering his final words about forgotten corners and reflecting truths.",
      "Characters in image": [{"Character": "Elder Prince (young man)"}, {"Character": "Bard / Wild Man of the Preserve / Grove-King"}]
    },
    {
      "Chapter Number": "24",
      "Location": "Castle Attics",
      "Perspective": "The Elder Prince stands before the mist-filled Magic Mirror, his hand on the velvet cloth, speaking to it with quiet firmness.",
      "Characters in image": [{"Character": "Elder Prince (young man)"}]
    },
    {
      "Chapter Number": "25",
      "Location": "Castle Attics",
      "Perspective": "The Magic Mirror shows the Elder Prince an image of his mother, Queen Anna, making the bargain with the Sorcerer. His face reflects shock and chilling understanding.",
      "Characters in image": [{"Character": "Elder Prince (young man)"}, {"Character": "Queen Anna (in vision)"}, {"Character": "Sorcerer (in vision)"}]
    },
    {
      "Chapter Number": "26",
      "Location": "King's Study",
      "Perspective": "The Elder Prince stands before King Peter, the weight of newfound knowledge in his eyes. The King looks weary but resigned.",
      "Characters in image": [{"Character": "Elder Prince (young man)"}, {"Character": "King Peter"}]
    },
    {
      "Chapter Number": "27",
      "Location": "Armory",
      "Perspective": "The Elder Prince tells the Younger Prince the terrible truth. The Younger Prince sits heavily on a bench, his sword clattering to the floor.",
      "Characters in image": [{"Character": "Elder Prince (young man)"}, {"Character": "Younger Prince (young man)"}]
    },
    {
      "Chapter Number": "28",
      "Location": "Solar (Queen Petra's)",
      "Perspective": "The two Princes recount the tale to Queen Petra, who listens with a still, compassionate face after sending her young children away.",
      "Characters in image": [{"Character": "Elder Prince (young man)"}, {"Character": "Younger Prince (young man)"}, {"Character": "Queen Petra"}]
    },
    {
      "Chapter Number": "29",
      "Location": "Secluded Tower (Anna's final confinement)",
      "Perspective": "The Elder Prince confronts Queen Anna. As she angrily denies his words, a single, long, black thorn appears on the stone floor between them, pulsing with dark light.",
      "Characters in image": [{"Character": "Elder Prince (young man)"}, {"Character": "Queen Anna"}]
    },
    {
      "Chapter Number": "30",
      "Location": "Secluded Tower (Anna's final confinement)",
      "Perspective": "During the Elder Prince's second confrontation, the clear water in a clay pitcher on Queen Anna's table turns cloudy and brackish. She turns away, a tear on her cheek.",
      "Characters in image": [{"Character": "Elder Prince (young man)"}, {"Character": "Queen Anna"}]
    },
    {
      "Chapter Number": "31",
      "Location": "Secluded Tower (Anna's final confinement)",
      "Perspective": "Queen Anna, pale and still, finally whispers, \\\"It is true. My selfishness... it wounded all of you.\\\" A faint sliver of sunlight touches her face for an instant.",
      "Characters in image": [{"Character": "Elder Prince (young man)"}, {"Character": "Queen Anna"}]
    },
    {
      "Chapter Number": "32",
      "Location": "Royal Preserve",
      "Perspective": "The Elder Prince stands before a slender tree glowing with soft inner light. A single, perfect apple, the color of moonlight on snow, materializes on a branch.",
      "Characters in image": [{"Character": "Elder Prince (young man)"}]
    },
    {
      "Chapter Number": "33",
      "Location": "Royal Preserve (Sacred Grove)",
      "Perspective": "The Elder Prince, holding the luminous silver-white apple, enters a hidden, sun-dappled grove where the air is sweet and the light is golden.",
      "Characters in image": [{"Character": "Elder Prince (young man)"}]
    },
    {
      "Chapter Number": "34",
      "Location": "Royal Preserve (Sacred Grove)",
      "Perspective": "The Elder Prince stands breathless before Princess Cut-a-tree-na-na, who stands beside a magnificent, ancient tree with silver bark and rainbow leaves.",
      "Characters in image": [{"Character": "Elder Prince (young man)"}, {"Character": "Princess Cut-a-tree-na-na"}]
    },
    {
      "Chapter Number": "35",
      "Location": "Royal Preserve (Sacred Grove)",
      "Perspective": "The Elder Prince carefully loosens a clinging, shadowy vine from an ancient, carved stone, guiding it towards a propped branch. Sunlight falls on the stone.",
      "Characters in image": [{"Character": "Elder Prince (young man)"}]
    },
    {
      "Chapter Number": "36",
      "Location": "Royal Preserve (Sacred Grove)",
      "Perspective": "The Elder Prince, using his hands and bark, creates a new channel for a trickle of water to flow around a fallen log towards a parched streambed.",
      "Characters in image": [{"Character": "Elder Prince (young man)"}]
    },
    {
      "Chapter Number": "37",
      "Location": "Royal Preserve (Sacred Grove)",
      "Perspective": "A small, exquisitely colored bird, perched on a flowering bush, looks at the Elder Prince and lets out a clear, joyful song. The Prince sits patiently nearby.",
      "Characters in image": [{"Character": "Elder Prince (young man)"}]
    },
    {
      "Chapter Number": "38",
      "Location": "Royal Preserve (Sacred Grove)",
      "Perspective": "Princess Cut-a-tree-na-na places her hand in the Elder Prince's. Behind them, the great tree shimmers, and the old Bard steps forth in regal robes.",
      "Characters in image": [{"Character": "Elder Prince (young man)"}, {"Character": "Princess Cut-a-tree-na-na"}, {"Character": "Bard / Wild Man of the Preserve / Grove-King"}]
    },
    {
      "Chapter Number": "39",
      "Location": "Royal Preserve (Sacred Grove)",
      "Perspective": "The Bard-King, now revealed as the Grove-King and Cut-a-tree-na-na's father, smiles gently at the astonished Elder Prince.",
      "Characters in image": [{"Character": "Elder Prince (young man)"}, {"Character": "Princess Cut-a-tree-na-na"}, {"Character": "Bard / Wild Man of the Preserve / Grove-King"}]
    },
    {
      "Chapter Number": "40",
      "Location": "The Kingdom / Royal Preserve",
      "Perspective": "Split perspective: The Elder Prince and Princess Cut-a-tree-na-na stand together, a beacon of hope. Separately, the Younger Prince walks thoughtfully towards the Royal Preserve.",
      "Characters in image": [{"Character": "Elder Prince (young man)"}, {"Character": "Princess Cut-a-tree-na-na"}, {"Character": "Younger Prince (young man)"}]
    }
  ],
  "Characters": [
    {
      "Age (exact)": "Mid-forties at start, aging to late sixties, face deeply lined with sorrow.",
      "Build (exact)": "Stands 6 feet tall, broad-shouldered, becomes slightly stooped with sorrow.",
      "Character Names/Aliases": "King / King Peter",
      "Facial features (exact)": "Square jaw, deep-set grey eyes under heavy brows, initially a ruddy complexion that pales with worry; a neatly trimmed brown beard that greys to white over time.",
      "Hairstyle (exakt)": "Shoulder-length brown hair, later mostly white, often held back by a thin gold circlet with a single inset sapphire.",
      "Outfits": [
        {
          "Visual description (detailed)": "Royal robes of deep sapphire blue velvet, the edges embroidered with gold thread in intricate patterns of sunbursts and oak leaves, worn over a cream-colored fine linen tunic. A heavy gold chain of office with a lion-head pendant rests on his chest.",
          "Worn in chapters": "1, 3, 5, 6, 11, 12, 13, 14, 15, 16, 17, 26, 28 (implied)"
        },
        {
          "Visual description (detailed)": "Private attire: A simple dark wool doublet of forest green, high-necked, fastened with five plain polished silver buttons, worn with dark brown trousers of sturdy twill.",
          "Worn in chapters": "5, 12, 13, 14, 15, 26"
        }
      ]
    },
    {
      "Age (exact)": "Early thirties at start, appears mid-fifties in confinement, frail in her late sixties.",
      "Build (exact)": "Stands 5 feet 7 inches, slender, willowy frame which becomes gaunt and fragile over time.",
      "Character Names/Aliases": "Queen / Queen Anna / Old Queen Anna",
      "Facial features (exact)": "Oval face, large expressive hazel eyes that lose their sparkle and become shadowed, a delicate, straight nose, lips that thin with persistent sadness. Her skin is like pale ivory, later almost translucent.",
      "Hairstyle (exakt)": "Long, wavy auburn hair, initially worn in elaborate updos secured with pearl-tipped pins, later hangs loose and unadorned, streaked with dull grey strands.",
      "Outfits": [
        {
          "Visual description (detailed)": "Royal Gown (early chapters): A flowing gown of sea-foam green silk, with wide, dagged sleeves lined with cream satin, and a silver girdle intricately worked with moonstones.",
          "Worn in chapters": "1, 2, 3, 4, 5, 6"
        },
        {
          "Visual description (detailed)": "Travelling Clothes: A practical, hooded cloak of dark grey, heavy wool, fastened with a simple bronze clasp, worn over a simple calf-length tunic of undyed, coarse linen and sturdy, dark brown leather boots laced to mid-calf.",
          "Worn in chapters": "7, 8, 9, 10"
        },
        {
          "Visual description (detailed)": "Return Gown: A gown of bright golden yellow damask, with intricate gold thread embroidery in a motif of intertwined roses and thorns at the wide neckline and cuffs.",
          "Worn in chapters": "11"
        },
        {
          "Visual description (detailed)": "Confinement Attire: A loose-fitting, high-necked gown of faded lavender-grey linen, devoid of any adornment, the fabric thin from wear.",
          "Worn in chapters": "12, 16, 17, 18, 29, 30, 31"
        }
      ]
    },
    {
      "Age (exact)": "Around ten years old at start, grows into a young man of early twenties.",
      "Build (exact)": "Average height as a child, grows to 5 feet 11 inches, with a lean and athletic physique.",
      "Character Names/Aliases": "Elder Prince",
      "Facial features (exact)": "A high forehead suggesting thoughtfulness, keen, intelligent brown eyes, a defined jawline. Develops a quiet strength and resolute expression as he matures.",
      "Hairstyle (exakt)": "Dark brown, wavy hair, kept neatly trimmed as a child, slightly longer and often tucked behind his ears as a young man.",
      "Outfits": [
        {
          "Visual description (detailed)": "Princely Attire (child/youth): A tunic of forest green wool, reaching mid-thigh, belted with a tooled brown leather belt with a simple brass buckle, worn with dark grey hose and soft, ankle-high leather shoes.",
          "Worn in chapters": "1, 7, 11, 16"
        },
        {
          "Visual description (detailed)": "Preserve Attire: A close-fitting jerkin of dark brown, almost black, rough-spun wool over a dark grey linen shirt, faded brown breeches tucked into scuffed, knee-high dark leather boots. A small, plain steel hunting knife with a smooth wooden handle is sheathed in a leather scabbard at his belt.",
          "Worn in chapters": "18, 19, 20, 21, 22"
        },
        {
          "Visual description (detailed)": "Mature Princely Attire: A tailored doublet of deep crimson brocade patterned with small, repeating silver falcons, fastened with five silver clasps, over a fine white linen shirt with ruffled cuffs, dark grey fitted trousers, and polished black riding boots.",
          "Worn in chapters": "23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40"
        }
      ]
    },
    {
      "Age (exact)": "Around eight years old at start, grows into a young man in his late teens/early twenties.",
      "Build (exact)": "Slender as a child, develops a muscular, agile build from sword practice, standing around 5 feet 10 inches.",
      "Character Names/Aliases": "Younger Prince",
      "Facial features (exact)": "Quiet, watchful dark blue eyes, a firm mouth, often carries a solemn or observant expression. His complexion is fair.",
      "Hairstyle (exakt)": "Straight, dark blond hair, cut short and practical, often falling slightly over his brow.",
      "Outfits": [
        {
          "Visual description (detailed)": "Princely Attire (child/youth): A tunic of sky blue linen, with simple white cord embroidery at the V-neck collar and cuffs, belted with a woven blue and silver cord.",
          "Worn in chapters": "1, 7, 11, 16"
        },
        {
          "Visual description (detailed)": "Armory/Later Attire: A plain, dark brown leather jerkin, worn open over a sturdy, cream-colored linen shirt, practical dark grey trousers, and well-worn, calf-high leather boots. Often seen with a simple steel arming sword with a leather-wrapped grip and a plain cross-guard, either in hand or sheathed at his hip.",
          "Worn in chapters": "18 (implied overhearing), 27, 28, 40"
        }
      ]
    },
    {
      "Age (exact)": "Ageless, appears ancient and beyond human years.",
      "Build (exact)": "Tall, standing over 6 feet 2 inches, with an unnaturally thin, almost skeletal figure beneath his robes.",
      "Character Names/Aliases": "Sorcerer",
      "Facial features (exact)": "Completely obscured by a deep, pointed hood that falls far forward, except for two piercing, icy-blue eyes that seem to glow faintly in the dimness. The skin on his visible long-fingered hands is paper-thin, like old parchment, stretched tautly over prominent knuckles, with nails that are yellowed and overly long, slightly curved.",
      "Hairstyle (exakt)": "Entirely concealed by the deep hood.",
      "Outfits": [
        {
          "Visual description (detailed)": "Long, voluminous robes of a fabric that seems to shift in color between darkest charcoal grey and an oily black, with no visible seams, buttons, or adornment. The sleeves are wide and trail to the floor, and the deep cowl casts his face in permanent, impenetrable shadow.",
          "Worn in chapters": "9, 10, 15 (in vision), 25 (in vision)"
        }
      ]
    },
    {
      "Age (exact)": "Appears in her late seventies, with many years of service.",
      "Build (exact)": "Stooped from age and work, thin frame, standing about 5 feet 2 inches.",
      "Character Names/Aliases": "Old Serving Woman",
      "Facial features (exact)": "Face is a network of fine wrinkles like dried parchment, kind but worried eyes of faded hazel-brown, a few wisps of thin white hair escaping her cap. Her lips are often pursed with concern.",
      "Hairstyle (exakt)": "Mostly white hair, sparse and fine, pulled back into a tight, small bun at the nape of her neck, almost entirely covered by a simple, clean white linen coif tied under her chin.",
      "Outfits": [
        {
          "Visual description (detailed)": "A long-sleeved, ankle-length dress of coarse, dark brown wool, somewhat faded and worn at the elbows and hem. Over this, she wears a clean but carefully patched linen apron of a faded blue, tied around her waist with a simple cord.",
          "Worn in chapters": "4"
        }
      ]
    },
    {
      "Age (exact)": "Appears mid-fifties as Bard; his age seems indeterminate and ancient as Wild Man and Grove-King.",
      "Build (exact)": "As Bard: average height, about 5 feet 9 inches, with a wiry frame. As Wild Man/Grove-King: seems taller, more imposing, around 6 feet, with a surprisingly strong build.",
      "Character Names/Aliases": "Bard / Wild Man of the Preserve / Grove-King / Cut-a-tree-na-na's father",
      "Facial features (exact)": "As Bard: keen, observant grey eyes with prominent laugh lines at the corners, weathered skin tanned from travel, a slightly crooked nose. As Wild Man: face mostly hidden by tangled hair and beard, but his eyes are visible, like polished grey river stones, unblinking. As Grove-King: a noble, serene face, deeply wise grey eyes that hold a gentle light, skin has a faint, fine texture reminiscent of smooth tree bark.",
      "Hairstyle (exakt)": "As Bard: grey-streaked dark brown hair, medium length, somewhat untidy and windblown. As Wild Man: long, matted dark brown hair and a full beard interwoven with small twigs, dried leaves, and moss. As Grove-King: flowing silver-grey hair reaching his shoulders and a neatly trimmed beard of the same color, with a simple crown of woven living ivy leaves with tiny, star-like white flowers intertwined.",
      "Outfits": [
        {
          "Visual description (detailed)": "As Bard: A knee-length cloak made of many mismatched, overlapping patches of faded wool in earthy tones (moss green, russet brown, ochre yellow, faded blue), stitched with thick, visible thread. Worn over a simple brown linen tunic and dark trousers. Carries a dark wood lute with a rounded body, its strings worn, and small mother-of-pearl dots inlaid around the soundhole.",
          "Worn in chapters": "12 (mentioned), 16 (mentioned), 37 (melodies recalled), 38 (revealed)"
        },
        {
          "Visual description (detailed)": "As Wild Man: A roughly fashioned tunic and leggings crudely stitched together from various animal furs (patches of reddish deer hide, soft grey rabbit fur, tawny fox fur) and interwoven with strips of dried leaves and pieces of flexible tree bark.",
          "Worn in chapters": "19, 20, 21, 22, 23"
        },
        {
          "Visual description (detailed)": "As Grove-King: Robes of a flowing, self-patterned fabric that shifts in color from deep forest green to shimmering silver, like moonlight on wet leaves. The fabric seems to have a texture of fine veins, like a leaf. Wears the crown of woven living ivy leaves.",
          "Worn in chapters": "38, 39"
        }
      ]
    },
    {
      "Age (exact)": "Appears in her late thirties, exuding a calm maturity.",
      "Build (exact)": "Stands 5 feet 6 inches, with a gentle, somewhat rounded figure suggesting comfort rather than frailty.",
      "Character Names/Aliases": "Queen Petra / New Queen",
      "Facial features (exact)": "A calm, kind face with warm, deep-set brown eyes, a soft mouth that often curves into a gentle, understanding smile. Her complexion is fair with a dusting of light freckles across the bridge of her nose and cheeks.",
      "Hairstyle (exakt)": "Light brown hair, thick and with a slight wave, neatly braided into a single plait that is then coiled at the back of her head, sometimes adorned with a simple dark blue ribbon woven through it.",
      "Outfits": [
        {
          "Visual description (detailed)": "A high-waisted gown of soft, cornflower-blue wool, with long, fitted sleeves that end in a slight point over the hand. The neckline is a simple, rounded scoop. She wears a plain silver circlet, about half an inch wide, in her hair. Her only jewelry is a small, carved wooden pendant in the shape of a dove, hanging from a leather thong.",
          "Worn in chapters": "17, 28"
        }
      ]
    },
    {
      "Age (exact)": "Appears as a young woman of timeless grace, perhaps early twenties in human terms.",
      "Build (exact)": "Slender and willowy, standing 5 feet 8 inches. She moves with an effortless grace, like a sapling swaying in a gentle breeze.",
      "Character Names/Aliases": "Princess Cut-a-tree-na-na",
      "Facial features (exact)": "An oval face of ethereal quality, with large eyes the precise color of clear spring water just after a rain, fringed with long, dark lashes. Her skin seems to possess a faint inner luminosity, like alabaster lit from within. Her lips are naturally rose-tinted, and her expression is one of gentle wisdom and fearless compassion.",
      "Hairstyle (exakt)": "Very long, dark brown hair, like polished walnut wood, that falls in soft, natural waves almost to her knees. It is unbound and unadorned, save for perhaps a few tiny, star-like wildflowers unknowingly caught in its lengths.",
      "Outfits": [
        {
          "Visual description (detailed)": "A simple, flowing gown made of a fabric that resembles fresh, young leaves, in varying shades of spring green from pale lime to deep emerald. The gown seems to have no visible seams, as if it were grown rather than sewn, and it drapes around her in soft folds, ending at her bare feet.",
          "Worn in chapters": "33, 34, 35 (watching), 36 (watching), 37 (watching), 38, 39, 40"
        }
      ]
    }
  ],
  "Locations": [
    {
      "Description": "A sprawling stone castle complex constructed of grey granite blocks. It features a central keep that is three stories high, topped with a single, tall round tower (the King's private tower, an additional two stories). Four shorter, square corner towers, each two stories high with narrow arched windows (one every 10 feet horizontally on each floor), punctuate the main rectangular curtain wall which is 30 feet high. The main gate is a heavy, iron-banded oak double door, 15 feet high, set within a massive rounded archway, and is flanked by two squat, D-shaped guard towers integrated into the wall.",
      "List of props present": "Heavy, dark red velvet curtains hanging in main halls, often faded and slightly dusty; several polished dark oak tables (rectangular, 8 feet long) and numerous high-backed chairs with carved lion heads on the armrests; multiple wrought iron candelabras, each holding seven thick beeswax candles; large, faded tapestries (10 feet by 15 feet) depicting heroic scenes such as 'The Slaying of the Crimson Gryphon' and 'The Founding of the Kingdom by King Alaric'.",
      "Name": "Royal Palace",
      "Architectural style (if any)": "A blend of Norman keep architecture (massive stone walls, rounded arches) with later Gothic elements (taller towers, more refined window tracery in some sections)."
    },
    {
      "Description": "A rectangular walled garden, approximately two acres in size, adjacent to the west wing of the Royal Palace. It is enclosed by a 10-foot high stone wall. Neatly trimmed boxwood hedges, 3 feet high, form intricate knot garden patterns and define pathways around circular rose beds (containing deep red 'King's Ransom', pure white 'Moonbeam', and pale yellow 'Sun's Kiss' roses). A central stone fountain, 8 feet in diameter, depicts three intricately carved stone dolphins spouting water into a wide, shallow basin. Several weathered grey stone benches, their surfaces covered in fine moss, are placed in secluded alcoves formed by yew hedges.",
      "List of props present": "Numerous rose bushes with vibrant red, white, and yellow blooms; pathways of fine, light grey gravel in intricate patterns; moss-covered grey stone benches with curved backs; the three-dolphin stone fountain with clear water." ,
      "Name": "Palace Gardens",
      "Architectural style (if any)": "Formal Renaissance-inspired garden design with symmetrical layouts and sculpted topiary elements."
    },
    {
      "Description": "A circular room, 20 feet in diameter, located within the King's private tower at the top of the central keep. The curved walls are lined from floor to ceiling with tall, dark oak bookshelves crammed with leather-bound volumes. A single, large arched window, 8 feet high, offers a panoramic view of the kingdom. A large, unlit stone fireplace with a carved stone mantelpiece depicting hunting scenes dominates one section of the curved wall.",
      "List of props present": "A massive, carved oak desk (6 feet long, 3 feet wide) covered with rolled parchments tied with faded red ribbons, several open books bound in dark brown and black leather with faded gold lettering, a tarnished brass astrolabe on a wooden stand, a heavy pewter inkwell with a single white goose quill pen resting beside it, a single tall silver candelabra with three flickering beeswax candles.",
      "Name": "King's Study",
      "Architectural style (if any)": "Romanesque tower interior with thick stone walls and deep-set windows, oak paneling on lower walls."
    },
    {
      "Description": "A long, high-ceilinged hall (the Great Hall), 80 feet long and 40 feet wide, with a vaulted timber roof supported by massive oak beams. The floor is made of polished stone flags in alternating dark grey and light cream squares. Tall, narrow stained-glass windows (each 10 feet high, depicting royal crests and stylized mythical beasts like griffins and unicorns) line one long wall, casting shifting patterns of colored light onto the floor. At the far end, a raised dais of three shallow stone steps supports two large, carved oak thrones.",
      "List of props present": "Two imposing thrones of dark, weathered oak, intricately carved with motifs of lions and eagles, with deep crimson velvet cushions; long banners (6 feet long) hanging from the rafters between the beams, displaying the kingdom's sigil (a golden rampant lion on a deep blue field); several rows of simple, backless wooden benches, each 10 feet long, for courtiers.",
      "Name": "Royal Court",
      "Architectural style (if any)": "Early Gothic hall with a high vaulted ceiling, timber hammer-beam roof structure, and lancet-style stained-glass windows."
    },
    {
      "Description": "A suite of two interconnected rooms (a sitting room and a bedchamber) in the main palace keep, each approximately 20 feet square. The sitting room has a large arched window, 6 feet high, with a padded window seat upholstered in faded rose damask, looking out over the Palace Gardens. The walls are hung with pale blue silk tapestries depicting idyllic pastoral scenes of shepherds and shepherdesses.",
      "List of props present": "In the bedchamber: a four-poster bed of dark oak, draped with embroidered cream linen curtains showing patterns of twining ivy; a polished maplewood dressing table with an oval silver-backed mirror and several small, stoppered crystal perfume bottles; a small, unlit stone fireplace with a simple mantel; a small, heart-shaped silver locket with delicate floral engravings resting on a mahogany bedside table next to a single, unlit beeswax candle in a brass holder.",
      "Name": "Queen's Chambers (Anna's)",
      "Architectural style (if any)": "Comfortable Gothic interior with plastered walls, timber-beamed ceilings, and stone window frames."
    },
    {
      "Description": "A rectangular room, 30 feet by 20 feet, with dark oak-paneled walls reaching halfway up, the upper walls plastered and painted a deep wine red. A very long, heavy oak table, 15 feet in length and 4 feet wide, occupies the center of the room, surrounded by twelve high-backed, carved wooden chairs. A large, detailed map of the kingdom, hand-drawn on aged parchment (5 feet by 4 feet), is pinned to one wall with small iron tacks.",
      "List of props present": "The long oak table with a slightly scarred and ink-stained surface; twelve chairs with seats and backs upholstered in dark green tooled leather, studded with brass nails; a tarnished brass globe, 2 feet in diameter, on a carved wooden stand in one corner; a heavy silver water pitcher and twelve matching silver goblets on a small oak side table.",
      "Name": "Grand Council Chamber",
      "Architectural style (if any)": "Manorial Gothic style with wood paneling and a sense of formal gravity."
    },
    {
      "Description": "A vast, low-ceilinged space directly under the castle's main roof, approximately 100 feet long and 60 feet wide, with exposed, rough-hewn wooden support beams thick with grey, trailing cobwebs. Dust motes dance in the few shafts of pale light filtering in from small, round, grimy glass windows set into the sloping roof. The floor is made of bare, uneven, and extremely dusty wooden planks that creak underfoot.",
      "List of props present": "Stacks of five disused, dented steel shields leaning against a stone support pillar; three large, locked wooden chests bound with rusted iron bands; various pieces of furniture covered in thick white dust sheets (e.g., a tall harp with several broken strings, a child's faded wooden rocking horse with one missing eye); several rolls of faded, moth-eaten tapestries depicting forgotten battles, leaning in a corner; the Magic Mirror: a tall, narrow rectangle of glass (4 feet high, 2 feet wide) that appears as dark and unreflective as polished obsidian, set in a simple, heavily tarnished silver frame, and entirely covered by a heavy, dark purple velvet cloth, also coated in dust.",
      "Name": "Castle Attics",
      "Architectural style (if any)": "Utilitarian medieval roof space with rough timber framing and minimal finishing."
    },
    {
      "Description": "A series of three interconnected rooms in a less frequented part of the palace, each about 15 feet square. These rooms receive less direct sunlight due to their northern aspect. Windows are smaller than in the main palace (3 feet high, 2 feet wide) and are barred with simple, vertical iron rods. Furnishings are serviceable but plainer than her original chambers, lacking personal touches.",
      "List of props present": "A simple wooden bed frame with plain, undyed linen bedding and a single thin woolen blanket; a small, unadorned square wooden table and one matching straight-backed chair; a single, unlit three-branched iron candelabra on the table; bare, plastered walls painted a dull grey.",
      "Name": "West Wing Chambers (Anna's initial confinement)",
      "Architectural style (if any)": "Simplified Gothic, functional and somewhat stark."
    },
    {
      "Description": "A solitary, circular stone tower, approximately 15 feet in internal diameter and 50 feet tall, constructed of rough, dark grey stones. It stands at the furthest western edge of the palace grounds, with its few windows directly overlooking the encroaching Dark Forest of Thorns. It has three narrow, slit-like arrow-loop windows, each only 6 inches wide and 2 feet high, set very high in the walls. A single heavy, planked wooden door, reinforced with iron bands and a large iron ring handle, is the only entrance. The interior is one stark, circular room with a cold, uneven flagstone floor and bare stone walls.",
      "List of props present": "A narrow straw-filled pallet on the stone floor for a bed, covered with a single, thin grey blanket; a small, rough-hewn three-legged wooden stool; a chipped, unglazed clay pitcher containing murky water, resting on the floor; later, a single black thorn, three inches long, sharply pointed and slightly glistening, lying directly on the stone floor between the door and the pallet; the water in the pitcher becomes cloudy and brackish.",
      "Name": "Secluded Tower (Anna's final confinement)",
      "Architectural style (if any)": "Austere Romanesque defensive tower, repurposed."
    },
    {
      "Description": "A bright, airy room on an upper floor of the palace, approximately 25 feet by 20 feet, with a large, south-facing bay window composed of many small, leaded panes of clear glass. The walls are plastered and painted a light, cheerful yellow. The floor is covered with a woven rush mat patterned with simple green and brown stripes.",
      "List of props present": "Three comfortable armchairs upholstered in a floral patterned chintz (roses and bluebells); a small, light-colored maplewood harp with carved floral details on its pillar, leaning against a wall; a low, round oak table strewn with children's wooden toys (e.g., a brightly painted red and blue toy soldier, a roughly carved wooden rabbit, a set of nine wooden building blocks).",
      "Name": "Solar (Queen Petra's)",
      "Architectural style (if any)": "Late Gothic domestic interior, designed for light and comfort."
    },
    {
      "Description": "A long, rectangular room (50 feet by 20 feet) located in the castle basement, with rough stone walls and a low, arched ceiling. The air is cool and smells faintly of oil and old leather. The floor is packed earth, heavily scuffed and marked from practice drills.",
      "List of props present": "Wooden weapon racks lining the walls, holding various steel swords (longswords with cruciform hilts, shorter arming swords), several round and kite-shaped wooden shields with faded painted heraldry, and a few practice blunts; two practice dummies made of straw stuffed into old leather jerkins, mounted on wooden stands; a single long wooden bench against one wall.",
      "Name": "Armory",
      "Architectural style (if any)": "Utilitarian Romanesque undercroft or basement."
    },
    {
      "Description": "A realm characterized by rolling green hills, interspersed with small farming villages consisting of timber-framed cottages with steeply pitched, dark brown thatched roofs. Winding dirt roads, often muddy, connect these settlements. Initially, the fields surrounding the villages are golden with ripe wheat or green with young crops; later, these colors become muted, fields appear poorly tended, and a general air of neglect and dimness pervades the landscape.",
      "List of props present": "Distant views of small villages with thin plumes of grey smoke rising from stone chimneys; fields of wheat (initially golden, later dull brown or greyish) or fallow ground with sparse, weedy growth; a winding dirt road with deep ruts.",
      "Name": "The Kingdom",
      "Architectural style (if any)": "Rural medieval European vernacular architecture for villages."
    },
    {
      "Description": "A simple wooden pier, about 50 feet long and 10 feet wide, constructed of weathered grey timbers, extending into a grey, choppy sea. The shoreline itself is a mixture of coarse, dark grey sand and smooth, rounded dark pebbles of various sizes. The air smells of salt and damp wood.",
      "List of props present": "Thick, weathered wooden pilings supporting the pier, some encrusted with barnacles; several coils of thick, tarred hemp rope lying on the pier deck; a few empty, weathered wooden fish barrels stacked near the shore end of the pier.",
      "Name": "Shore / Quay",
      "Architectural style (if any)": "Basic timber pier construction."
    },
    {
      "Description": "A single-masted wooden sailing ship, approximately 60 feet in length from bow to stern, with a beam of 15 feet. It features a raised sterncastle and a smaller forecastle. Its hull is carvel-built and painted a dark, dull blue, showing signs of wear and salt stains. Its single large square sail is made of heavy, patched canvas, a faded tan color.",
      "List of props present": "Dark, weathered wooden deck planks, visibly worn; thick hemp ropes coiling on deck or running through wooden blocks; a simple wooden ship's wheel at the stern, about 3 feet in diameter; a small, cramped cabin below deck with a narrow wooden bunk built into the hull.",
      "Name": "Queen's Ship",
      "Architectural style (if any)": "Fantastical interpretation of a medieval cog or small carrack."
    },
    {
      "Description": "A narrow strip of coarse, black volcanic sand, perhaps 30 feet wide, at the foot of jagged, dark grey cliffs that rise sharply to about 100 feet. The sea here is a tumultuous, dark grey, constantly crashing against sharp, black basaltic rocks that litter the shoreline and extend into the water.",
      "List of props present": "Black, gritty volcanic sand; sharp, dark grey rocks of varying sizes, some slick with green algae; pieces of driftwood, bleached almost white by sun and salt; a few scattered, sun-bleached bones of seabirds.",
      "Name": "Desolate Shore",
      "Architectural style (if any)": "None, a raw and untamed natural volcanic landscape."
    },
    {
      "Description": "A perfectly cylindrical tower constructed of smooth, seamless black stone that seems to absorb light, approximately 100 feet tall and 30 feet in diameter. It has no visible windows or battlements. A single, massive door of charred black wood, 10 feet high and 6 feet wide, deeply set into its base, is the only apparent entrance. The interior is a vast, circular hall, the full diameter of the tower, dimly lit by an unseen, diffuse grey light source. It has a cold, polished black stone floor and walls that curve upwards into shadow, seeming to absorb all sound, creating an oppressive silence.",
      "List of props present": "A single, unadorned chair made of what appears to be twisted, black, thorn-like wood, placed precisely in the center of the circular hall.",
      "Name": "Black Tower",
      "Architectural style (if any)": "Ominous, stark, minimalist dark fantasy architecture, possibly of magical construction due to its seamlessness."
    },
    {
      "Description": "An impenetrable, seemingly endless wall of twisted, gnarled blackish-purple thorny vines and dead-looking, skeletal trees. The thorns are viciously sharp, some as long as a man's finger, and glisten with a faint, oily sheen. The ground beneath this barrier is barren, cracked, dark earth. The forest emits a palpable chill and a faint, sour odor.",
      "List of props present": "Countless viciously sharp, long black thorns, often hooked; tangled, leafless branches forming a dense lattice; dark, cracked earth with no undergrowth.",
      "Name": "Dark Forest of Thorns",
      "Architectural style (if any)": "None, a malevolent, magically-influenced natural growth."
    },
    {
      "Description": "An ancient, sprawling forest with a crumbling, moss-covered dry-stone wall, about 6 feet high in places but often lower or breached, marking its ill-defined boundary. Inside, massive, gnarled oak and beech trees, hundreds of years old, create a dense, shadowy canopy. The air is consistently cool and smells strongly of damp earth, decaying leaves, and fungi. The forest floor is thick with leaf litter. Hidden within are small, sun-dappled glades, winding streams with mossy banks, and rocky defiles where the ground drops away sharply.",
      "List of props present": "Ancient gnarled oak trees with wide trunks and hollows at their bases; large, moss-covered granite boulders scattered throughout; streams with clear water running over pebbly beds, or in one case, an illusionary uphill flow created by cunningly shaped rocks and channels; a patch of cracked, dry, barren earth near the Dark Forest's edge, about 20 feet square.",
      "Name": "Royal Preserve",
      "Architectural style (if any)": "None, an ancient, wild, and minimally disturbed natural temperate forest."
    },
    {
      "Description": "A small, roughly circular clearing within the Royal Preserve, approximately 50 feet across. Moonlight, when present, filters through the high canopy of surrounding ancient trees, creating shifting, dappled patterns of silver light and deep shadow on the mossy ground. A large, flat-topped granite boulder, about 4 feet high and 6 feet across, its surface almost entirely covered in dark green moss, sits near the center of the glade. Beside it stands an immense, ancient oak tree, its bark deeply furrowed and grey, with massive, exposed roots like grasping claws.",
      "List of props present": "The flat-topped granite boulder covered in dark green, velvety moss; the immense oak tree with deeply furrowed bark and exposed, gnarled roots.",
      "Name": "Royal Preserve (Moon-dappled Glade)",
      "Architectural style (if any)": "None, a natural clearing within an old-growth forest."
    },
    {
      "Description": "A perfectly circular grove, perhaps 100 yards in diameter, located in the deepest, most hidden part of the Royal Preserve. It is filled with a soft, warm, golden light that seems to emanate from the air itself or from the flora within. The air is unusually warm and sweet with the scent of unknown, faintly luminescent white and pale blue flowers that grow in clusters on the forest floor. The central feature is a colossal, ancient tree, far larger than any other in the Preserve, with smooth, shimmering silver bark and leaves that constantly shift through all the colors of the rainbow. The ground is covered in soft, vibrant green moss.",
      "List of props present": "The great silver-barked tree with iridescent, rainbow-hued leaves; clusters of unknown, luminescent white and pale blue flowers; an ancient flat stone tablet (3 feet long by 2 feet wide) of dark grey stone, carved with intricate, swirling, unknown symbols, lying half in shadow, partially covered by a thick, clinging, shadowy vine with dark green, heart-shaped leaves and small, black berries; a dry streambed, about 3 feet wide, and a blockage formed by a massive, moss-covered fallen log (at least 4 feet in diameter) and a jumble of smaller, lichen-covered rocks; a flowering bush with delicate, bell-shaped white flowers and a small, vividly blue-and-gold songbird with dull, listless feathers, perched silently within it.",
      "Name": "Royal Preserve (Sacred Grove)",
      "Architectural style (if any)": "None, a magically enhanced, pristine natural sanctuary."
    }
  ],
  "Overall Artstyle": "detailed colorful early 20th century illustration style, reminiscent of Arthur Rackham or Edmund Dulac, with rich textures, soft lighting, and a fantastical yet grounded feel."
}
"""
data = json.loads(input_json_string)

overall_artstyle = data['Overall Artstyle']
all_characters_data = data['Characters']
all_locations_data = data['Locations']
chapter_images_data = data['Chapter Images']
total_chapters_in_story = len(chapter_images_data)

generated_prompts = []

for chapter_image in chapter_images_data:
    chapter_num_str = chapter_image['Chapter Number']
    location_name = chapter_image['Location']
    scene_perspective = chapter_image['Perspective']
    characters_in_scene_list = chapter_image.get('Characters in image', [])

    summary_intro = f"Image Summary for Chapter {chapter_num_str}: {scene_perspective}"
    if characters_in_scene_list:
        char_names_for_summary = ", ".join([entry['Character'] for entry in characters_in_scene_list])
        summary_intro += f" The scene features {char_names_for_summary}."
    else:
        summary_intro += " This scene primarily focuses on the location or an event without specific central characters."
    
    prompt_lines = [summary_intro + "\n"]
    prompt_lines.append(f"Overall Artstyle:\n{overall_artstyle}\n")

    prompt_lines.append(f"Location: {location_name}")
    location_details_str = get_location_details(location_name, all_locations_data)
    prompt_lines.append(location_details_str)

    if characters_in_scene_list:
        prompt_lines.append("Characters Present:")
        for char_entry in characters_in_scene_list:
            char_name = char_entry['Character']
            char_details_str = get_character_details_for_chapter(char_name, all_characters_data, chapter_num_str, total_chapters_in_story)
            prompt_lines.append(char_details_str)
    else:
        prompt_lines.append("Characters Present: None specified in this scene.\n")
        
    prompt_lines.append(f"Scene Details from Perspective Field (for emphasis):\n{scene_perspective}\n")
    
    full_prompt = "\n".join(prompt_lines)
    generated_prompts.append({
        "chapter_number": chapter_num_str,
        "prompt": full_prompt
    })

output_filename = "chapter_prompts_v2.json"
with open(output_filename, 'w') as f:
    json.dump(generated_prompts, f, indent=2)

print(f"Generated prompts saved to {output_filename}")

# Verification prints
if generated_prompts:
    print("\n--- Verification Samples ---")
    
    # Chapter 1: King Peter's Age
    prompt_ch1 = next((p for p in generated_prompts if p['chapter_number'] == '1'), None)
    if prompt_ch1 and "King Peter" in prompt_ch1['prompt']:
        kp_age_ch1 = re.search(r"King Peter:\s*Age: (.*?)\n", prompt_ch1['prompt'])
        if kp_age_ch1:
            print(f"Chapter 1 - King Peter's Age: \"{kp_age_ch1.group(1)}\"")

    # Chapter 26: King Peter's Age and Hairstyle
    prompt_ch26 = next((p for p in generated_prompts if p['chapter_number'] == '26'), None)
    if prompt_ch26 and "King Peter" in prompt_ch26['prompt']:
        kp_age_ch26 = re.search(r"King Peter:\s*Age: (.*?)\n", prompt_ch26['prompt'])
        kp_hair_ch26 = re.search(r"King Peter:\s*.*?Hairstyle: (.*?)\n", prompt_ch26['prompt'], re.DOTALL)
        if kp_age_ch26:
            print(f"Chapter 26 - King Peter's Age: \"{kp_age_ch26.group(1)}\"")
        if kp_hair_ch26:
            print(f"Chapter 26 - King Peter's Hairstyle: \"{kp_hair_ch26.group(1)}\"")

    # Chapter 18: Elder Prince Age and Queen Anna Hair
    prompt_ch18 = next((p for p in generated_prompts if p['chapter_number'] == '18'), None)
    if prompt_ch18:
        if "Elder Prince (young man)" in prompt_ch18['prompt']:
            ep_age_ch18 = re.search(r"Elder Prince \(young man\):\s*Age: (.*?)\n", prompt_ch18['prompt'])
            if ep_age_ch18:
                print(f"Chapter 18 - Elder Prince's Age: \"{ep_age_ch18.group(1)}\"")
        if "Queen Anna" in prompt_ch18['prompt']:
             qa_hair_ch18 = re.search(r"Queen Anna:\s*.*?Hairstyle: (.*?)\n", prompt_ch18['prompt'], re.DOTALL)
             if qa_hair_ch18:
                print(f"Chapter 18 - Queen Anna's Hairstyle: \"{qa_hair_ch18.group(1)}\"")


    # Chapter 3: Handling of "Royal Physicians"
    prompt_ch3 = next((p for p in generated_prompts if p['chapter_number'] == '3'), None)
    if prompt_ch3 and "Royal Physicians" in prompt_ch3['prompt']:
        rp_desc_ch3 = re.search(r"Royal Physicians:\s*\((.*?)\)\.", prompt_ch3['prompt'])
        if rp_desc_ch3:
            print(f"Chapter 3 - Royal Physicians: \"{rp_desc_ch3.group(1)}\"")
    
    # Check the summary sentence
    print(f"\nChapter 1 - Summary section:\n{generated_prompts[0]['prompt'].splitlines()[0]}")

else:
    print("No prompts were generated.")