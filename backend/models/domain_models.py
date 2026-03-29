import uuid
from sqlalchemy import (
    Column, Integer, String, Boolean, Float, 
    TIMESTAMP, Text, ForeignKey, func, Numeric, BigInteger
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "user"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = Column(Integer, nullable=False) # 1: Seller, 2: Buyer, 3: Admin, 4: Data Scientist
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    gender = Column(String(50), nullable=True)
    age = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    wishlist_items = relationship("Wishlist", back_populates="user", cascade="all, delete-orphan")
    cart_items = relationship("Cart", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(username={self.username!r}, id={self.id})>"

class Product(Base):
    __tablename__ = "product"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    price = Column(Integer, nullable=False)
    discounted_price = Column(Integer, nullable=True)
    style_type = Column(String(255), nullable=True)
    product_type_id = Column(Integer, nullable=True)
    article_number = Column(String(255), unique=True, nullable=True)
    visual_tag = Column(String(255), nullable=True)
    product_display_name = Column(String(500), nullable=False)
    myntra_rating = Column(Integer, nullable=True)
    variant_name = Column(String(255), nullable=True)
    gender = Column(String(50), nullable=True)
    age_group = Column(String(100), nullable=True)
    brand_name = Column(String(255), nullable=False)
    catalog_add_date = Column(BigInteger, nullable=True)
    base_colour = Column(String(100), nullable=True)
    colour1 = Column(String(100), nullable=True)
    colour2 = Column(String(100), nullable=True)
    fashion_type = Column(String(255), nullable=True)
    season = Column(String(100), nullable=True)
    year = Column(String(50), nullable=True)
    usage = Column(String(100), nullable=True)
    vat = Column(Numeric(5, 2), default=0, nullable=False)
    display_categories = Column(String(500), nullable=True)
    weight = Column(String(100), nullable=True)
    navigation_id = Column(String(255), nullable=True)
    landing_page_url = Column(String(500), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    order_items = relationship("OrderItem", back_populates="product", cascade="all, delete-orphan")
    wishlisted_by = relationship("Wishlist", back_populates="product", cascade="all, delete-orphan")
    in_carts = relationship("Cart", back_populates="product", cascade="all, delete-orphan")

class Order(Base):
    __tablename__ = "order"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    order_date = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    status = Column(Integer, default=0, nullable=False) # 0: chờ thanh toán, 1: đang giao, 2: hoàn thành, 3: đã hủy
    total_amount = Column(Integer, nullable=False)
    note = Column(Text, nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_item"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(PG_UUID(as_uuid=True), ForeignKey('order.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey('product.id', ondelete='RESTRICT'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Integer, nullable=False)
    subtotal = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

class Wishlist(Base):
    __tablename__ = "wishlist"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="wishlist_items")
    product = relationship("Product", back_populates="wishlisted_by")

class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Integer, nullable=False)
    total_price = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="in_carts")