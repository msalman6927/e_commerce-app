from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.config.database import get_db
from src.models.product_model import Products
from src.models.order_model import Orders
from src.models.order_item_model import OrderItems
from src.models.cart_model import CartItems
from src.utils.dependencies import get_current_user, check_admin_role
from src.models.user_model import Users
from src.schemas.order_schema import OrderResponse

router = APIRouter(prefix="/orders", tags=["Orders & Checkout"])

# 1. CUSTOMER ROUTE: Checkout (Cart se automatic order generate karna)
@router.post("/checkout", status_code=status.HTTP_201_CREATED)
def checkout_from_cart(
    db: Session = Depends(get_db), 
    current_user: Users = Depends(get_current_user)
):
    """
    User ki active cart se items fetch kar ke order banata hai,
    stock deduct karta hai aur cart ko empty kar deta hai.
    """
    try:
        # 1. User ki cart items database se nikalhein
        cart_items = db.query(CartItems).filter(CartItems.user_id == current_user.id).all()
        if not cart_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Aap ki shopping cart khali hai!"
            )
            
        # 2. Parent Order create karein (Initial price 0)
        new_order = Orders(
            user_id=current_user.id, 
            total_price=0, 
            status="pending"  # Default status matching your comment
        )
        db.add(new_order)
        db.flush()  # Is se new_order.id memory me generate ho jayegi
        
        calculated_total = 0
        
        # 3. Cart ke items ko process karein aur stock check/deduct karein
        for cart_item in cart_items:
            # Row locking (.with_for_update()) taake double-selling na ho सके (Isolation)
            product = db.query(Products).filter(Products.id == cart_item.product_id).with_for_update().first()
            
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail=f"Product ID {cart_item.product_id} ab store me nahi hai!"
                )
                
            if product.stock < cart_item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"Stock limit exceeded for '{product.name}'! Available: {product.stock}"
                )
                
            # Stock minus karein
            product.stock -= cart_item.quantity
            
            # price_at_purchase integer hai, so hum price ko integer me map karenge
            current_price = int(product.price)
            item_total = current_price * cart_item.quantity
            calculated_total += item_total
            
            # Detail Item record create karein aapke 'price_at_purchase' variable ke sath
            order_item = OrderItems(
                order_id=new_order.id,
                product_id=product.id,
                quantity=cart_item.quantity,
                price_at_purchase=current_price  # <-- Matches your model column
            )
            db.add(order_item)
            
        # Parent order ka final total set karein
        new_order.total_price = calculated_total
        
        # 4. Cart khali kar dein
        db.query(CartItems).filter(CartItems.user_id == current_user.id).delete()
        
        # TRANSACTION COMPLETE (Commit everything!)
        db.commit()
        
        return {
            "message": "Order successfully placed!",
            "order_id": new_order.id,
            "total_price": calculated_total,
            "status": new_order.status
        }
        
    except Exception as e:
        db.rollback()  # Kuch bhi fail hua toh auto-rollback (Atomicity)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Checkout failed: {str(e)}"
        )


# 2. ADMIN ROUTE: View all orders across the store
@router.get("/", response_model=List[OrderResponse])
def get_all_orders(
    db: Session = Depends(get_db), 
    current_admin: Users = Depends(check_admin_role)
):
    """Admin Only: Pure store ke orders ki list fetch karein."""
    return db.query(Orders).all()


# 3. ADMIN ROUTE: Update order delivery status (pending, completed, cancelled)
@router.put("/{order_id}/status")
def update_order_status(
    order_id: int, 
    new_status: str,  # e.g., "completed" or "cancelled"
    db: Session = Depends(get_db),
    current_admin: Users = Depends(check_admin_role)
):
    """Admin Only: Order ka status change karein."""
    order = db.query(Orders).filter(Orders.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order nahi mila!")
        
    # Matches your model's comment: pending, completed, cancelled
    allowed_statuses = ["pending", "completed", "cancelled"]
    if new_status.lower() not in allowed_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status! Only {allowed_statuses} are allowed."
        )
        
    order.status = new_status.lower()
    db.commit()
    return {"message": f"Order {order_id} status updated to '{order.status}' successfully!"}