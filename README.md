# Whisper Transcription GUI

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

Whisper Transcription GUI is a desktop application that allows you to transcribe audio and video files into text using OpenAI's Whisper model. The tool supports multiple output formats (SRT, TXT, VTT) and provides options for language selection, task type (transcribe or translate), and word-level timestamps.

## Features

- **Audio & Video Transcription**: Transcribe audio and video files into text using OpenAI's Whisper model.
- **Multiple Output Formats**: Save transcriptions in SRT, TXT, or VTT formats.
- **Language Selection**: Supports multiple languages (e.g., English, Chinese, Japanese, etc.) with an "auto" option for automatic language detection.
- **Task Type**: Choose between transcription or translation tasks.
- **Word-Level Timestamps**: Optionally include word-level timestamps in the output.
- **Processing History**: Tracks recent inputs, outputs, and processing history for easy access.
- **Processing Time Estimation**: Provides an estimate of the time required to process a file based on historical data.

## Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (automatically downloaded during setup)

### Steps

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/whisper-transcription-gui.git
    cd whisper-transcription-gui
    ```
2.  **Set up the virtual environment**:

    - On Windows:
      ```bash
      python -m venv whisper-env
      whisper-env\Scripts\activate
      ```
    - On macOS/Linux:
      ```bash
      python3 -m venv whisper-env
      source whisper-env/bin/activate
      ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the build script (Windows only)**:

    ```bash
    build_portable.bat
    ```

    This script will:

    - Set up the virtual environment.

    - Install required packages.

    - Download FFmpeg.

    - Create a launcher script (`run_whisper_gui.bat`).

5.  **Launch the application**:

    - On Windows:
      ```bash
      run_whisper_gui.bat
      ```
    - On macOS/Linux:
      ```bash
      python -m whisper_gui.main
      ```

## Usage

1. **Select Input File**: Click "Browse" to select the audio or video file you want to transcribe.
2. **Set Output Path**: Choose where to save the transcription file (SRT, TXT, or VTT).
3. **Configure Settings**:
   - **Model Size**: Choose the Whisper model size (tiny, base, small, medium, large).
   - **Language**: Select the language of the audio or use "auto" for automatic language detection.
   - **Task**: Choose between "transcribe" (convert speech to text) or "translate" (translate speech to English).
   - **Output Format**: Select the desired output format (SRT, TXT, VTT).
   - **Word-Level Timestamps**: Enable this option to include word-level timestamps in the output.
4. **Process File**: Click "Process File" to start the transcription process. The estimated processing time will be displayed.

## Supported File Formats

### Audio Formats

- MP3 (.mp3)
- WAV (.wav)
- FLAC (.flac)
- OGG (.ogg)
- M4A (.m4a)

### Video Formats

- MP4 (.mp4)
- AVI (.avi)
- MKV (.mkv)
- MOV (.mov)

## Configuration

The application stores user preferences and processing history in a configuration file (`whisper_config.json`). This file is automatically created in the `whisper_gui` directory and is ignored by Git to ensure user-specific data is not shared.

### Template Configuration

A template configuration file (`whisper_config_template.json`) is provided. Users can rename this file to `whisper_config.json` and customize it as needed.

## Dependencies

- **OpenAI Whisper**: For audio transcription.
- **Torch**: For running the Whisper model.
- **OpenCV**: For video processing.
- **Tkinter**: For the graphical user interface.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.
