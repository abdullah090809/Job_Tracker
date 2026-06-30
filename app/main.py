from fastapi import FastAPI
from app.routers import application, auth, user

app = FastAPI(title="Job Tracker API")

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(application.router)

@app.get("/")
def root():
    return {"message": "Job Tracker API is running"}