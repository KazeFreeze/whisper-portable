# whisper_gui/whisper_gui.py --- main.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import whisper
import datetime
import os
import threading
from pathlib import Path
import cv2
from whisper_gui.config_manager import ConfigManager


class WhisperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Whisper Transcription GUI")
        self.root.geometry("600x800")

        try:
            self.config_manager = ConfigManager()
        except Exception as e:
            messagebox.showerror(
                "Configuration Error", f"Error loading configuration: {e}"
            )
            self.config_manager = None

        # Create main frame with padding
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        current_row = 0

        # File Selection Frame
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="5")
        file_frame.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=5)
        main_frame.columnconfigure(0, weight=1)

        # Input File
        ttk.Label(file_frame, text="Input File:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.input_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.input_path, width=50).grid(
            row=0, column=1, pady=5, padx=5
        )
        ttk.Button(file_frame, text="Browse", command=self.browse_input).grid(
            row=0, column=2, padx=5, pady=5
        )

        # Output Path
        ttk.Label(file_frame, text="Output Path:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.output_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.output_path, width=50).grid(
            row=1, column=1, pady=5, padx=5
        )
        ttk.Button(file_frame, text="Browse", command=self.browse_output).grid(
            row=1, column=2, padx=5, pady=5
        )

        current_row += 1

        # Recent Paths Frame
        if self.config_manager:
            paths_frame = ttk.LabelFrame(main_frame, text="Recent Paths", padding="5")
            paths_frame.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=5)

            ttk.Label(paths_frame, text="Recent Inputs:").grid(
                row=0, column=0, sticky=tk.W
            )
            self.input_combo = ttk.Combobox(paths_frame, width=50)
            self.input_combo.grid(row=0, column=1, pady=5, padx=5)
            self.input_combo["values"] = self.config_manager.config["recent_inputs"]
            self.input_combo.bind(
                "<<ComboboxSelected>>",
                lambda e: self.input_path.set(self.input_combo.get()),
            )

            ttk.Label(paths_frame, text="Recent Outputs:").grid(
                row=1, column=0, sticky=tk.W
            )
            self.output_combo = ttk.Combobox(paths_frame, width=50)
            self.output_combo.grid(row=1, column=1, pady=5, padx=5)
            self.output_combo["values"] = self.config_manager.config["recent_outputs"]
            self.output_combo.bind(
                "<<ComboboxSelected>>",
                lambda e: self.output_path.set(self.output_combo.get()),
            )

            current_row += 1

        # Model Configuration Frame
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="5")
        config_frame.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=5)

        # Model Size
        ttk.Label(config_frame, text="Model Size:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.model_size = tk.StringVar(value="base")
        model_sizes = ["tiny", "base", "small", "medium", "large"]
        size_menu = ttk.OptionMenu(config_frame, self.model_size, "base", *model_sizes)
        size_menu.grid(row=0, column=1, sticky=tk.W, pady=5)
        self.model_size.trace_add("write", self.update_estimate)

        # Language
        ttk.Label(config_frame, text="Language:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.language = tk.StringVar(value="auto")
        languages = [
            "auto",
            "English",
            "Filipino",
            "Chinese",
            "Japanese",
            "Korean",
            "Spanish",
        ]
        ttk.OptionMenu(config_frame, self.language, "auto", *languages).grid(
            row=1, column=1, sticky=tk.W, pady=5
        )

        # Task Type
        ttk.Label(config_frame, text="Task:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.task = tk.StringVar(value="transcribe")
        tasks = ["transcribe", "translate"]
        ttk.OptionMenu(config_frame, self.task, "transcribe", *tasks).grid(
            row=2, column=1, sticky=tk.W, pady=5
        )

        # Output Format
        ttk.Label(config_frame, text="Output Format:").grid(
            row=3, column=0, sticky=tk.W, pady=5
        )
        self.output_format = tk.StringVar(value="srt")
        formats = ["srt", "txt", "vtt"]
        ttk.OptionMenu(config_frame, self.output_format, "srt", *formats).grid(
            row=3, column=1, sticky=tk.W, pady=5
        )

        current_row += 1

        # Segment Length Controls
        segment_frame = ttk.LabelFrame(
            main_frame, text="Segment Length Control", padding="5"
        )
        segment_frame.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=5)

        # Preset buttons
        presets_frame = ttk.Frame(segment_frame)
        presets_frame.grid(row=0, column=0, columnspan=3, pady=5)

        preset_values = [
            ("Short (3s)", 3.0),
            ("Medium (7s)", 7.0),
            ("Long (12s)", 12.0),
        ]

        for i, (text, value) in enumerate(preset_values):
            ttk.Button(
                presets_frame,
                text=text,
                command=lambda v=value: self.set_segment_length(v),
            ).grid(row=0, column=i, padx=5)

        # Custom slider
        ttk.Label(segment_frame, text="Custom Length:").grid(
            row=1, column=0, sticky=tk.W
        )
        self.segment_length = tk.DoubleVar(value=7.0)
        self.segment_slider = ttk.Scale(
            segment_frame,
            from_=1.0,
            to=30.0,
            orient="horizontal",
            variable=self.segment_length,
            length=200,
        )
        self.segment_slider.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        self.segment_length_label = ttk.Label(segment_frame, text="7.0s")
        self.segment_slider.configure(command=self.update_segment_length_label)
        self.segment_length_label.grid(row=1, column=2, padx=5)
        self.segment_length.trace_add("write", self.update_estimate)

        current_row += 1

        # Additional Options Frame
        options_frame = ttk.LabelFrame(
            main_frame, text="Additional Options", padding="5"
        )
        options_frame.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=5)

        self.word_timestamps = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame, text="Word-level timestamps", variable=self.word_timestamps
        ).grid(row=0, column=0, sticky=tk.W)
        self.word_timestamps.trace_add("write", self.update_estimate)

        self.compute_confidence = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Compute confidence scores",
            variable=self.compute_confidence,
        ).grid(row=1, column=0, sticky=tk.W)

        current_row += 1

        # Processing Time Estimate Frame
        self.estimate_frame = ttk.LabelFrame(
            main_frame, text="Processing Time Estimate", padding="5"
        )
        self.estimate_frame.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=5)
        self.estimate_label = ttk.Label(
            self.estimate_frame, text="Estimated processing time: Select an input file"
        )
        self.estimate_label.grid(row=0, column=0, pady=5)

        current_row += 1

        # Progress Frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=5)

        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            progress_frame, length=400, mode="determinate", variable=self.progress_var
        )
        self.progress.grid(row=0, column=0, columnspan=2, pady=5)

        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, columnspan=2)

        current_row += 1

        # Process Button
        self.process_button = ttk.Button(
            main_frame, text="Process File", command=self.process_file
        )
        self.process_button.grid(row=current_row, column=0, pady=10)

        current_row += 1

        # Log Area
        self.log_text = tk.Text(main_frame, height=10, width=70)
        self.log_text.grid(row=current_row, column=0, pady=10)

    def browse_input(self):
        filename = filedialog.askopenfilename(
            filetypes=[
                (
                    "Media files",
                    "*.mp4 *.avi *.mkv *.mov *.mp3 *.wav *.flac *.ogg *.m4a",
                ),
                ("Video files", "*.mp4 *.avi *.mkv *.mov"),
                ("Audio files", "*.mp3 *.wav *.flac *.ogg *.m4a"),
                ("All files", "*.*"),
            ]
        )
        if filename:
            self.input_path.set(filename)
            # Auto-set output path if empty
            if not self.output_path.get():
                output_dir = os.path.dirname(filename)
                base_name = os.path.splitext(os.path.basename(filename))[0]
                self.output_path.set(
                    os.path.join(output_dir, f"{base_name}.{self.output_format.get()}")
                )

            # Update estimate after file selection
            self.update_estimate()

    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=f".{self.output_format.get()}",
            filetypes=[
                ("SRT files", "*.srt"),
                ("Text files", "*.txt"),
                ("VTT files", "*.vtt"),
            ],
        )
        if filename:
            self.output_path.set(filename)

    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

    def format_timestamp(self, seconds):
        """Convert seconds to SRT/VTT timestamp format with improved precision"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        msec = int((seconds % 1) * 1000)
        seconds = int(seconds)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{msec:03d}"

    def process_file(self):
        if not self.input_path.get() or not self.output_path.get():
            messagebox.showerror("Error", "Please select input and output paths")
            return

        self.process_button.state(["disabled"])
        self.status_var.set("Processing...")
        self.progress_var.set(0)

        # Start processing in a separate thread
        thread = threading.Thread(target=self.run_processing)
        thread.daemon = True
        thread.start()

    def run_processing(self):
        start_time = datetime.datetime.now()
        try:
            self.log_message("Loading model...")
            model = whisper.load_model(self.model_size.get())

            self.log_message("Transcribing media...")
            result = model.transcribe(
                self.input_path.get(),
                language=(
                    None
                    if self.language.get() == "auto"
                    else self.language.get().lower()
                ),
                task=self.task.get(),
                word_timestamps=self.word_timestamps.get(),
            )

            self.log_message("Writing output...")
            self.write_output(result)

            self.status_var.set("Processing complete!")
            self.progress_var.set(100)
            messagebox.showinfo("Success", "Processing completed successfully!")

            # After successful processing, save the record
            end_time = datetime.datetime.now()
            processing_time = (end_time - start_time).total_seconds() / 60.0

            # Get duration and file size
            duration = self.get_media_duration(self.input_path.get())
            file_size = os.path.getsize(self.input_path.get())

            self.config_manager.add_processing_record(
                file_size,
                duration,
                self.model_size.get(),
                self.word_timestamps.get(),
                self.segment_length.get(),
                processing_time,
            )

            # Save paths
            self.config_manager.add_paths(self.input_path.get(), self.output_path.get())

            # Update dropdowns
            self.input_combo["values"] = self.config_manager.config["recent_inputs"]
            self.output_combo["values"] = self.config_manager.config["recent_outputs"]

        except Exception as e:
            self.status_var.set("Error occurred!")
            messagebox.showerror("Error", str(e))
            self.log_message(f"Error: {str(e)}")

        finally:
            self.process_button.state(["!disabled"])

    def get_media_duration(self, file_path):
        """Get the duration of media file (video or audio)"""
        try:
            # Try to open as video first
            cap = cv2.VideoCapture(file_path)
            if cap.isOpened():
                duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
                cap.release()
                return duration
            else:
                # Failed to get video duration, use a default value
                # Ideally, we would use a library like librosa or pydub for audio files
                # but keeping dependencies minimal for now
                self.log_message("Warning: Could not determine media duration")
                return -1
        except Exception as e:
            self.log_message(f"Warning: Error getting media duration - {str(e)}")
            return -1

    def write_output(self, result):
        output_format = self.output_format.get()
        segment_gap = 0.01  # 10ms gap between segments to prevent overlap

        with open(self.output_path.get(), "w", encoding="utf-8") as f:
            if output_format == "srt":
                for i, segment in enumerate(result["segments"], start=1):
                    # Ensure there's no overlap with the next segment
                    current_end = segment["end"]
                    if i < len(result["segments"]):
                        next_start = result["segments"][i]["start"]
                        if current_end > next_start:
                            current_end = next_start - segment_gap

                    f.write(f"{i}\n")
                    f.write(
                        f"{self.format_timestamp(segment['start'])} --> {self.format_timestamp(current_end)}\n"
                    )
                    f.write(f"{segment['text'].strip()}\n\n")

            elif output_format == "vtt":
                f.write("WEBVTT\n\n")
                for i, segment in enumerate(result["segments"]):
                    # Ensure there's no overlap with the next segment
                    current_end = segment["end"]
                    if i < len(result["segments"]):
                        next_start = result["segments"][i]["start"]
                        if current_end > next_start:
                            current_end = next_start - segment_gap

                    f.write(
                        f"{self.format_timestamp(segment['start']).replace(',', '.')} --> {self.format_timestamp(current_end).replace(',', '.')}\n"
                    )
                    f.write(f"{segment['text'].strip()}\n\n")

            else:  # txt
                f.write(result["text"])

    def set_segment_length(self, value):
        """Update segment length and label when preset is clicked"""
        self.segment_length.set(value)
        self.update_segment_length_label(value)

    def update_segment_length_label(self, value):
        """Update the label showing current segment length"""
        try:
            self.segment_length_label.config(text=f"{float(value):.1f}s")
        except ValueError:
            pass

    def update_estimate(self, *args):
        """Update processing time estimate"""
        if not self.input_path.get() or not self.config_manager:
            return

        try:
            duration = self.get_media_duration(self.input_path.get())

            if duration > 0:
                estimate = self.config_manager.estimate_processing_time(
                    duration, self.model_size.get(), self.word_timestamps.get()
                )

                if estimate > 0:
                    self.estimate_label.config(
                        text=f"Estimated processing time: {estimate:.1f} minutes"
                    )
                else:
                    self.estimate_label.config(
                        text="Estimated processing time: calculating..."
                    )
            else:
                self.estimate_label.config(
                    text="Estimated processing time: unknown (new media type)"
                )
        except Exception as e:
            self.estimate_label.config(text="Estimated processing time: unavailable")
            print(f"Error updating estimate: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = WhisperGUI(root)
    root.mainloop()
