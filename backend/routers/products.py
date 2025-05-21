from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import datetime
from ..models import Product, User
from ..config import get_db, UPLOAD_DIR
from ..utils.encryption import encrypt_data, decrypt_data
from ..services.ai_classifier import classifier
from pydantic import BaseModel, Field
import shutil
import uuid

router = APIRouter()

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10)
    price: float = Field(..., gt=0)
    category: Optional[str] = None

class ProductResponse(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: Optional[str]
    image_path: Optional[str]
    commission: float
    seller_id: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=ProductResponse)
async def create_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Create a new product listing with optional image upload
    """
    try:
        # AI Classification and safety check
        classification = classifier.classify_product(description)
        if not classification["is_safe"]:
            raise HTTPException(
                status_code=400,
                detail="Content flagged as potentially unsafe"
            )

        # Calculate commission (2.5%)
        commission = price * 0.025

        # Create product instance
        product = Product(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            price=price,
            category=classification["category"],
            commission=commission,
            seller_id="temp_seller"  # Replace with actual seller ID from auth
        )

        # Handle image upload if provided
        if image:
            # Generate unique filename
            file_ext = os.path.splitext(image.filename)[1]
            file_name = f"{product.id}{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, file_name)

            # Read and encrypt image data
            image_data = await image.read()
            encrypted_data = encrypt_data(image_data)

            # Save encrypted image
            with open(file_path, "wb") as f:
                f.write(encrypted_data)

            product.image_path = file_name

        # Save to database
        db.add(product)
        db.commit()
        db.refresh(product)

        return product

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating product: {str(e)}"
        )

@router.get("/", response_model=List[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    List all products with pagination
    """
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific product by ID
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a product (seller only)
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Delete associated image if exists
    if product.image_path:
        file_path = os.path.join(UPLOAD_DIR, product.image_path)
        if os.path.exists(file_path):
            os.remove(file_path)

    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}
