from fastapi import FastAPI
from database import Base, engine
from routes import auth, cart, orders, products, users

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mini Shop API")
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
