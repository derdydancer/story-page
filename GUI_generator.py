import glob
import os
import subprocess
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import threading
import chardet
import mutagen

class GUIApp:
    def __init__(self, root):
        WIDTH = 160

        self.root = root
        self.root.title("GUI Generator")
        


        # File paths
        self.prompt_file = ".\\prompt\\prompt_text.txt"
        self.seeds_dir = ".\\seeds\\"


        # Dropdown for processed code files
        self.processed_files_dropdown = ttk.Combobox(root, state="readonly", width=100)
        self.refresh_processed_files()

        # Bind selection event to load file content
        self.processed_files_dropdown.bind("<<ComboboxSelected>>", self.load_processed_file_content)

        # Text editor
        self.text_editor = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=WIDTH, height=25)
        self.load_prompt_file()
        
        # Save button
        save_button = tk.Button(root, text="Save prompt file", command=self.save_prompt_file)
        
        # Dropdown for "seed" files
        self.seed_files_dropdown = ttk.Combobox(root, state="readonly", width=50)
        self.refresh_seed_files()
        
        # Run generate_story.py button
        run_generate_story_button = tk.Button(root, text="Run generate_story.py", command=self.run_generate_story)
        
        # Run process_json_files_updated.py button
        run_process_json_button = tk.Button(root, text="Run process_json_files_updated.py", command=self.run_process_json)
        
        # Dropdown for non-"seed" files
        self.non_seed_files_dropdown = ttk.Combobox(root, state="readonly", width=50)
        self.refresh_non_seed_files()

        # Refresh button for non-seed files
        refresh_non_seed_button = tk.Button(root, text="Refresh Unseeded stories", command=self.refresh_non_seed_files)
        
        # Run generate_seed.py button
        run_generate_seed_button = tk.Button(root, text="Run generate_seed.py", command=self.run_generate_seed)
        
        # Refresh button for processed files
        refresh_button = tk.Button(root, text="Refresh Processed Files", command=self.refresh_processed_files)

        # Refresh button for seed files
        refresh_seed_button = tk.Button(root, text="Refresh Seed Files", command=self.refresh_seed_files)

        # Dropdown for stories folders
        self.stories_folders_dropdown = ttk.Combobox(root, state="readonly", width=50)
        self.refresh_stories_folders()
        self.stories_folders_dropdown.bind("<<ComboboxSelected>>", self.load_stories_folder_content)
        # Event binding when folder is selected to enable the generate audio button if there is a .txt file in the folder and no mp3 file
        self.stories_folders_dropdown.bind("<<ComboboxSelected>>", lambda event: run_generate_audio_button.config(state="normal") if any(f.endswith(".txt") for f in os.listdir(os.path.join(".\\stories\\", self.stories_folders_dropdown.get()))) and not any(f.endswith(".mp3") for f in os.listdir(os.path.join(".\\stories\\", self.stories_folders_dropdown.get()))) else run_generate_audio_button.config(state="disabled"))

        # Button to open selected story html in browser
        open_story_button = tk.Button(root, text="Open Story HTML", command=self.open_story_html)

        # Refresh button for stories folders
        refresh_stories_button = tk.Button(root, text="Refresh Stories Folders", command=self.refresh_stories_folders)

        # Button to run generate_audio.py for selected story
        run_generate_audio_button = tk.Button(root, text="Run generate_audio.py", command=self.run_generate_audio)
        #disabled by default
        run_generate_audio_button.config(state="disabled")



        # Output display
        self.output_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=WIDTH, height=20, state="disabled")

        # Section to load prompt
        i_row = 0
        tk.Label(root, text="Chose a prompt to load below:").grid(row=i_row, column=0, sticky=tk.W, padx=10)
        self.processed_files_dropdown.grid(row=i_row, column=1, padx=10)
        refresh_button.grid(row=i_row, column=2, padx=10, pady=5)
        i_row += 1
        self.text_editor.grid(row=i_row, column=0, columnspan=6, padx=10, pady=10)
        i_row += 1
        save_button.grid(row=i_row, column=0, padx=10, pady=5)
        
        # section for seed files
        i_row += 1
        tk.Label(root, text="################################################################### SEED SELECTION   ###################################################################").grid(row=i_row, column=0, columnspan=6, sticky=tk.W, padx=10)
        i_row += 1
        tk.Label(root, text="Seed Files:").grid(row=i_row, column=0, sticky=tk.W, padx=10)
        i_row += 1
        self.seed_files_dropdown.grid(row=i_row, column=0, padx=10)
        refresh_seed_button.grid(row=i_row, column=2, padx=10, pady=5)

        # Section to generate story
        i_row += 1
        tk.Label(root, text="################################################################### STORY GENERATION ###################################################################").grid(row=i_row, column=0, columnspan=6, sticky=tk.W, padx=10)
        i_row += 1
        tk.Label(root, text="Generate story from saved prompt file using the selected seed file:").grid(row=i_row, column=0, sticky=tk.W, padx=10)
        i_row += 1
        run_generate_story_button.grid(row=i_row, column=0, padx=10, pady=5)

        # section for processed files
        i_row += 1
        tk.Label(root, text="################################################################### FOLDER SELECTION ###################################################################").grid(row=i_row, column=0, columnspan=6, sticky=tk.W, padx=10)
        i_row += 1
        tk.Label(root, text="Stories Folders:").grid(row=i_row, column=0, sticky=tk.W, padx=10)
        i_row += 1
        self.stories_folders_dropdown.grid(row=i_row, column=0, padx=10)
        run_generate_audio_button.grid(row=i_row, column=1, padx=10, pady=5)
        refresh_stories_button.grid(row=i_row, column=2, padx=10, pady=5)
        i_row += 1
        open_story_button.grid(row=i_row, column=0, padx=10, pady=5)

        # section for non-seed files
        i_row += 1
        tk.Label(root, text="################################################################### SEED GENERATION  ###################################################################").grid(row=i_row, column=0, columnspan=6, sticky=tk.W, padx=10)
        i_row += 1
        tk.Label(root, text="Unseeded stories:").grid(row=i_row, column=0, sticky=tk.W, padx=10)
        i_row += 1
        self.non_seed_files_dropdown.grid(row=i_row, column=0, padx=10)
        run_generate_seed_button.grid(row=i_row, column=1, padx=10, pady=5)
        refresh_non_seed_button.grid(row=i_row, column=2, padx=10, pady=5)

        # SECTION FOR BUILDING THE WEB PAGE
        i_row += 1
        tk.Label(root, text="################################################################### BUILD WEB PAGE    ###################################################################").grid(row=i_row, column=0, columnspan=6, sticky=tk.W, padx=10)
        i_row += 1
        tk.Label(root, text="Generate the web page:").grid(row=i_row, column=0, sticky=tk.W, padx=10)
        i_row += 1
        run_process_json_button.grid(row=i_row, column=0, pady=5)

        i_row += 1
        tk.Label(root, text="################################################################### OUTPUT            ###################################################################").grid(row=i_row, column=0, columnspan=6, sticky=tk.W, padx=10)
        i_row += 1
        tk.Label(root, text="Output:").grid(row=i_row, column=0, sticky=tk.W, padx=10)
        i_row += 1
        self.output_display.grid(row=i_row, column=0, columnspan=6, padx=10, pady=10)

    def run_generate_audio(self):
        selected_folder = self.stories_folders_dropdown.get()
        if not selected_folder:
            messagebox.showerror("Error", "No stories folder selected!")
            return
        stories_dir = os.path.join(".\\stories\\", selected_folder)
        try:
            files = [f for f in os.listdir(stories_dir) if f.endswith(".txt")]
            # ignore files named "creation_time.txt"
            files = [f for f in files if f != "creation_time.txt"]
            if files:
                file_path = os.path.join(stories_dir, files[0])
                command = f"python .\\generate_audio.py \"{file_path}\""
                self.output_display.config(state="normal")
                self.output_display.delete(1.0, tk.END)
                self.output_display.insert(tk.END, "Running generate_audio...\n")
                self.output_display.config(state="disabled")
                self.start_time = time.time()

                def run_async():
                    try:
                        # Calculate approximate progress based on word count
                        with open(file_path, "r") as f:
                            word_count = len(f.read().split())
                        total_audio_length = word_count / 3  # Total audio length in seconds
                        estimated_run_time = total_audio_length / 5  # Estimated run time in seconds (1s generates 5s of audio)
                        # print extimated length
                        self.output_display.config(state="normal")
                        self.output_display.insert(tk.END, f"Estimated audio length: {total_audio_length:.2f} seconds\n")
                        self.output_display.insert(tk.END, f"Word count: {word_count}\n")
                        self.output_display.insert(tk.END, f"Estimated run time: {estimated_run_time:.2f} seconds\n")
                        self.output_display.config(state="disabled")

                        process = subprocess.Popen(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        while True:                          
                            total_audio_length = word_count / 3  # Total audio length in seconds
                            elapsed = int(time.time() - self.start_time)
                            generated_audio_length = elapsed * 5  # Generated audio length in seconds (1s generates 5s of audio)
                            progress_percentage = (generated_audio_length / total_audio_length) * 100
                            self.output_display.config(state="normal")
                            self.output_display.insert(tk.END, f"Progress: {progress_percentage:.2f}% ({elapsed} seconds elapsed)\n")
                            self.output_display.config(state="disabled")
                            self.output_display.see(tk.END)

                            if process.poll() is not None:
                                break

                            # Check progress every 1 seconds
                            time.sleep(1)

                        stderr = process.stderr.read()
                        if stderr:
                            self.output_display.config(state="normal")
                            self.output_display.insert(tk.END, stderr)
                            self.output_display.config(state="disabled")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to run command: {e}")
                    finally:
                        # Get the length of the generated mp3 file in seconds
                        mp3_file = os.path.join(stories_dir, os.path.basename(file_path).replace(".txt", ".mp3"))
                        if os.path.exists(mp3_file):
                            from mutagen.mp3 import MP3
                            audio = MP3(mp3_file)
                            mp3_length = audio.info.length
                        else:
                            mp3_length = "N/A"
                        self.output_display.config(state="normal")
                        self.output_display.insert(tk.END, f"\nActual audio length: {mp3_length}\n")
                        self.output_display.insert(tk.END, "\nFinished generate_audio.\n")
                        self.output_display.config(state="disabled")
                        self.output_display.see(tk.END)

                        # Update the HTML file with the audio link
                        html_filename = os.path.join(stories_dir, os.path.basename(file_path).replace(".txt", ".html"))
                        print(html_filename)
                        with open(html_filename, 'rb') as f:
                            raw_data = f.read()
                            result = chardet.detect(raw_data)
                            encoding = result['encoding']
                        
                        with open(html_filename, 'r', encoding=encoding) as f:
                            html_content = f.read()
                        audio_html = f'<audio controls src="{os.path.basename(mp3_file)}"><p>Your browser does not support the audio element.</p></audio>'
                        html_content = html_content.replace('<p>No audio file available.</p>', audio_html)
                        with open(html_filename, 'w', encoding=encoding) as f:
                            f.write(html_content)


                threading.Thread(target=run_async).start()
            else:
                messagebox.showinfo("Info", "No text files found in the selected folder.")
        except FileNotFoundError:
            messagebox.showerror("Error", f"Directory not found: {stories_dir}")

    def open_story_html(self):
        selected_folder = self.stories_folders_dropdown.get()
        if not selected_folder:
            messagebox.showerror("Error", "No stories folder selected!")
            return
        stories_dir = os.path.join(".\\stories\\", selected_folder)
        try:
            files = [f for f in os.listdir(stories_dir) if f.endswith(".html")]
            if files:
                file_path = os.path.join(stories_dir, files[0])
                os.startfile(file_path)
            else:
                messagebox.showinfo("Info", "No HTML files found in the selected folder.")
        except FileNotFoundError:
            messagebox.showerror("Error", f"Directory not found: {stories_dir}")

    def refresh_stories_folders(self):
        stories_folders = [f for f in os.listdir(".\\stories\\") if os.path.isdir(os.path.join(".\\stories\\", f))]
        self.stories_folders_dropdown["values"] = stories_folders
        if stories_folders:
            self.stories_folders_dropdown.current(0)
    
    def load_stories_folder_content(self, event):
        selected_folder = self.stories_folders_dropdown.get()
        if not selected_folder:
            return
        stories_dir = os.path.join(".\\stories\\", selected_folder)
        try:
            files = [f for f in os.listdir(stories_dir) if f.endswith(".txt")]
            self.output_display.config(state="normal")
            self.output_display.delete(1.0, tk.END)
            for file in files:
                with open(os.path.join(stories_dir, file), "r") as f:
                    content = f.read()
                    self.output_display.insert(tk.END, f"--- {file} ---\n{content}\n\n")
            self.output_display.config(state="disabled")
        except FileNotFoundError:
            messagebox.showerror("Error", f"Directory not found: {stories_dir}")

    def refresh_processed_files(self):
        processed_files_dir = ".\\processed code\\"
        try:
            processed_files = [f for f in os.listdir(processed_files_dir) if f.endswith("(prompt used).txt")]
            self.processed_files_dropdown["values"] = processed_files
            if processed_files:
                self.processed_files_dropdown.current(0)
        except FileNotFoundError:
            self.processed_files_dropdown["values"] = []
            messagebox.showerror("Error", f"Directory not found: {processed_files_dir}")
    
    def load_processed_file_content(self, event):
        selected_file = self.processed_files_dropdown.get()
        if not selected_file:
            return
        processed_files_dir = ".\\processed code\\"
        try:
            with open(os.path.join(processed_files_dir, selected_file), "r") as file:
                content = file.read()
                self.text_editor.delete(1.0, tk.END)
                self.text_editor.insert(tk.END, content)
        except FileNotFoundError:
            messagebox.showerror("Error", f"File not found: {selected_file}")

    def load_prompt_file(self):
        try:
            with open(self.prompt_file, "r") as file:
                self.text_editor.delete(1.0, tk.END)
                self.text_editor.insert(tk.END, file.read())
        except FileNotFoundError:
            messagebox.showerror("Error", f"File not found: {self.prompt_file}")
    
    def save_prompt_file(self):
        try:
            with open(self.prompt_file, "w") as file:
                file.write(self.text_editor.get(1.0, tk.END).strip())
            messagebox.showinfo("Success", "File saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")
    
    def refresh_seed_files(self):
        seed_files = [f for f in os.listdir(self.seeds_dir) if f.startswith("seed") and f.endswith(".txt")]
        self.seed_files_dropdown["values"] = seed_files
        if seed_files:
            self.seed_files_dropdown.current(0)
    
    def refresh_non_seed_files(self):
        non_seed_files = [f for f in os.listdir(self.seeds_dir) if not f.startswith("seed") and f.endswith(".txt")]
        self.non_seed_files_dropdown["values"] = non_seed_files
        if non_seed_files:
            self.non_seed_files_dropdown.current(0)
    
    def run_generate_story(self):
        selected_file = self.seed_files_dropdown.get()
        if not selected_file:
            messagebox.showerror("Error", "No seed file selected!")
            return
        command = f"python .\generate_story.py \".\seeds\{selected_file}\""
        self.output_display.config(state="normal")
        self.output_display.delete(1.0, tk.END)
        self.output_display.insert(tk.END, "Running generate_story...\n")
        self.start_time = time.time()
        self.output_display.config(state="disabled")
        
        def run_async():
            try:
                process = subprocess.Popen(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                while True:
                    output = process.stdout.readline()
                    if output == "" and process.poll() is not None:
                        break
                    if output:
                        if '"Sentence Number":' in output:
                            self.output_display.config(state="normal")
                            elapsed = int(time.time() - self.start_time)
                            self.output_display.insert(tk.END, f"Progress: {output.strip()} ({elapsed} seconds)\n")
                            self.output_display.config(state="disabled")
                            self.output_display.see(tk.END)
                        if '"Sentence":' in output:
                            self.output_display.config(state="normal")
                            elapsed = int(time.time() - self.start_time)
                            self.output_display.insert(tk.END, f"{output.strip()}\n")
                            self.output_display.config(state="disabled")
                            self.output_display.see(tk.END)
                stderr = process.stderr.read()
                if stderr:
                    self.output_display.config(state="normal")
                    self.output_display.insert(tk.END, stderr)
                    self.output_display.config(state="disabled")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to run command: {e}")
            finally:
                self.output_display.config(state="normal")
                self.output_display.insert(tk.END, "\nFinished generate_story.\n")
                self.output_display.insert(tk.END, f"Total time taken: {int(time.time() - self.start_time)} seconds\n")
                self.output_display.config(state="disabled")
                self.output_display.see(tk.END)
        
        threading.Thread(target=run_async).start()
    
    def run_process_json(self):
        command = "python \".\process_json_files_updated (7).py\""
        self.output_display.config(state="normal")
        self.output_display.delete(1.0, tk.END)
        self.output_display.insert(tk.END, "Running process_json_files_updated...\n")
        self.output_display.config(state="disabled")
        
        def run_async():
            try:
                result = subprocess.run(command, shell=True, text=True, capture_output=True)
                self.output_display.config(state="normal")
                self.output_display.insert(tk.END, result.stdout + result.stderr + "\nFinished process_json_files_updated.\n")
                self.output_display.config(state="disabled")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to run command: {e}")
        
        threading.Thread(target=run_async).start()
    
    def run_generate_seed(self):
        selected_file = self.non_seed_files_dropdown.get()
        if not selected_file:
            messagebox.showerror("Error", "No non-seed file selected!")
            return
        story_name = selected_file.split(".")[0]
        command = f"python .\generate_seed.py \".\seeds\{selected_file}\" \"{story_name}\""
        self.output_display.config(state="normal")
        self.output_display.delete(1.0, tk.END)
        self.output_display.insert(tk.END, "Running generate_seed...\n")
        self.start_time = time.time()
        self.output_display.config(state="disabled")
        
        def run_async():
            try:
                process = subprocess.Popen(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                while True:
                    output = process.stdout.readline()
                    if output == "" and process.poll() is not None:
                        break
                    if output:
                        if '"Sentence Number":' in output:
                            self.output_display.config(state="normal")
                            elapsed = int(time.time() - self.start_time)
                            self.output_display.insert(tk.END, f"Progress: {output.strip()} ({elapsed} seconds)\n")
                            self.output_display.config(state="disabled")
                            self.output_display.see(tk.END)
                stderr = process.stderr.read()
                if stderr:
                    self.output_display.config(state="normal")
                    self.output_display.insert(tk.END, stderr)
                    self.output_display.config(state="disabled")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to run command: {e}")
            finally:
                self.output_display.config(state="normal")
                self.output_display.insert(tk.END, "\nFinished generate_seed.\n")
                self.output_display.config(state="disabled")
                self.output_display.see(tk.END)
                self.refresh_seed_files()
        
        threading.Thread(target=run_async).start()
    
    def run_command(self, command):
        try:
            result = subprocess.run(command, shell=True, text=True, capture_output=True)
            self.output_display.config(state="normal")
            self.output_display.delete(1.0, tk.END)
            self.output_display.insert(tk.END, result.stdout + result.stderr)
            self.output_display.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run command: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GUIApp(root)
    root.mainloop()