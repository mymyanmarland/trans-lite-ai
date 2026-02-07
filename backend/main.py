import os
import sys
import uuid
import shutil
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import google.generativeai as genai
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

# Add local libs to path
sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
STATIC_DIR = "static"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def process_video_with_gemini(video_path, task_id):
    try:
        if not GEMINI_API_KEY:
            raise Exception("GEMINI_API_KEY not found in environment")

        # 1. Upload file to Gemini
        print(f"Uploading {video_path} to Gemini...")
        video_file = genai.upload_file(path=video_path)
        
        # 2. Generate Subtitles using Gemini 1.5 Flash
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = """
        Analyze this video and generate subtitles. 
        For each spoken segment, provide:
        1. Start and End timestamps (in HH:MM:SS,mmm format)
        2. Original English text
        3. Burmese translation
        
        Output the result ONLY as a valid SRT file content.
        Each subtitle block should look like:
        [Index]
        [Start] --> [End]
        [English Text]
        [Burmese Translation]
        """
        
        response = model.generate_content([video_file, prompt])
        srt_content = response.text.strip()
        
        # Simple cleanup if Gemini wraps it in markdown
        if "```" in srt_content:
            parts = srt_content.split("```")
            for part in parts:
                if "-->" in part:
                    srt_content = part.strip()
                    if srt_content.startswith("srt"):
                        srt_content = srt_content[3:].strip()
                    break

        srt_path = os.path.join(STATIC_DIR, f"{task_id}.srt")
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(srt_content)
            
        # Cleanup uploaded video to Gemini (optional but good practice)
        # genai.delete_file(video_file.name)
        
        # Cleanup local video
        if os.path.exists(video_path):
            os.remove(video_path)
            
        return srt_path
    except Exception as e:
        print(f"Error processing video: {e}")
        return None

@app.post("/upload")
async def upload_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    task_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    video_path = os.path.join(UPLOAD_DIR, f"{task_id}{ext}")
    
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    background_tasks.add_task(process_video_with_gemini, video_path, task_id)
    
    return {"task_id": task_id, "status": "processing"}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    srt_path = os.path.join(STATIC_DIR, f"{task_id}.srt")
    if os.path.exists(srt_path):
        return {"status": "completed", "download_url": f"/download/{task_id}"}
    return {"status": "processing"}

@app.get("/download/{task_id}")
async def download_srt(task_id: str):
    srt_path = os.path.join(STATIC_DIR, f"{task_id}.srt")
    if os.path.exists(srt_path):
        return FileResponse(srt_path, filename="translated_subtitles.srt")
    return {"error": "File not found"}

# Serve frontend
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
