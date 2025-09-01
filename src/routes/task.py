from fastapi import APIRouter, Form, Request, Response, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from src.config.db import db
from io import BytesIO
from typing import List
import random 

templates = Jinja2Templates(directory="templates")
router = APIRouter()



def get_loggin(request: Request):
    token = request.cookies.get("user_session")
    if token:
        result = db.auth.get_user(token)
        if result:
            return result.user
    return None
        

@router.get("/dashboard")
async def dashboard(request: Request):
    user = get_loggin(request)
    if not user:
        return RedirectResponse("/login")
    
    # fetch task
    task_result = db.table("task").select("*").eq("user_id", user.id).execute()
    tasks = task_result.data if task_result.data else []  
    
    #fetch notes
    notes_result = db.table("notes").select("*").eq("user_id", user.id).execute()
    notes = notes_result.data if notes_result.data else []
    
    #fetch files
    bucket_name = "files"
    files_result = db.storage.from_(bucket_name).list()
    files = files_result if files_result else []
    
    # fetch images
    bucket_name = "images"
    images_result = db.storage.from_(bucket_name).list()
    images = images_result if images_result else []
    random_images = random.sample(images, min(3, len(images)))
    for img in images:
        try:
            signed_url_response = db.storage.from_(bucket_name).create_signed_url(img["name"], 3600)
            img["url"] = signed_url_response.get("signedURL", "")
        except Exception as e:
            print(f"Error generating signed URL for {img['name']}: {e}")
            img["url"] = ""
            

        
    return templates.TemplateResponse("index.html", {
        "request": request,
        "tasks": tasks,
        "notes": notes, 
        "files": files,
        "images": images,
        "overview": random_images
        })
    
    
    



@router.get('/logout')
def logout(response: Response):
    response = RedirectResponse(url='/login')
    response.delete_cookie("user_session")
    return response

      

    
# ----------------- UPDATE: Edit Task -----------------
@router.get("/edittask/{task_id}")
async def edit_task_form(request: Request, task_id: int):
    user = get_loggin(request)
    if not user:
        return RedirectResponse("/login")

    task = db.table("task").select("*").eq("id", task_id).eq("user_id", user.id).execute()
    if not task.data:
        return RedirectResponse("/dashboard#todo")
    return templates.TemplateResponse("edit_task.html", {"request": request, "task": task.data[0]})


@router.post("/edittask")
async def update_task(request: Request, id: int = Form(...), title: str = Form(...), description: str = Form(...), status: str = Form(...)):
    user = get_loggin(request)
    if not user:
        return RedirectResponse("/login")

    db.table("task").update({
        "title": title,
        "description": description,
        "status": status
    }).eq("id", id).eq("user_id", user.id).execute()

    return RedirectResponse("/dashboard#todo", status_code=303)
    
   
#----New Task-----
    
@router.post('/newtask')
async def newtask(request: Request, title = Form(...), description = Form(...), status = Form(...)):
    user = get_loggin(request)
    if user:
        user_id = user.id   
        result = db.table('task').insert({
            'title': title,
            'description': description,
            'status': status,
            'user_id': user_id
        }).execute()
        if result.data:
            return templates.TemplateResponse("task_success.html", {'request': request})
        else:
            return RedirectResponse("/dashboard#todo", status_code=303)
    else:
        return RedirectResponse("/login")
    
@router.get('/newtask')
async def newtask(request: Request):
    if get_loggin(request):
        return templates.TemplateResponse("nw_task.html", {'request': request})
    else:
        return RedirectResponse('/login')   

#-----Delete Task----

@router.post("/deltask/{task_id}")
async def delete_task(request: Request, task_id: int):
    user = get_loggin(request)
    if not user:
        return RedirectResponse("/login")
    
    db.table("task").delete().eq("id", task_id).eq("user_id", user.id).execute()
    return RedirectResponse("/dashboard#todo", status_code=303)





#---------------Notes------------------

@router.get('/notes')
async def notes(request: Request):
    user = get_loggin(request)
    if not user:
        return RedirectResponse("/login")
    
    notes = db.table("notes").select("*").eq("user_id", user.id).execute()
    return templates.TemplateResponse("notes.html", {
        'request': request,
        'note': notes.data
    })


@router.post('/notes')
async def post_notes(request: Request, title = Form(...), info = Form(...)):
    user = get_loggin(request)
    if user:
        user_id = user.id   
        result = db.table('notes').insert({
            'title': title,
            'info': info,
            'user_id': user_id
        }).execute()
        if result.data:
            return RedirectResponse("/dashboard#notes", status_code=303)

