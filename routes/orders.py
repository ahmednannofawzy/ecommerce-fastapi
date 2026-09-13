from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
import models, schemas, auth

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/checkout", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
def checkout(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_price = 0
    order_items_to_create = []

    # التحقق من الـ stock وحساب السعر الإجمالي
    for cart_item in cart_items:
        product = cart_item.product
        if product.stock < cart_item.quantity:
            raise HTTPException(status_code=400, detail=f"Product {product.name} out of stock")

        total_price += product.price * cart_item.quantity
        
        # خصم الكمية المشتراة من المخزون
        product.stock -= cart_item.quantity

        order_items_to_create.append(
            models.OrderItem(
                product_id=product.id,
                price=product.price,
                quantity=cart_item.quantity
            )
        )

    # إنشاء الطلب الرئيسي
    new_order = models.Order(user_id=current_user.id, total_price=total_price)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # إضافة المنتجات داخل الطلب
    for order_item in order_items_to_create:
        order_item.order_id = new_order.id
        db.add(order_item)

    # تفريغ السلة بعد نجاح الطلب
    db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).delete(synchronize_session=False)
    db.commit()
    db.refresh(new_order)

    return new_order

@router.get("/", response_model=List[schemas.OrderResponse])
def get_user_orders(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Order).filter(models.Order.user_id == current_user.id).all()