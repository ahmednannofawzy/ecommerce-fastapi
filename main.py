import uvicorn
from fastapi import FastAPI
from database import engine, Base
from routes import auth as auth_router, products as products_router, cart as cart_router, orders as orders_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Simple E-commerce API", version="1.0.0")

app.include_router(auth_router.router)
app.include_router(products_router.router)
app.include_router(cart_router.router)
app.include_router(orders_router.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)