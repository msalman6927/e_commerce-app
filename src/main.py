from fastapi import FastAPI
from src.routes import auth_routes,order_routes,admin_routes,product_routes,category_routes, cart_routes
from src.models.user_model import Users
from src.models.category_model import Categories
from src.models.product_model import Products
from src.models.order_model import Orders
from src.models.order_item_model import OrderItems
from src.models.cart_model import CartItems

app = FastAPI(
    title="E-Commerce Store API",
    description="A production-grade secure E-Commerce backend API",
    version="1.0.0"
)

# Saare routers register karein
app.include_router(auth_routes.router)
app.include_router(category_routes.router)
app.include_router(product_routes.router)
app.include_router(cart_routes.router)
app.include_router(order_routes.router)
app.include_router(admin_routes.router)
# Admin routes ko bhi register karein

@app.get("/", tags=["Root"])
def root():
    return {"message": "E-Commerce Store API is running smoothly!"} 