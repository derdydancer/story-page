import glob
import json
import html
import os
import shutil

# Function to sanitize title for filename and folder name
def sanitize_title(title):
    return ''.join(c for c in title if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')

# HTML template for story pages with title as h1
story_html_template = '''
<html>
<head>
<title>{title}</title>
<style>
body {{
    font-family: Arial, sans-serif;
    font-size: 16px;
    margin: 0;
}}
.container {{
    display: grid;
    grid-template-rows: auto auto 33vh;
    height: 100vh;
}}
.audio-player {{
    padding: 10px 20px;
    background-color: #f0f0f0;
    max-width: 100ch;
    margin: 0 auto;
}}
.story {{
    padding: 20px;
    overflow-y: auto;
    max-width: 100ch;
    margin: 0 auto;
}}
.chapter {{
    margin-bottom: 30px;
}}
.sentence {{
    display: inline;
    text-align: justify;
    cursor: pointer;
    padding: 5px;
    margin-bottom: 5px;
    line-height: 1.5;
    word-spacing: normal;
}}
.sentence:hover {{
    background-color: #e0e0e0;
}}
.sentence.selected {{
    background-color: #add8e6;
    border-left: 4px solid #4682b4;
    padding-left: 10px;
}}
.word {{
    display: inline;
}}
.analysis {{
    padding: 20px;
    background-color: #f0f0f0;
    border-top: 1px solid #ccc;
    overflow-y: auto;
    max-width: 100ch;
    margin: 0 auto;
}}
.analysis p {{
    margin-bottom: 10px;
}}
</style>
</head>
<body>
<div class="container">
    <div class="audio-player">
        {audio_html}
    </div>
    <div class="story">
        <h1>{title}</h1>
        {chapters_html}
    </div>
    <div class="analysis">
        <p><strong>Plot Function:</strong> <span id="plot-function"></span></p>
        <p><strong>Grimm Style:</strong> <span id="grimm-style"></span></p>
        <p><strong>Moral Implication:</strong> <span id="moral-implication"></span></p>
        <p><strong>Metaphorical/Psychological Meaning:</strong> <span id="metaphorical-meaning"></span></p>
        <p><strong>Chapter Number:</strong> <span id="chapter-number"></span></p>
        <p><strong>Sentence Number:</strong> <span id="sentence-number"></span></p>
    </div>
</div>
<script>
var analysisData = {analysis_data_json};
function selectSentence(index) {{
    document.querySelectorAll('.sentence').forEach(function(el) {{
        el.classList.remove('selected');
    }});
    document.querySelector(`.sentence[data-index="${{index}}"]`).classList.add('selected');
    var data = analysisData[index];
    document.getElementById('plot-function').textContent = data['Plot Function'] || '';
    document.getElementById('grimm-style').textContent = data['Grimm Style'] || '';
    document.getElementById('moral-implication').textContent = data['Moral Implication'] || '';
    document.getElementById('metaphorical-meaning').textContent = data['Metaphorical/Psychological Meaning'] || '';
    document.getElementById('chapter-number').textContent = data['Chapter Number'] || '';
    document.getElementById('sentence-number').textContent = data['Sentence Number'] || '';
}}
document.querySelectorAll('.sentence').forEach(function(el) {{
    el.addEventListener('click', function() {{
        selectSentence(this.dataset.index);
    }});
}});
if (analysisData.length > 0) {{
    selectSentence(0);
}}
</script>
</body>
</html>
'''

# HTML template for main page
main_html_template = '''
<html>
<head>
<title>Story Index</title>
<style>
body {{
    font-family: Arial, sans-serif;
    font-size: 16px;
    margin: 0;
    padding: 20px;
    background-color: #f9f9f9;
}}
h1 {{
    text-align: center;
    color: #333;
}}
ul {{
    list-style: none;
    padding: 0;
    max-width: 60ch;
    margin: 0 auto;
}}
li {{
    margin-bottom: 10px;
}}
a {{
    text-decoration: none;
    color: #4682b4;
    font-size: 18px;
}}
a:hover {{
    text-decoration: underline;
    color: #add8e6;
}}
</style>
</head>
<body>
<h1>Story Index</h1>
<ul>
{links_html}
</ul>
</body>
</html>
'''

# Get list of JSON files
files = glob.glob('code*.txt')

# Process JSON files to generate story pages
for file in files:
    with open(file, 'r') as f:
        data = json.load(f)
    
    title = data['The Complete Story']['Title']
    chapters = data['The Complete Story']['Chapters']
    analysis = data['Analysis']
    
    safe_title = sanitize_title(title)
    
    # Create stories directory if it doesn't exist
    stories_dir = os.path.join(os.getcwd(), 'stories')
    if not os.path.exists(stories_dir):
        os.makedirs(stories_dir)
    
    folder_path = os.path.join(stories_dir, safe_title)
    
    # Create story folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    txt_filename = os.path.join(folder_path, safe_title + '.txt')
    html_filename = os.path.join(folder_path, safe_title + '.html')
    mp3_filename = os.path.join(folder_path, safe_title + '.mp3')
    
    # Check for existing .mp3 files and rename if necessary
    mp3_files = glob.glob(os.path.join(folder_path, '*.mp3'))
    if mp3_files and not os.path.exists(mp3_filename):
        # Rename the first .mp3 file found to match safe_title
        shutil.move(mp3_files[0], mp3_filename)
    
    # Generate audio HTML
    audio_html = ''
    if os.path.exists(mp3_filename):
        audio_html = f'<audio controls src="{html.escape(safe_title + ".mp3")}"><p>Your browser does not support the audio element.</p></audio>'
    else:
        audio_html = '<p>No audio file available.</p>'
    
    # Generate text file
    with open(txt_filename, 'w') as f:
        f.write(title + '\n')
        for chapter in chapters:
            f.write(chapter + '\n')
    
    # Group sentences by chapter
    chapters_content = {}
    for i, item in enumerate(analysis):
        chapter_num = item.get('Chapter Number', 0)
        if chapter_num not in chapters_content:
            chapters_content[chapter_num] = []
        chapters_content[chapter_num].append((i, item['Sentence']))
    
    # Generate chapters HTML with words wrapped in spans
    chapters_html = ''
    for chapter_num in sorted(chapters_content.keys()):
        sentences_html = ''
        for i, sentence in chapters_content[chapter_num]:
            # Split sentence into words and wrap each in a span
            words = sentence.split()
            words_html = ''.join(f'<span class="word">{html.escape(word)}</span> ' for word in words)
            sentences_html += f'<span class="sentence" data-index="{i}">{words_html}</span>'
        chapters_html += f'<div class="chapter">{sentences_html}</div>\n'
    
    # Generate analysis data JSON
    analysis_data_json = json.dumps(analysis)
    
    # Write story HTML file
    with open(html_filename, 'w') as f:
        f.write(story_html_template.format(
            title=html.escape(title),
            audio_html=audio_html,
            chapters_html=chapters_html,
            analysis_data_json=analysis_data_json
        ))

# Generate main.html with links to all HTML files in subfolders
links_html = ''
html_files = []

# Scan all subdirectories for .html files
for root, dirs, files in os.walk(os.getcwd()):
    for file in files:
        if file.endswith('.html') and root != os.getcwd():  # Exclude HTML files in current directory
            relative_path = os.path.relpath(os.path.join(root, file), os.getcwd()).replace('\\', '/')
            # Derive display title from folder name
            folder_name = os.path.basename(root)
            display_title = folder_name.replace('_', ' ')
            html_files.append((display_title, relative_path))

# Sort links alphabetically by display title
html_files.sort(key=lambda x: x[0].lower())
links_html = ''.join(f'<li><a href="{html.escape(path)}">{html.escape(title)}</a></li>\n' for title, path in html_files)

# Write main.html
with open('main.html', 'w') as f:
    f.write(main_html_template.format(links_html=links_html))
