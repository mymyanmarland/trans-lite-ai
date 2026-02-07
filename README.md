# AI Video Translator (English to Burmese)

This is a prototype for an AI-powered video translator that extracts audio from English videos, transcribes them using OpenAI Whisper, translates the text to Burmese using Gemini AI, and generates a downloadable SRT subtitle file.

## Features
- **Clean Modern UI**: Premium dark mode design with glassmorphism.
- **Whisper Transcription**: High-accuracy English transcription.
- **Gemini Translation**: Context-aware Burmese translation.
- **SRT Generation**: Standard subtitle format with both English and Burmese text.

## Setup
1. **API Key**: Add your Gemini API key to `backend/.env`.
   ```
   GEMINI_API_KEY=your_actual_key_here
   ```
2. **Run the Server**:
   ```bash
   ./run.sh
   ```
3. **Access the App**: Open your browser and go to `http://localhost:8000`.

## Notes
- The first run will download the Whisper "base" model (~140MB).
- Subtitle generation happens in the background. You can check the status on the UI.
- Large videos may take a few minutes to process.
