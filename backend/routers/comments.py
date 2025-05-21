from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..models import Review, Product
from ..config import get_db
from pydantic import BaseModel, Field
import uuid

router = APIRouter()

class ReviewCreate(BaseModel):
    product_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., min_length=1, max_length=1000)

class ReviewResponse(BaseModel):
    id: str
    product_id: str
    user_id: str
    rating: int
    comment: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=ReviewResponse)
async def create_review(
    review: ReviewCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new review for a product
    """
    try:
        # Verify product exists
        product = db.query(Product).filter(Product.id == review.product_id).first()
        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        # Create review instance
        db_review = Review(
            id=str(uuid.uuid4()),
            product_id=review.product_id,
            user_id="temp_user",  # Replace with actual user ID from auth
            rating=review.rating,
            comment=review.comment
        )

        # Save to database
        db.add(db_review)
        db.commit()
        db.refresh(db_review)

        return db_review

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating review: {str(e)}"
        )

@router.get("/product/{product_id}", response_model=List[ReviewResponse])
async def list_product_reviews(
    product_id: str,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    List all reviews for a specific product
    """
    # Verify product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    reviews = db.query(Review)\
        .filter(Review.product_id == product_id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return reviews

@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific review by ID
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )
    return review

@router.delete("/{review_id}")
async def delete_review(
    review_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a review (owner or admin only)
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    # TODO: Add authorization check here
    # Only allow review owner or admin to delete

    db.delete(review)
    db.commit()
    return {"message": "Review deleted successfully"}
