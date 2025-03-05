from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import matches, analytics, predictions
from app.database import init_db

app = FastAPI(title="Marvel Rivals Analytics")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(matches.router, prefix="/api/matches", tags=["matches"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/")
async def root():
    return {"message": "Welcome to Marvel Rivals Analytics API"} 