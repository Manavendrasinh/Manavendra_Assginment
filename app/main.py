# app/main.py
from fastapi import FastAPI
from app.core.config import settings
from app.api.routers import auth as auth_router
from app.api.routers import users as users_router 
from app.api.routers import events as events_router 


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for a Collaborative Event Management System.",
    version="0.1.0",
    openapi_url="/api/v1/openapi.json" 
)

# Include your routers
app.include_router(auth_router.router)
app.include_router(users_router.router) 
app.include_router(events_router.router) 

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

# To run: uvicorn app.main:app --reload