#---------DELETE TASK-----------
     
@router.post("/delnotes/{notes_id}")
async def delete_notes(request: Request, notes_id: int):
    user = get_loggin(request)
    if not user:
        return RedirectResponse("/login")
    
    db.table("notes").delete().eq("id", notes_id).eq("user_id", user.id).execute()
    return RedirectResponse("/dashboard#notes", status_code=303)

# ----------------- UPDATE: Edit notes -----------------

@router.get("/editnotes/{notes_id}")
async def edit_notes_form(request: Request, notes_id: int):
    user = get_loggin(request)
    if not user:
        return RedirectResponse("/login")

    notes = db.table("notes").select("*").eq("id", notes_id).eq("user_id", user.id).execute()
    if not notes.data:
        return RedirectResponse("/dashboard#notes")
    return templates.TemplateResponse("edit_notes.html", {"request": request, "notes": notes.data[0]})


@router.post("/editnotes")
async def update_notes(request: Request, id: int = Form(...), title: str = Form(...), info: str = Form(...)):
    user = get_loggin(request)
    if not user:
        return RedirectResponse("/login")

    db.table("notes").update({
        "title": title,
        "info": info
    }).eq("id", id).eq("user_id", user.id).execute()

    return RedirectResponse("/dashboard#notes", status_code=303)







#------------FILES: UPLOAD-----------------

@router.get('/uploadfiles')
async def notes(request: Request):
    user = get_loggin(request)
    if not user:
        return RedirectResponse("/login")
    
    bucket_name = "files"
    db.storage.from_(bucket_name).list()
    return RedirectResponse("/dashboard#files", status_code=303)




@router.post("/uploadfiles")
async def upload_file(request: Request, files: List[UploadFile] = File(...)):
    user = get_loggin(request)
    if not user:
        return RedirectResponse("/login")
    
    bucket_name = "files"
    for file in files:
        if file.size > 10 * 1024 * 1024:
            continue
        file_bytes = await file.read()
        db.storage.from_(bucket_name).upload(
            file=file_bytes,
            path=file.filename,
            file_options={"content-type": file.content_type}
        )
    return RedirectResponse("/uploadfiles", status_code=303)


@router.get("/download/{filename}")
async def download_file(request: Request, filename: str):
    user = get_loggin(request)
    if not user:
        return RedirectResponse("/login")
    bucket_name = "files"
    file_data = db.storage.from_(bucket_name).download(filename)
    return StreamingResponse(
        BytesIO(file_data),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/delete/{filename}")
async def delete_file(request: Request, filename: str):
    user = get_loggin(request)
    if not user:
        return RedirectResponse("/login")
    bucket_name = "files"
    db.storage.from_(bucket_name).remove([filename])
    return RedirectResponse("/dashboard#files", status_code=303)







# -------------------photos---------------------

@router.get('/upload_img')
async def get_images(request: Request):
    user = get_loggin(request)
    if not user:
        return RedirectResponse("/login")

    bucket_name = "images"
    photos = db.storage.from_(bucket_name).list()

    # Generate signed URLs valid for 1 hour
    for photo in photos:
        signed = db.storage.from_(bucket_name).create_signed_url(photo["name"], 3600)
        photo["url"] = signed["signedURL"]

    return RedirectResponse("/dashboard#images", status_code=303)


@router.post("/upload_img")
async def upload_file(request: Request, photos: List[UploadFile] = File(...)):
    user = get_loggin(request)
    if not user:
        return RedirectResponse("/login")
    
    bucket_name = "images"
    for p in photos:
        file_bytes = await p.read()
        db.storage.from_(bucket_name).upload(
            file=file_bytes,
            path=p.filename,    
            file_options={"content-type": p.content_type} 
        )
    return RedirectResponse("/upload_img", status_code=303) 

@router.post("/delete_img/{filename}")
async def delete_img(request: Request, filename: str):
    user = get_loggin(request)
    if not user:
        return RedirectResponse("/login")
    bucket_name = "images"
    db.storage.from_(bucket_name).remove([filename])
    return RedirectResponse("/dashboard#images", status_code=303)

@router.get("/download_img/{filename}")
async def download_img(request: Request, filename: str):
    user = get_loggin(request)
    if not user:
        return RedirectResponse("/login")
    bucket_name = "images"
    file_data = db.storage.from_(bucket_name).download(filename)
    return StreamingResponse(
        BytesIO(file_data),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )