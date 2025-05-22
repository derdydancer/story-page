import os
import re

# The code to insert at the end of the <script> section
SCRIPT_SNIPPET = '''// Add Copy JSON to Clipboard button if .code.json file exists in the same directory
(function() {
    // Get the current HTML file name (without extension)
    var htmlFile = location.pathname.split('/').pop();
    var baseName = htmlFile.replace(/\.html$/, '');
    baseName = baseName.replace(/_/g, ' ');
    var jsonFile = baseName + '.code.json';
    // Try to fetch the .code.json file
    fetch(jsonFile)
        .then(function(response) {
            if (!response.ok) throw new Error('No code.json');
            return response.text();
        })
        .then(function(jsonText) {
            // Create the button
            var btn = document.createElement('button');
            btn.textContent = 'Copy JSON to Clipboard';
            btn.style.margin = '10px auto';
            btn.style.display = 'inline-block';
            btn.onclick = function() {
                navigator.clipboard.writeText(jsonText).then(function() {
                    btn.textContent = 'Copied!';
                    setTimeout(function() { btn.textContent = 'Copy JSON to Clipboard'; }, 1500);
                }, function() {
                    btn.textContent = 'Copy Failed!';
                    setTimeout(function() { btn.textContent = 'Copy JSON to Clipboard'; }, 1500);
                });
            };
            document.getElementById('copy-json-container').appendChild(btn);
        })
        .catch(function() {
            // No .code.json file found, do nothing
        });
})();'''

# The div to insert at the end of <div class="story">
DIV_SNIPPET = '<div id="copy-json-container" style="text-align:center;margin:20px 0;"></div>'

def process_html_file(filepath):
    # Try utf-8, then windows-1252 if decode fails
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='windows-1252') as f:
            content = f.read()
    changed = False

    # Insert the div at the end of <div class="story">
    story_div_open = re.search(r'<div class="story"[^>]*>', content)
    if story_div_open:
        # Find the closing </div> for the story
        start = story_div_open.end()
        stack = 1
        i = start
        while stack > 0 and i < len(content):
            next_open = content.find('<div', i)
            next_close = content.find('</div>', i)
            if next_close == -1:
                break
            if next_open != -1 and next_open < next_close:
                stack += 1
                i = next_open + 4
            else:
                stack -= 1
                i = next_close + 6
        if stack == 0:
            # Insert before this closing </div>
            content = content[:i-6] + DIV_SNIPPET + content[i-6:]
            changed = True

    # Insert the script at the end of <script> section, before </script>
    script_end = content.rfind('</script>')
    if script_end != -1 and SCRIPT_SNIPPET not in content:
        # Add a second button for copy+open
        extra_btn = '''\n(function() {\n    // Get the current HTML file name (without extension)\n    var htmlFile = location.pathname.split('/').pop();\n    var baseName = htmlFile.replace(/\\.html$/, '');\n    baseName = baseName.replace(/_/g, ' ');\n    var jsonFile = baseName + '.code.json';\n    fetch(jsonFile)\n        .then(function(response) {\n            if (!response.ok) throw new Error('No code.json');\n            return response.text();\n        })\n        .then(function(jsonText) {\n            var btn2 = document.createElement('button');\n            btn2.textContent = 'Copy & Annotate';\n            btn2.style.margin = '10px auto 10px 10px';\n            btn2.style.display = 'inline-block';\n            btn2.onclick = function() {\n                navigator.clipboard.writeText(jsonText).then(function() {\n                    btn2.textContent = 'Copied!';\n                    setTimeout(function() { btn2.textContent = 'Copy & Annotate'; }, 1500);\n                    window.open('https://derdydancer.github.io/story-annotator-pro/', '_blank');\n                }, function() {\n                    btn2.textContent = 'Copy Failed!';\n                    setTimeout(function() { btn2.textContent = 'Copy & Annotate'; }, 1500);\n                });\n            };\n            document.getElementById('copy-json-container').appendChild(btn2);\n        })\n        .catch(function() { });\n})();'''
        content = content[:script_end] + SCRIPT_SNIPPET + extra_btn + '\n' + content[script_end:]
        changed = True

    if changed:
        # Write back using the same encoding as read
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        except UnicodeEncodeError:
            with open(filepath, 'w', encoding='windows-1252') as f:
                f.write(content)
    return changed

def main():
    base_dir = os.path.join(os.path.dirname(__file__), 'stories')
    report = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                try:
                    changed = process_html_file(path)
                    if changed:
                        report.append(f"[MODIFIED] {path}")
                    else:
                        report.append(f"[UNCHANGED] {path}")
                except Exception as e:
                    report.append(f"[ERROR] {path}: {e}")
    print("\n".join(report))

if __name__ == '__main__':
    main()
