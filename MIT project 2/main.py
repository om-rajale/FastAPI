from fastapi import FastAPI
from auth import create_token, get_current_user, hash_password, verify_password
from models import LoginUser, Register, CategoryCreate, TaskCreate, Taskupdate
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from fastapi import Depends
from database import supabase

app = FastAPI()

@app.get("/")
def home():
    return {
        "message": "Welcome"
    }


@app.post("/register")
@app.post("/Register")
def register(user: Register):
    existing_user = supabase.table("users").select("*").eq("email", user.email).execute()
    if existing_user.data:
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed = hash_password(user.password)
    new_user = supabase.table("users").insert({
        "email": user.email,
        "password": hashed,
        "name": user.name
    }).execute()

    return {
        "message": "user registered successfully",
        "user_id": new_user.data[0]
    }

@app.post("/login")
def login(user: LoginUser):
    res = supabase.table("users").select("*").eq("email", user.email).execute()

    if not res.data:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    db_user = res.data[0]
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token({"user_id": db_user["id"]})
    return {
        "message":"Login Successful",
        "token": token
    }


@app.post("/categories")
def create_category(category: CategoryCreate, user_id: str = Depends(get_current_user)):
    new_category = supabase.table("categories").insert({
        "name": category.name,
        "user_id": user_id
    }).execute()

    return {
        "message": "Category created successfully",
        "category_id": new_category.data[0]
    }


@app.get("/get_categories")
def get_categories(user_id: str = Depends(get_current_user)):
    categories = supabase.table("categories").select("*").eq("user_id", user_id).execute()
    return {
        "categories": categories.data
    }

@app.post("/tasks")
def create_task(task: TaskCreate, user_id: str = Depends(get_current_user)):
    res = supabase.table("tasks").insert({
        "title": task.title,
        "description": task.description,
        "category_id": task.category_id,
        "user_id": user_id
    }).execute()
    
    return {
        "message": "Task created successfully",
        "task_id": res.data[0]
    }
        
@app.get("/get_tasks")
def get_tasks(user_id: str = Depends(get_current_user)):
    tasks = supabase.table("tasks").select("*").eq("user_id", user_id).execute()
    return {
        "tasks": tasks.data
    }

@app.get("/get_tasks/{task_id}")
def get_task(task_id: str, user_id: str = Depends(get_current_user)):
    task = supabase.table("tasks").select("*").eq("id", task_id).eq("user_id", user_id).execute()
    if not task.data:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.data[0]