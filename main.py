from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from src.routes.auth import router as auth_router
from src.routes.task import router as task_router

app = FastAPI(title="Personal_Pro")

# Routers
app.include_router(auth_router)
app.include_router(task_router)

# Templates
templates = Jinja2Templates(directory="templates")

# Root route
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")
