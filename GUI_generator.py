import os
import subprocess
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import threading

class GUIApp:
    def __init__(self, root):
        WIDTH = 160

        self.root = root
        self.root.title("GUI Generator")
        
        # File paths
        self.prompt_file = ".\\prompt\\prompt_text.txt"
        self.seeds_dir = ".\\seeds\\"
        
        # Dropdown for processed code files
        tk.Label(root, text="Processed Code Files:").grid(row=0, column=0, sticky=tk.W, padx=10)
        self.processed_files_dropdown = ttk.Combobox(root, state="readonly", width=100)
        self.processed_files_dropdown.grid(row=0, column=1, padx=10)
        self.refresh_processed_files()

        # Bind selection event to load file content
        self.processed_files_dropdown.bind("<<ComboboxSelected>>", self.load_processed_file_content)

        # Text editor
        self.text_editor = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=WIDTH, height=30)
        self.text_editor.grid(row=1, column=0, columnspan=3, padx=10, pady=10)
        self.load_prompt_file()
        
        # Save button
        save_button = tk.Button(root, text="Save prompt file", command=self.save_prompt_file)
        save_button.grid(row=2, column=0, padx=10, pady=5)
        
        # Dropdown for "seed" files
        tk.Label(root, text="Seed Files:").grid(row=3, column=0, sticky=tk.W, padx=10)
        self.seed_files_dropdown = ttk.Combobox(root, state="readonly", width=50)
        self.seed_files_dropdown.grid(row=3, column=1, padx=10)
        self.refresh_seed_files()
        
        # Run generate_story.py button
        run_generate_story_button = tk.Button(root, text="Run generate_story.py", command=self.run_generate_story)
        run_generate_story_button.grid(row=3, column=2, padx=10, pady=5)
        
        # Run process_json_files_updated.py button
        run_process_json_button = tk.Button(root, text="Run process_json_files_updated.py", command=self.run_process_json)
        run_process_json_button.grid(row=4, column=0, columnspan=3, pady=5)
        
        # Dropdown for non-"seed" files
        tk.Label(root, text="Non-Seed Files:").grid(row=5, column=0, sticky=tk.W, padx=10)
        self.non_seed_files_dropdown = ttk.Combobox(root, state="readonly", width=50)
        self.non_seed_files_dropdown.grid(row=5, column=1, padx=10)
        self.refresh_non_seed_files()
        
        # Run generate_seed.py button
        run_generate_seed_button = tk.Button(root, text="Run generate_seed.py", command=self.run_generate_seed)
        run_generate_seed_button.grid(row=5, column=2, padx=10, pady=5)
        
        # Output display
        self.output_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=WIDTH, height=30, state="disabled")
        self.output_display.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

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