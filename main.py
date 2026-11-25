from fastapi import FastAPI
from database import Base, engine
from routes import router, users_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mini Shop API")
app.include_router(router)
app.include_router(users_router)
