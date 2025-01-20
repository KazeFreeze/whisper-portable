import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import whisper
import datetime
import os
import threading

class WhisperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Whisper Transcription GUI")
        self.root.geometry("600x700")
        
        # Create main frame with padding
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # File Selection
        ttk.Label(main_frame, text="Input Video:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.input_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.input_path, width=50).grid(row=0, column=1, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_input).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(main_frame, text="Output Path:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.output_path, width=50).grid(row=1, column=1, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)
        
        # Model Configuration
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="5")
        config_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Model Size
        ttk.Label(config_frame, text="Model Size:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.model_size = tk.StringVar(value="base")
        model_sizes = ["tiny", "base", "small", "medium", "large"]
        ttk.OptionMenu(config_frame, self.model_size, "base", *model_sizes).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Language
        ttk.Label(config_frame, text="Language:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.language = tk.StringVar(value="auto")
        languages = ["auto", "English", "Filipino", "Chinese", "Japanese", "Korean", "Spanish"]
        ttk.OptionMenu(config_frame, self.language, "auto", *languages).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Task Type
        ttk.Label(config_frame, text="Task:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.task = tk.StringVar(value="transcribe")
        tasks = ["transcribe", "translate"]
        ttk.OptionMenu(config_frame, self.task, "transcribe", *tasks).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Output Format
        ttk.Label(config_frame, text="Output Format:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.output_format = tk.StringVar(value="srt")
        formats = ["srt", "txt", "vtt"]
        ttk.OptionMenu(config_frame, self.output_format, "srt", *formats).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Additional Options
        options_frame = ttk.LabelFrame(main_frame, text="Additional Options", padding="5")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.word_timestamps = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Word-level timestamps", variable=self.word_timestamps).grid(row=0, column=0, sticky=tk.W)
        
        self.compute_confidence = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Compute confidence scores", variable=self.compute_confidence).grid(row=1, column=0, sticky=tk.W)
        
        # Progress
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(main_frame, length=400, mode='determinate', variable=self.progress_var)
        self.progress.grid(row=4, column=0, columnspan=3, pady=10)
        
        # Status
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=5, column=0, columnspan=3)
        
        # Process Button
        self.process_button = ttk.Button(main_frame, text="Process Video", command=self.process_video)
        self.process_button.grid(row=6, column=0, columnspan=3, pady=10)
        
        # Log Area
        self.log_text = tk.Text(main_frame, height=10, width=70)
        self.log_text.grid(row=7, column=0, columnspan=3, pady=10)
        
    def browse_input(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4 *.avi *.mkv *.mov"), ("All files", "*.*")]
        )
        if filename:
            self.input_path.set(filename)
            # Auto-set output path if empty
            if not self.output_path.get():
                output_dir = os.path.dirname(filename)
                base_name = os.path.splitext(os.path.basename(filename))[0]
                self.output_path.set(os.path.join(output_dir, f"{base_name}.{self.output_format.get()}"))

    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=f".{self.output_format.get()}",
            filetypes=[("SRT files", "*.srt"), ("Text files", "*.txt"), ("VTT files", "*.vtt")]
        )
        if filename:
            self.output_path.set(filename)

    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        
    def format_timestamp(self, seconds):
        """Convert seconds to SRT timestamp format"""
        return str(datetime.timedelta(seconds=seconds)).replace('.', ',')[:12]

    def process_video(self):
        if not self.input_path.get() or not self.output_path.get():
            messagebox.showerror("Error", "Please select input and output paths")
            return
            
        self.process_button.state(['disabled'])
        self.status_var.set("Processing...")
        self.progress_var.set(0)
        
        # Start processing in a separate thread
        thread = threading.Thread(target=self.run_processing)
        thread.daemon = True
        thread.start()

    def run_processing(self):
        try:
            self.log_message("Loading model...")
            model = whisper.load_model(self.model_size.get())
            
            self.log_message("Transcribing video...")
            result = model.transcribe(
                self.input_path.get(),
                language=None if self.language.get() == "auto" else self.language.get().lower(),
                task=self.task.get(),
                word_timestamps=self.word_timestamps.get()
            )
            
            self.log_message("Writing output...")
            self.write_output(result)
            
            self.status_var.set("Processing complete!")
            self.progress_var.set(100)
            messagebox.showinfo("Success", "Processing completed successfully!")
            
        except Exception as e:
            self.status_var.set("Error occurred!")
            messagebox.showerror("Error", str(e))
            self.log_message(f"Error: {str(e)}")
        
        finally:
            self.process_button.state(['!disabled'])

    def write_output(self, result):
        output_format = self.output_format.get()
        
        with open(self.output_path.get(), "w", encoding="utf-8") as f:
            if output_format == "srt":
                for i, segment in enumerate(result["segments"], start=1):
                    f.write(f"{i}\n")
                    f.write(f"{self.format_timestamp(segment['start'])} --> {self.format_timestamp(segment['end'])}\n")
                    f.write(f"{segment['text'].strip()}\n\n")
                    
            elif output_format == "vtt":
                f.write("WEBVTT\n\n")
                for segment in result["segments"]:
                    f.write(f"{self.format_timestamp(segment['start']).replace(',', '.')} --> {self.format_timestamp(segment['end']).replace(',', '.')}\n")
                    f.write(f"{segment['text'].strip()}\n\n")
                    
            else:  # txt
                f.write(result["text"])

if __name__ == "__main__":
    root = tk.Tk()
    app = WhisperGUI(root)
    root.mainloop()