from fastapi import FastAPI
from routes import auth_routes, product_routes  
# from models.user_model import Users
# from models.category_model import Categories
# from models.product_model import Products
# from models.order_model import Orders
# from models.order_item_model import OrderItems
app = FastAPI(
    title="E-Commerce Store API",
    description="A production-grade secure E-Commerce backend API",
    version="1.0.0"
)

# Saare routers register karein
app.include_router(auth_routes.router)
app.include_router(product_routes.router)  # Store router link ho gaya

@app.get("/", tags=["Root"])
def root():
    return {"message": "E-Commerce Store API is running smoothly!"}