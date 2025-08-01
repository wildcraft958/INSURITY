"""
FastAPI application entrypoint for telematics insurance platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Telematics Insurance API",
    description="AI-powered telematics insurance platform with expert models",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Telematics Insurance API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
