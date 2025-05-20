document.addEventListener('DOMContentLoaded', () => {
    // --- CONFIGURATION ---
    const authorsGuidePath = './../prompt/Authors guide short.txt';
    const formatsDir = './../formats';
    const seedsDir = './../seeds';
    const contentsFilename = 'contents.txt';

    // --- DOM ELEMENTS ---
    const formatSelect = document.getElementById('format-select');
    const seedSelect = document.getElementById('seed-select');
    const seedPreview = document.getElementById('seed-preview');
    const chaptersCountInput = document.getElementById('chapters-count');
    const sentencesPerChapterInput = document.getElementById('sentences-per-chapter');
    const generateBtn = document.getElementById('generate-prompt-btn');
    const combinedPromptTextarea = document.getElementById('combined-prompt');
    const receivedPromptTextElement = document.getElementById('received-prompt-text');

    // New button elements
    const downloadPromptBtn = document.getElementById('download-prompt-btn');
    const copyFullPromptBtn = document.getElementById('copy-full-prompt-btn');
    const copyNoFormatBtn = document.getElementById('copy-no-format-btn');
    const copyFormatOnlyBtn = document.getElementById('copy-format-only-btn');
    const copyPromptOnlyBtn = document.getElementById('copy-prompt-only-btn');

    let authorsGuideData = '';
    let promptTextObject = '';
    let currentPromptCore = ''; // Stores the main prompt without the format JSON
    let currentFormatJsonString = ''; // Stores the format JSON string
    let currentPromptOnlyPrompt = ''; // Stores the prompt part only

    // --- HELPER TO LOAD FILE LISTS ---
    async function loadFileList(directoryPath) {
        try {
            const response = await fetch(`${directoryPath}/${contentsFilename}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status} while fetching ${directoryPath}/${contentsFilename}`);
            }
            const text = await response.text();
            return text.split('\n')
                       .map(filename => filename.trim())
                       .filter(filename => filename.length > 0)
                       .map(filename => `${directoryPath}/${filename}`);
        } catch (error) {
            console.error(`Error loading file list from ${directoryPath}/${contentsFilename}:`, error);
            alert(`Could not load file list from ${directoryPath}. Check console for details.`);
            return [];
        }
    }

    // --- INITIALIZATION ---
    async function initialize() {
        const formatFiles = await loadFileList(formatsDir);
        const seedFiles = await loadFileList(seedsDir);

        populateSelect(formatSelect, formatFiles);
        populateSelect(seedSelect, seedFiles);

        try {
            const response = await fetch(authorsGuidePath);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            authorsGuideData = await response.text();
        } catch (error) {
            console.error('Error loading authors guide:', error);
            authorsGuideData = 'Error: Could not load Authors Guide.';
        }
        
        const urlParams = new URLSearchParams(window.location.search);
        promptTextObject = urlParams.get('prompt_text_object') || 'No specific elements requested for this story.';
        receivedPromptTextElement.textContent = promptTextObject;

        // Event Listeners
        seedSelect.addEventListener('change', displaySeedPreview);
        generateBtn.addEventListener('click', generateCombinedPrompt);

        // Add event listeners for new buttons
        downloadPromptBtn.addEventListener('click', downloadPrompt);
        copyFullPromptBtn.addEventListener('click', () => copyToClipboard(combinedPromptTextarea.value, copyFullPromptBtn));
        copyNoFormatBtn.addEventListener('click', () => copyToClipboard(currentPromptCore, copyNoFormatBtn));
        copyFormatOnlyBtn.addEventListener('click', () => copyToClipboard(currentFormatJsonString, copyFormatOnlyBtn));
        copyPromptOnlyBtn.addEventListener('click', () => copyToClipboard(currentPromptOnlyPrompt, copyPromptOnlyBtn));
    }

    function populateSelect(selectElement, files) {
        // Clear existing options except the first placeholder
        while (selectElement.options.length > 1) {
            selectElement.remove(1);
        }
        
        if (files.length === 0) {
            selectElement.options[0].textContent = `-- No files found --`;
            selectElement.disabled = true;
            return;
        }
        selectElement.options[0].textContent = `-- Select ${selectElement.id.includes('format') ? 'Format' : 'Seed'} --`;
        selectElement.disabled = false;

        files.forEach(file => {
            const option = document.createElement('option');
            option.value = file;
            option.textContent = file.split('/').pop();
            selectElement.appendChild(option);
        });
    }

    async function displaySeedPreview() {
        const selectedSeedFile = seedSelect.value;
        if (!selectedSeedFile) {
            seedPreview.textContent = 'Select a seed file to see its preview.';
            return;
        }
        try {
            const response = await fetch(selectedSeedFile);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const textData = await response.text();
            const jsonData = JSON.parse(textData); 
            let previewContent = `File: ${selectedSeedFile.split('/').pop()}\n\n`;
            previewContent += `Title: ${jsonData['The Complete Story']?.Title || 'N/A'}\n\n`;
            previewContent += `Chapters (start): \n${(jsonData['The Complete Story']?.Chapters || '').substring(0, 200)}...\n\n`;
            previewContent += `Analysis (keys): ${Object.keys(jsonData.Analysis || {}).join(', ')}`;
            seedPreview.textContent = previewContent;
        } catch (error) {
            console.error('Error loading or parsing seed file:', error);
            seedPreview.textContent = `Error loading preview for ${selectedSeedFile.split('/').pop()}: ${error.message}`;
        }
    }

    async function generateCombinedPrompt() {
        const selectedFormatFile = formatSelect.value;
        const selectedSeedFile = seedSelect.value;
        const chaptersCount = parseInt(chaptersCountInput.value, 10);
        const sentencesPerChapter = parseInt(sentencesPerChapterInput.value, 10);

        if (!selectedFormatFile || !selectedSeedFile) {
            alert('Please select both a format file and a seed file.');
            return;
        }
        if (formatSelect.disabled || seedSelect.disabled) {
            alert('File lists could not be loaded. Cannot generate prompt.');
            return;
        }

        try {
            const formatResponse = await fetch(selectedFormatFile);
            if (!formatResponse.ok) throw new Error(`Format fetch error: ${formatResponse.status} for ${selectedFormatFile}`);
            const formatData = await formatResponse.json();

            const seedResponse = await fetch(selectedSeedFile);
            if (!seedResponse.ok) throw new Error(`Seed fetch error: ${seedResponse.status} for ${selectedSeedFile}`);
            const seedText = await seedResponse.text();
            const seedData = JSON.parse(seedText);

            const storyTitle = seedData['The Complete Story']?.Title || 'Untitled Story';
            const storyChapters = seedData['The Complete Story']?.Chapters || 'No chapter content available.';
            const analysisJsonString = seedData.Analysis ? JSON.stringify(seedData.Analysis, null, 2) : '{}';
            
            currentFormatJsonString = JSON.stringify(formatData, null, 2); // Store format JSON
            
            const totalSentences = sentencesPerChapter * chaptersCount;

            // Store the main part of the prompt
            currentPromptCore = `Read this authors guide:
BEGIN AUTHORS GUIDE
´´´
${authorsGuideData}
´´´
END AUTHORS GUIDE

The following story will be analyzed according to the authors guide:
BEGIN STORY
´´´
${storyTitle}
${storyChapters}
´´´
END STORY


Here is the analysis of each sentence of the story one by one structured in chapters where there is a chapter for each sentence in order. Each sentence is regarded in relation to the whole story, morals, and metaphorical or psychological meanings (if there are any).
BEGIN ANALYSIS
´´´
${analysisJsonString}
´´´
END ANALYSIS
Now for your task:
BEGIN PROMPT
Write a new essay and as you go along you need to come up with a new original story. Let each chapter consist of ${sentencesPerChapter} sentences.  Write ${chaptersCount} chapters, so there will be ${totalSentences} sentence sections in total.  DO NOT COME UP WITH THE PLOT OR TITLE OR SETTING OR ANYTHING AT ALL BEFORE STARTING WRITING.  You as the author need to come up with the plot "as you go" writing this. For each section (sentence) start by writing the analysis/explanation/commenatary of the sentence and then write the sentence last after these, (plot function, grimm style, moral implication, metaphorical/psychological meaning, sentence). This way you will "plan out" the sentence before writing it.   

You must also adhere to the following guidelines:  
- Do not come up with names for characters, just call them "the king's son" or "The miller". 
- Do not come up with names for places (like Whispering Woods or anything like that). Just say "A dark forest". 
- Do not describe the inner state of characters (example to avoid: "her heart full of both fear and a strange resolve. ").  

I also have some requirements for elements to be present in this particular story: 
${promptTextObject}

Make sure that you cover different details when analyzing each sentence. So if "plot function" touches on the next step of the story, leave that unsaid in the rest of the sections you write for that sentence.  Do not write an intruduction. Finally, write out the whole story exactly as stated all the way until sentence ${totalSentences}.
END PROMPT`;

            combinedPromptTextarea.value = `${currentPromptCore}\n${currentFormatJsonString}`;
            // get the part of the currentPromptCore that starts with BEGIN PROMPT and ends with END PROMPT
            const promptStartIndex = currentPromptCore.indexOf('BEGIN PROMPT') + 'BEGIN PROMPT'.length;
            const promptEndIndex = currentPromptCore.indexOf('END PROMPT');
            currentPromptOnlyPrompt = currentPromptCore.substring(promptStartIndex, promptEndIndex).trim();
            combinedPromptTextarea.value = combinedPromptTextarea.value.replace(/´´´/g, '```'); // Replace with triple backticks
            // Enable action buttons now that a prompt is generated
            enableActionButtons(true);

        } catch (error) {
            console.error('Error generating combined prompt:', error);
            combinedPromptTextarea.value = `Error: ${error.message}`;
            currentPromptCore = '';
            currentPromptOnlyPrompt = '';
            currentFormatJsonString = '';
            alert(`Failed to generate prompt: ${error.message}`);
            enableActionButtons(false); // Disable if generation failed
        }
    }

    function enableActionButtons(enable) {
        downloadPromptBtn.disabled = !enable;
        copyFullPromptBtn.disabled = !enable;
        copyNoFormatBtn.disabled = !enable || !currentPromptCore;
        copyFormatOnlyBtn.disabled = !enable || !currentFormatJsonString;
        copyPromptOnlyBtn.disabled = !enable || !currentPromptOnlyPrompt;
    }

    function downloadPrompt() {
        if (!combinedPromptTextarea.value) {
            alert("No prompt generated to download.");
            return;
        }
        const filename = "combined_prompt.txt";
        const text = combinedPromptTextarea.value;
        const element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
        element.setAttribute('download', filename);
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }

    async function copyToClipboard(textToCopy, buttonElement) {
        if (!textToCopy) {
            // alert("Nothing to copy."); // Or silently do nothing
            if (buttonElement) {
                const originalText = buttonElement.textContent;
                buttonElement.textContent = 'Nothing to Copy!';
                setTimeout(() => {
                    buttonElement.textContent = originalText;
                }, 2000);
            }
            return;
        }
        try {
            await navigator.clipboard.writeText(textToCopy);
            if (buttonElement) {
                const originalText = buttonElement.textContent;
                buttonElement.textContent = 'Copied!';
                setTimeout(() => {
                    buttonElement.textContent = originalText;
                }, 1500);
            } else {
                alert('Copied to clipboard!');
            }
        } catch (err) {
            console.error('Failed to copy: ', err);
            if (buttonElement) {
                const originalText = buttonElement.textContent;
                buttonElement.textContent = 'Copy Failed!';
                setTimeout(() => {
                    buttonElement.textContent = originalText;
                }, 2000);
            } else {
                alert('Failed to copy text.');
            }
        }
    }

    // --- RUN INITIALIZATION ---
    initialize();
});