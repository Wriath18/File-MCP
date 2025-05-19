# File System Manager with Gemini AI

A Streamlit-based application that uses Gemini API to process natural language commands for managing your file system.

## Features

- Organize files by type
- Rename files based on user requirements
- Move files between folders
- Natural language command processing
- Simple and intuitive UI

## Requirements

- Python 3.8+
- Streamlit
- Google Generative AI package
- Gemini API key

## Installation

1. Clone the repository
2. Install the requirements:
   ```
   pip install streamlit google-generativeai
   ```
3. Create a `.streamlit/secrets.toml` file with your Gemini API key:
   ```
   GEMINI_API_KEY = "your-api-key"
   ```

## Usage

1. Run the application:
   ```
   ./start_file_manager.sh
   ```
   or
   ```
   streamlit run file_manager.py
   ```

2. Enter the path to the directory you want to manage
3. Use natural language commands to organize your files, for example:
   - "Move all images to a Photos folder"
   - "Rename all PDF files to include today's date"
   - "Organize files by type"

## Notes

- The application only works on the directory you specify
- All operations are executed in the specified directory only
- Optimized for macOS environment, but should work on any platform

## Security

- The application only operates on the directory you specify
- Be cautious when using delete commands
- Review operations before confirming execution
