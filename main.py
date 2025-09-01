from fastapi import FastAPI
from src.routes.auth import router as auth_router
from src.routes.task import router as task_router
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Personal_Pro")

app.include_router(auth_router)
app.include_router(task_router)

app.mount("/static", StaticFiles(directory="static"), name="static")