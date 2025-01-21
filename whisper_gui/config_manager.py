# whisper_gui/config_manager.py
import json
import os
from datetime import datetime
from pathlib import Path


class ConfigManager:
    def __init__(self):
        self.config_file = Path(os.path.dirname(__file__)) / "whisper_config.json"
        self.config = {
            "recent_inputs": [],
            "recent_outputs": [],
            "processing_history": [],
        }
        self.load_config()

    def load_config(self):
        """Load configuration from JSON file, creating default if doesn't exist"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    # Validate and merge with default config
                    for key in self.config:
                        if key in loaded_config and isinstance(
                            loaded_config[key], list
                        ):
                            self.config[key] = loaded_config[key]
        except Exception as e:
            print(f"Error loading config: {e}")
            # Keep default config if loading fails

    def save_config(self):
        """Save current configuration to JSON file"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    def add_paths(self, input_path, output_path):
        """Add paths to recent lists, maintaining uniqueness and limit"""
        if input_path and input_path not in self.config["recent_inputs"]:
            self.config["recent_inputs"].insert(0, input_path)
            self.config["recent_inputs"] = self.config["recent_inputs"][:5]

        if output_path and output_path not in self.config["recent_outputs"]:
            self.config["recent_outputs"].insert(0, output_path)
            self.config["recent_outputs"] = self.config["recent_outputs"][:5]

        self.save_config()

    def add_processing_record(
        self,
        video_size,
        duration,
        model_size,
        word_timestamps,
        segment_length,
        processing_time,
    ):
        """Add a processing record to history"""
        try:
            self.config["processing_history"].append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "video_size": float(video_size),
                    "duration": float(duration),
                    "model_size": str(model_size),
                    "word_timestamps": bool(word_timestamps),
                    "segment_length": float(segment_length),
                    "processing_time": float(processing_time),
                }
            )
            # Keep last 20 records
            self.config["processing_history"] = self.config["processing_history"][-20:]
            self.save_config()
        except Exception as e:
            print(f"Error adding processing record: {e}")

    def estimate_processing_time(self, video_duration, model_size, word_timestamps):
        """Estimate processing time based on history or base estimates"""
        try:
            # Base estimates in minutes for 1 minute of video
            base_estimates = {
                "tiny": 0.2,
                "base": 0.3,
                "small": 0.5,
                "medium": 0.8,
                "large": 1.2,
            }

            # If we have history, use it for better estimates
            if self.config["processing_history"]:
                similar_jobs = [
                    job
                    for job in self.config["processing_history"]
                    if job["model_size"] == model_size
                    and job["word_timestamps"] == word_timestamps
                ]
                if similar_jobs:
                    avg_rate = sum(
                        job["processing_time"] / job["duration"] for job in similar_jobs
                    ) / len(similar_jobs)
                    return avg_rate * video_duration

            # Fall back to base estimates
            estimate = base_estimates.get(model_size, 0.3) * video_duration
            if word_timestamps:
                estimate *= 1.5  # Word timestamps add ~50% processing time

            return estimate
        except Exception as e:
            print(f"Error calculating estimate: {e}")
            return 0.0
