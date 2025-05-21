from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    pgp_key = Column(Text, nullable=False, unique=True)
    is_seller = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    products = relationship("Product", back_populates="seller")
    reviews = relationship("Review", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, is_seller={self.is_seller})>"

class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String)
    image_path = Column(String)
    commission = Column(Float)
    seller_id = Column(String, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    seller = relationship("User", back_populates="products")
    reviews = relationship("Review", back_populates="product")

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, price={self.price})>"

class Review(Base):
    __tablename__ = "reviews"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id'))
    product_id = Column(String, ForeignKey('products.id'))
    rating = Column(Integer)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")

    def __repr__(self):
        return f"<Review(id={self.id}, rating={self.rating})>"
