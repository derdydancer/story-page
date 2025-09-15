// story_tool.js

// Function to save a story to localStorage
function saveStoryToLocalStorage(storyData) {
    // Get existing stories from localStorage
    let stories = JSON.parse(localStorage.getItem('localStories') || '[]');
    
    // Add the new story with a timestamp
    storyData.timestamp = new Date().toISOString();
    stories.push(storyData);
    
    // Save back to localStorage
    localStorage.setItem('localStories', JSON.stringify(stories));
    
    // Update the display
    displayLocalStories();
}

// Function to get stories from localStorage
function getLocalStories() {
    return JSON.parse(localStorage.getItem('localStories') || '[]');
}

// Function to remove a story from localStorage
function removeLocalStory(index) {
    let stories = getLocalStories();
    stories.splice(index, 1);
    localStorage.setItem('localStories', JSON.stringify(stories));
    displayLocalStories();
}

// Function to export all local stories as a ZIP file
// Function to generate an index.html file that lists local stories as if they were in the repo
function generateLocalIndexHTML(stories) {
    // Generate links for each story
    let localStoriesHtml = '';
    
    // Group stories by date (using timestamp)
    const storiesByDate = {};
    
    stories.forEach((story, index) => {
        const title = story['The Complete Story']?.Title || story.title || `Story_${index + 1}`;
        const sanitizedTitle = sanitizeTitle(title);
        
        // Use the story's timestamp or current date
        const timestamp = story.timestamp || new Date().toISOString();
        const date = timestamp.split('T')[0]; // Get YYYY-MM-DD format
        
        if (!storiesByDate[date]) {
            storiesByDate[date] = [];
        }
        
        // Add h2-tags with date and li-tags with href following the pattern:
        // href="stories/SAME_FOLDER_NAME_AS_IN_EXPORTED_ZIP/SAME_PAGE_NAME_AS_IN_EXPORTED_ZIP"
        storiesByDate[date].push(`<li><a href="stories/${sanitizedTitle}/${sanitizedTitle}.html">${escapeHtml(title)}</a></li>`);
    });
    
    // Sort dates descending and generate the HTML
    const sortedDates = Object.keys(storiesByDate).sort((a, b) => b.localeCompare(a));
    
    sortedDates.forEach(date => {
        localStoriesHtml += `<h2>${date}</h2>
`;
        localStoriesHtml += storiesByDate[date].join('\n') + '\n';
    });
    
    // Return just the local stories HTML (to be inserted in the main index.html)
    return localStoriesHtml;
}

function exportLocalStories() {
    const stories = getLocalStories();
    
    if (stories.length === 0) {
        alert('No stories to export.');
        return;
    }
    
    // Create a new JSZip instance
    const zip = new JSZip();
    
    // Add each story to the ZIP
    stories.forEach((story, index) => {
        try {
            const title = story['The Complete Story']?.Title || story.title || `Story_${index + 1}`;
            const sanitizedTitle = sanitizeTitle(title);
            
            // Create a folder for the story
            const folder = zip.folder(`stories/${sanitizedTitle}`);
            
            // Add the story data as a JSON file
            folder.file(`${sanitizedTitle}.code.json`, JSON.stringify(story, null, 2));
            
            // Add the story text as an HTML file (using the same template as the Python script)
            const htmlContent = generateStoryHTML(story);
            folder.file(`${sanitizedTitle}.html`, htmlContent);
            
            // Add the story text as a TXT file
            const txtContent = generateStoryTXT(story);
            folder.file(`${sanitizedTitle}.txt`, txtContent);
        } catch (e) {
            console.error('Error processing story:', e);
        }
    });
    
    // Generate an index.html file that combines local stories with repository stories
    // First, get the current index.html content
    fetch('index.html')
        .then(response => response.text())
        .then(mainIndexContent => {
            // Generate the local stories HTML
            const localStoriesHtml = generateLocalIndexHTML(stories);
            
            // Insert the local stories HTML into the main index.html
            // Find the position after "Repository Stories" heading and insert before the closing </ul>
            const repoStoriesStart = mainIndexContent.indexOf('<h1>Repository Stories</h1>');
            if (repoStoriesStart !== -1) {
                const ulStart = mainIndexContent.indexOf('<ul>', repoStoriesStart);
                if (ulStart !== -1) {
                    const ulEnd = mainIndexContent.indexOf('</ul>', ulStart);
                    if (ulEnd !== -1) {
                        // Insert the local stories after the <ul> tag
                        const beforeUl = mainIndexContent.substring(0, ulStart + 4); // +4 for <ul>
                        const afterUl = mainIndexContent.substring(ulStart + 4); // Rest of content after <ul>
                        const updatedIndexContent = beforeUl + '\n' + localStoriesHtml + afterUl;
                        
                        // Add the updated index.html to the ZIP
                        zip.file('index.html', updatedIndexContent);
                        
                        // Generate the ZIP file and trigger download
                        zip.generateAsync({type:"blob"}).then(function(content) {
                            // Use FileSaver.js to save the file
                            saveAs(content, "local_stories.zip");
                        }).catch(function(error) {
                            console.error('Error generating ZIP file:', error);
                            alert('Error generating ZIP file. Please check the console for details.');
                        });
                    } else {
                        throw new Error('Could not find closing </ul> tag');
                    }
                } else {
                    throw new Error('Could not find <ul> tag after Repository Stories');
                }
            } else {
                throw new Error('Could not find Repository Stories heading');
            }
        })
        .catch(function(error) {
            console.error('Error generating index.html:', error);
            alert('Error generating index.html. Please check the console for details.');
        });
}

