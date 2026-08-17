from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from models.cart_model import CartItems
from models.product_model import Products
from schemas.cart_schema import CartItemAdd, CartItemUpdate, CartResponse, CartItemResponse
from utils.dependencies import get_current_user
from models.user_model import Users

router = APIRouter(prefix="/cart", tags=["Shopping Cart"])

@router.get("/", response_model=CartResponse)
def get_my_cart(db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    """User cart details with dynamic calculated items and grand totals."""
    cart_items = db.query(CartItems).filter(CartItems.user_id == current_user.id).all()
    
    response_items = []
    grand_total = 0.0
    
    for item in cart_items:
        total_item_price = item.product.price * item.quantity
        grand_total += total_item_price
        
        response_items.append(
            CartItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product.name,
                price_per_unit=item.product.price,
                quantity=item.quantity,
                total_price=total_item_price
            )
        )
        
    return CartResponse(items=response_items, grand_total=grand_total)

@router.post("/add", status_code=status.HTTP_201_CREATED)
def add_item_to_cart(
    item_data: CartItemAdd,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Add item to cart. If already exists, increase the quantity after verifying stock limit."""
    # Validate product and stock
    product = db.query(Products).filter(Products.id == item_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product nahi mila!")
        
    if product.stock < item_data.quantity:
        raise HTTPException(status_code=400, detail=f"Stock se zyada select nahi kar sakte! Sirf {product.stock} items available hain.")
        
    # Check existing cart item
    existing_item = db.query(CartItems).filter(
        CartItems.user_id == current_user.id,
        CartItems.product_id == item_data.product_id
    ).first()
    
    if existing_item:
        new_qty = existing_item.quantity + item_data.quantity
        if product.stock < new_qty:
            raise HTTPException(status_code=400, detail="Stock limit exceeded with existing cart items!")
        existing_item.quantity = new_qty
    else:
        new_cart_item = CartItems(
            user_id=current_user.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity
        )
        db.add(new_cart_item)
        
    db.commit()
    return {"message": f"'{product.name}' cart mein add ho gaya hai."}

@router.put("/update/{item_id}")
def update_cart_quantity(
    item_id: int,
    update_data: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Modify cart item quantity with validation checks on current inventory stock."""
    cart_item = db.query(CartItems).filter(
        CartItems.id == item_id,
        CartItems.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item cart mein nahi mila!")
        
    if cart_item.product.stock < update_data.quantity:
        raise HTTPException(status_code=400, detail="Humare pass stock mein is se kam items hain!")
        
    cart_item.quantity = update_data.quantity
    db.commit()
    return {"message": "Cart quantity updated!"}

@router.delete("/remove/{item_id}")
def remove_from_cart(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Permanently delete an item from the user's cart."""
    cart_item = db.query(CartItems).filter(
        CartItems.id == item_id,
        CartItems.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item cart mein nahi mila!")
        
    db.delete(cart_item)
    db.commit()
    return {"message": "Item cart se successfully remove kar diya gaya hai."}