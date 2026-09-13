from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
import models, schemas, auth

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.get("/", response_model=List[schemas.CartItemResponse])
def get_cart_items(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).all()

@router.post("/", response_model=schemas.CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(item: schemas.CartItemCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.stock < item.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock available")

    existing_item = db.query(models.CartItem).filter(
        models.CartItem.user_id == current_user.id,
        models.CartItem.product_id == item.product_id
    ).first()

    if existing_item:
        existing_item.quantity += item.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item

    new_cart_item = models.CartItem(user_id=current_user.id, product_id=item.product_id, quantity=item.quantity)
    db.add(new_cart_item)
    db.commit()
    db.refresh(new_cart_item)
    return new_cart_item

@router.delete("/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_cart(cart_item_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    cart_item = db.query(models.CartItem).filter(models.CartItem.id == cart_item_id, models.CartItem.user_id == current_user.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(cart_item)
    db.commit()
    return