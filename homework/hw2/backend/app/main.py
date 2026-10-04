from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import waitlist, tables, notifications, analytics

app = FastAPI(
    title="TableHop API",
    description="Restaurant Waitlist & Table Management API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(waitlist.router)
app.include_router(tables.router)
app.include_router(notifications.router)
app.include_router(analytics.router)




@app.get("/")
def root():
    return {
        "service": "TableHop API",
        "status": "online",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "waitlist": "/api/waitlist",
            "tables": "/api/tables",
            "notifications": "/api/notifications",
            "analytics": "/api/analytics/summary",
        },
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "TableHop API"}


