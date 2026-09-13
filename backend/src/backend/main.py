from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import auth, boards, realtime, sessions

app = FastAPI(
    title="Collaborative System Design Interview Platform API",
    description="Backend REST & WebSocket service for interview sessions and real-time canvas collaboration",
    version="1.0.0",
)

# Enable CORS for frontend development (supporting localhost:8080, 3000, 5173, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include sub-routers
app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(boards.router)
app.include_router(realtime.router)

@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "interview-platform-backend"}

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Collaborative System Design Interview Platform API is running",
        "docs": "/docs",
        "health": "/api/health",
    }
