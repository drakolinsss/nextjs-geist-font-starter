import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Read Tor hostname and setup
    try:
        hostname_path = "/var/lib/tor/zuno_service/hostname"
        if os.path.exists(hostname_path):
            with open(hostname_path, 'r') as f:
                onion_url = f.read().strip()
            logger.info(f"🧅 Zuno is live on http://{onion_url}")
        else:
            logger.warning("Tor hostname file not found. Service might not be accessible via .onion")
    except Exception as e:
        logger.error(f"Error reading Tor hostname: {e}")
    
    # Database initialization would go here
    
    yield
    
    # Cleanup
    logger.info("Shutting down application...")

# Initialize FastAPI
app = FastAPI(
    title="Zuno Marketplace API",
    description="A secure marketplace API with Tor integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - restrict in production to only allow .onion addresses
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Import and include routers
# We'll create these files next
from routers import products, comments, auth

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(comments.router, prefix="/api/comments", tags=["Comments"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
