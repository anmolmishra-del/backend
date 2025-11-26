from fastapi import FastAPI
from sqladmin import Admin
from app.modules.admin.views.locations import locationAdmin
from app.modules.admin.views.users import UserAdmin
from app.modules.auth import router as auth_router
from app.modules.admin import router as admin_router


from app.modules.food_delivery import food_delivery
from app.modules.locations import router as locations_router
from app.core.database import engine


app = FastAPI(title="User Management API", version="1.0.0")


@app.get("/")
def root():
    return {"status": "ok", "message": "API is running"}
admin = Admin(app=app, engine=engine, title="User Admin Panel", base_url="/admin")
admin.add_view(UserAdmin)
admin.add_view(locationAdmin)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(locations_router)

app.include_router(food_delivery.router)


@app.on_event("startup")
async def on_startup():
    try:
        from app.core.database import init_models
        init_models()
        print(" Database tables initialized")
    except Exception as e:
        print(f" Could not initialize database: {e}")
