from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.config.db import db

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get('/login')
def show_login(request: Request):
    if request.cookies.get("user_session"):
        return RedirectResponse('/dashboard', status_code=303)
    return templates.TemplateResponse("login.html", {'request': request, 'error': 'User_Not_Valid'})


@router.post('/login')
def login(request: Request, email: str = Form(...), password: str = Form(...)):
    result = db.auth.sign_in_with_password({
        "email": email,
        "password": password
    })
    # result = db.auth.sign_up({ 
    # "email": email, 
    # "password": password 
    # })
    if result and result.session and result.session.access_token:
        cookie = result.session.access_token
        
        redirect_response = RedirectResponse(url="/dashboard", status_code=303)
        redirect_response.set_cookie(
            key="user_session",
            value=cookie,
            httponly=True,
            max_age=60*60,   # 1 hour
            samesite="lax"
        )
        return redirect_response

    return templates.TemplateResponse("login.html", {'request': request, 'error': 'Login_Failed'})