// Function to sanitize title for filename and folder name (same as Python)
function sanitizeTitle(title) {
    return title.replace(/[^a-z0-9_ ]/gi, '').trim().replace(/ /g, '_');
}

// Function to escape HTML (similar to Python's html.escape)
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Function to generate HTML content for a story (same logic as Python script)
function generateStoryHTML(story) {
    const title = story['The Complete Story']?.Title || story.title || 'Untitled Story';
    const analysis = story.Analysis || [];
    const chapters = story['The Complete Story']?.Chapters || [];
    
    // Group sentences by chapter
    const chaptersContent = {};
    analysis.forEach((item, i) => {
        const chapterNum = item['Chapter Number'] || 0;
        if (!chaptersContent[chapterNum]) {
            chaptersContent[chapterNum] = [];
        }
        chaptersContent[chapterNum].push({index: i, sentence: item.Sentence});
    });
    
    // Generate chapters HTML with words wrapped in spans
    let chaptersHtml = '';
    Object.keys(chaptersContent).sort((a, b) => parseInt(a) - parseInt(b)).forEach(chapterNum => {
        let sentencesHtml = '';
        // Sort sentences within a chapter by Sentence Number
        const sortedSentences = chaptersContent[chapterNum].sort((a, b) => {
            const itemA = analysis[a.index];
            const itemB = analysis[b.index];
            return (itemA['Sentence Number'] || 0) - (itemB['Sentence Number'] || 0);
        });
        
        sortedSentences.forEach(({index, sentence}) => {
            // Split sentence into words and wrap each in a span
            const words = sentence.split(' ');
            const wordsHtml = words.map(word => `<span class="word">${escapeHtml(word)}</span>`).join(' ');
            sentencesHtml += `<span class="sentence" data-index="${index}">${wordsHtml} </span>`;
        });
        chaptersHtml += `<div class="chapter">${sentencesHtml}</div>
`;
    });
    
    // Dynamically determine all unique analysis keys
    const allAnalysisKeys = new Set();
    analysis.forEach(item => {
        Object.keys(item).forEach(key => {
            if (key !== 'Sentence') { // Remove 'Sentence' key
                allAnalysisKeys.add(key);
            }
        });
    });
    
    const displayKeys = Array.from(allAnalysisKeys);
    
    // Generate analysis fields HTML
    let analysisFieldsHtml = '';
    displayKeys.forEach(key => {
        const safeId = key.toLowerCase().replace(/ /g, '-').replace(/\//g, '-').replace(/:/g, '').replace(/\./g, '');
        analysisFieldsHtml += `<p><strong>${escapeHtml(key)}:</strong> <span id="${safeId}"></span></p>
`;
    });
    
    // Generate JS code to update all fields
    let jsUpdateFields = '';
    displayKeys.forEach(key => {
        const safeId = key.toLowerCase().replace(/ /g, '-').replace(/\//g, '-').replace(/:/g, '').replace(/\./g, '');
        jsUpdateFields += `    document.getElementById('${safeId}').textContent = data['${key}'] || '';
`;
    });
    
    // Generate analysis data JSON
    const analysisDataJson = JSON.stringify(analysis);
    
    // Add the copy-json-container div
    chaptersHtml += '<div id="copy-json-container" style="text-align:center;margin:20px 0;"></div>';
    
    // HTML template (similar to Python script)
    return `<!DOCTYPE html>
<html>
<head>
    <title>${escapeHtml(title)}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            font-size: 16px;
            margin: 0;
        }
        .container {
            display: grid;
            grid-template-rows: auto auto 33vh;
            height: 100vh;
        }
        .audio-player {
            padding: 10px 20px;
            background-color: #f0f0f0;
            max-width: 100ch;
            margin: 0 auto;
            zoom: 2;
        }
        .story {
            padding: 20px;
            overflow-y: auto;
            max-width: 100ch;
            margin: 0 auto;
        }
        .chapter {
            margin-bottom: 30px;
        }
        .sentence {
            display: inline;
            text-align: justify;
            cursor: pointer;
            padding: 5px;
            margin-bottom: 5px;
            line-height: 1.5;
            word-spacing: normal;
        }
        .sentence:hover {
            background-color: #e0e0e0;
        }
        .sentence.selected {
            background-color: #add8e6;
            border-left: 4px solid #4682b4;
            border-right: 4px solid #4682b4;
            padding-right: 1px;
            padding-left: 1px;
        }
        .word {
            display: inline;
        }
        .analysis {
            padding: 20px;
            background-color: #f0f0f0;
            border-top: 1px solid #ccc;
            overflow-y: auto;
            max-width: 100ch;
            margin: 0 auto;
        }
        .analysis p {
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="audio-player">
            <p>No audio file available.</p>
        </div>
        <div class="story">
            <h1>${escapeHtml(title)}</h1>
            ${chaptersHtml}
        </div>
        <div class="analysis">
            ${analysisFieldsHtml}
        </div>
    </div>
    <script>
        var analysisData = ${analysisDataJson};
        function selectSentence(index) {
            document.querySelectorAll('.sentence').forEach(function(el) {
                el.classList.remove('selected');
            });
            document.querySelector('.sentence[data-index="' + index + '"]').classList.add('selected');
            var data = analysisData[index];
            ${jsUpdateFields}
        }
        document.querySelectorAll('.sentence').forEach(function(el) {
            el.addEventListener('click', function() {
                selectSentence(this.dataset.index);
            });
        });
        if (analysisData.length > 0) {
            selectSentence(0);
        }
    </script>
</body>
</html>`;
}

// Function to generate TXT content for a story
function generateStoryTXT(story) {
    const title = story['The Complete Story']?.Title || story.title || 'Untitled Story';
    const chapters = story['The Complete Story']?.Chapters || [];
    
    let content = title + '\n';
    chapters.forEach(chapter => {
        content += chapter + '\n';
    });
    return content;
}

// Function to display local stories in the index page
function displayLocalStories() {
    const localStories = getLocalStories();
    const localStoriesList = document.getElementById('local-stories-list');
    
    if (!localStoriesList) return;
    
    // Clear the current list
    localStoriesList.innerHTML = '';
    
    if (localStories.length === 0) {
        localStoriesList.innerHTML = '<li>No local stories created yet.</li>';
        return;
    }
    
    // Add each story to the list
    localStories.forEach((story, index) => {
        const title = story['The Complete Story']?.Title || story.title || `Story ${index + 1}`;
        const li = document.createElement('li');
        li.innerHTML = `
            <a href="#" onclick="viewLocalStory(${index})">${escapeHtml(title)}</a>
            <button onclick="removeLocalStory(${index})" style="margin-left: 10px;">Remove</button>
        `;
        localStoriesList.appendChild(li);
    });
}

// Function to view a local story
function viewLocalStory(index) {
    const stories = getLocalStories();
    if (index >= 0 && index < stories.length) {
        const story = stories[index];
        const htmlContent = generateStoryHTML(story);
        
        // Replace the current page content with the story content
        document.open();
        document.write(htmlContent);
        document.close();
    }
}

// Function to initialize the story creation form
function initStoryCreationForm() {
    const form = document.getElementById('story-creation-form');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form values
        const title = document.getElementById('story-title').value;
        const jsonData = document.getElementById('story-json').value;
        
        if (!title) {
            alert('Please enter a title for the story.');
            return;
        }
        
        if (!jsonData) {
            alert('Please paste the story JSON data.');
            return;
        }
        
        try {
            // Parse the JSON data
            const storyData = JSON.parse(jsonData);
            
            // Add the title if not present
            if (!storyData.title) {
                storyData.title = title;
            }
            
            // Save to localStorage
            saveStoryToLocalStorage(storyData);
            
            // Reset the form
            form.reset();
            
            // Show success message
            alert('Story saved successfully!');
        } catch (e) {
            alert('Error parsing JSON data. Please check the format and try again. \nError: ' + e.message);
        }
    });
}

// Initialize when the page loads
document.addEventListener('DOMContentLoaded', function() {
    initStoryCreationForm();
    displayLocalStories();
});