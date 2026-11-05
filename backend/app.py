import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from backend.config import settings
from backend.routers import health, meeting

app = FastAPI(
    title="Meeting Voice Assistant",
    description="Real-time Executive Meeting AI Scribe & Scribe Studio"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(meeting.router)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

if os.path.exists(PUBLIC_DIR):
    css_dir = os.path.join(PUBLIC_DIR, "css")
    js_dir = os.path.join(PUBLIC_DIR, "js")
    if os.path.exists(css_dir):
        app.mount("/css", StaticFiles(directory=css_dir), name="css")
    if os.path.exists(js_dir):
        app.mount("/js", StaticFiles(directory=js_dir), name="js")

@app.get("/", response_class=HTMLResponse)
async def index():
    idx = os.path.join(PUBLIC_DIR, "index.html")
    if os.path.exists(idx):
        return FileResponse(idx)
    return HTMLResponse("<h1>Meeting Voice Assistant</h1>")
