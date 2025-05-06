# Story Page

A dynamic web-based story presentation system that transforms JSON story files into interactive HTML pages with sentence-by-sentence analysis and audio narration support.

## Features

- **Interactive Story Reading**: Each story is presented with clickable sentences that reveal detailed analysis
- **Multi-format Support**: Stories are available in multiple formats:
  - HTML pages with interactive features
  - Plain text files for easy reading
  - MP3 audio narrations (where available)
- **Story Analysis**: Each sentence includes detailed analysis of:
  - Plot Function
  - Grimm Style Elements
  - Moral Implications
  - Metaphorical/Psychological Meaning
  - Chapter and Sentence Numbers
- **Responsive Design**: Clean, readable layout with maximum width optimization for comfortable reading
- **Audio Integration**: Built-in audio player for stories with narration
- **Central Index**: Main page with easy navigation to all available stories

## Project Structure

```
story-page/
├── main.html                 # Index page with links to all stories
├── process_json_files_updated.py  # Processing script
├── code*.txt                 # Source JSON files
└── Story_Name/              # Individual story folders
    ├── Story_Name.html      # Interactive HTML version
    ├── Story_Name.txt       # Plain text version
    └── Story_Name.mp3       # Audio narration (if available)
```

## Technical Details

The system processes JSON files containing story content and analysis data. Each story is processed to create:

1. An HTML file with:
   - Interactive sentence selection
   - Analysis panel
   - Integrated audio player (when available)
   - Responsive styling
2. A plain text version for easy reading
3. Support for audio narration files

The HTML interface is divided into three main sections:
- Audio player section at the top
- Story content in the middle
- Analysis panel at the bottom

## Usage

1. Place story JSON files in the root directory (named as `code*.txt`)
2. Place any audio narration files in the respective story folders
3. Run the processing script:
   ```
   python process_json_files_updated.py
   ```
4. Open `main.html` in a web browser to access the story index

## Features of the HTML Interface

- **Sentence Interaction**: Click any sentence to view its detailed analysis
- **Audio Controls**: Integrated audio player for stories with narration
- **Responsive Layout**: Content is centered and width-limited for optimal reading
- **Visual Feedback**: Hover and selection effects for interactive elements
- **Clean Typography**: Optimized font settings and spacing for readability

## Story Analysis Components

Each sentence can be analyzed for:
- Plot Function: The role of the sentence in advancing the story
- Grimm Style: Elements reminiscent of Grimm's fairy tales
- Moral Implication: The ethical or moral aspects presented
- Metaphorical/Psychological Meaning: Deeper symbolic interpretations
- Structure Information: Chapter and sentence numbering
