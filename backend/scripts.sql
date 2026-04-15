CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 1. USER TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS "user" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_id INTEGER NOT NULL CHECK (role_id IN (1, 2, 3, 4)),
    -- 1: Seller, 2: Buyer, 3: Admin, 4: Data Scientist
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    gender VARCHAR(50),
    age INTEGER CHECK (age > 0 AND age < 150),
    created_at TIMESTAMP DEFAULT timezone('Asia/Ho_Chi_Minh', now()),
    updated_at TIMESTAMP NOT NULL DEFAULT timezone('Asia/Ho_Chi_Minh', now())
);

CREATE INDEX idx_user_email ON "user"(email);
CREATE INDEX idx_user_role_id ON "user"(role_id);
CREATE INDEX idx_user_username ON "user"(username);

-- ============================================================
-- 2. PRODUCT TABLE
-- ===========================================================
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_name VARCHAR(255) NOT NULL,
    product_display_name VARCHAR(500) NOT NULL,
    
    -- Các trường phục vụ AI
    image_url VARCHAR(500),
    description TEXT,
    style_note TEXT,
    occasion VARCHAR(255),
    cross_links VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,

    -- Metadata phân loại
    gender VARCHAR(50),
    master_category VARCHAR(100),
    sub_category VARCHAR(100),
    article_type VARCHAR(100),
    base_colour VARCHAR(100),
    season VARCHAR(100),
    usage VARCHAR(100),
    
    -- Dữ liệu số
    price FLOAT NOT NULL,
    discounted_price FLOAT,
    myntra_rating FLOAT,
    fabric VARCHAR(255),
    fit VARCHAR(100),
    neck VARCHAR(100),
    
    -- Hệ thống (Tự động set theo múi giờ VN)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('Asia/Ho_Chi_Minh', now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('Asia/Ho_Chi_Minh', now())
);

CREATE INDEX idx_product_brand_name ON product(brand_name);
CREATE INDEX idx_product_season ON product(season);
CREATE INDEX idx_product_gender ON product(gender);
CREATE INDEX idx_product_base_colour ON product(base_colour);
CREATE INDEX idx_product_fashion_type ON product(fashion_type);
CREATE INDEX idx_product_price ON product(price);

-- ============================================================
-- 3. ORDER TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS "order" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    order_date TIMESTAMP NOT NULL DEFAULT timezone('Asia/Ho_Chi_Minh', now()),
    status INTEGER NOT NULL DEFAULT 0 CHECK (status IN (0, 1, 2, 3)),
    -- 0: chờ thanh toán, 1: đang giao, 2: hoàn thành, 3: đã hủy
    total_amount INTEGER NOT NULL CHECK (total_amount > 0),
    note TEXT,
    updated_at TIMESTAMP NOT NULL DEFAULT timezone('Asia/Ho_Chi_Minh', now()),
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

CREATE INDEX idx_order_user_id ON "order"(user_id);
CREATE INDEX idx_order_status ON "order"(status);
CREATE INDEX idx_order_order_date ON "order"(order_date DESC);

-- ============================================================
-- 4. ORDER_ITEM TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS order_item (
    id SERIAL PRIMARY KEY,
    order_id UUID NOT NULL,
    product_id UUID NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price INTEGER NOT NULL CHECK (unit_price > 0),
    subtotal INTEGER NOT NULL CHECK (subtotal > 0),
    created_at TIMESTAMP DEFAULT timezone('Asia/Ho_Chi_Minh', now()),
    updated_at TIMESTAMP NOT NULL DEFAULT timezone('Asia/Ho_Chi_Minh', now()),
    FOREIGN KEY (order_id) REFERENCES "order"(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE RESTRICT,
    UNIQUE(order_id, product_id)
);

CREATE INDEX idx_order_item_order_id ON order_item(order_id);
CREATE INDEX idx_order_item_product_id ON order_item(product_id);

-- ============================================================
-- 5. WISHLIST TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS wishlist (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    product_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT timezone('Asia/Ho_Chi_Minh', now()),
    updated_at TIMESTAMP NOT NULL DEFAULT timezone('Asia/Ho_Chi_Minh', now()),
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE,
    UNIQUE(user_id, product_id)
);

CREATE INDEX idx_wishlist_user_id ON wishlist(user_id);
CREATE INDEX idx_wishlist_product_id ON wishlist(product_id);

-- ============================================================
-- 6. CART TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS cart (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    product_id UUID NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    unit_price INTEGER NOT NULL CHECK (unit_price > 0),
    total_price INTEGER NOT NULL CHECK (total_price > 0),
    created_at TIMESTAMP DEFAULT timezone('Asia/Ho_Chi_Minh', now()),
    updated_at TIMESTAMP NOT NULL DEFAULT timezone('Asia/Ho_Chi_Minh', now()),
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE,
    UNIQUE(user_id, product_id)
);

CREATE INDEX idx_cart_user_id ON cart(user_id);
CREATE INDEX idx_cart_product_id ON cart(product_id);

-- ============================================================
-- TRIGGER: Update updated_at timestamp (HCMC Timezone)
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('Asia/Ho_Chi_Minh', now());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for tables
CREATE TRIGGER update_user_updated_at BEFORE UPDATE ON "user" FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_product_updated_at BEFORE UPDATE ON product FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_order_updated_at BEFORE UPDATE ON "order" FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_order_item_updated_at BEFORE UPDATE ON order_item FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_wishlist_updated_at BEFORE UPDATE ON wishlist FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_cart_updated_at BEFORE UPDATE ON cart FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================
CREATE INDEX idx_order_user_date ON "order"(user_id, order_date DESC);
CREATE INDEX idx_wishlist_user_created ON wishlist(user_id, created_at DESC);
CREATE INDEX idx_cart_user_created ON cart(user_id, created_at DESC);
CREATE INDEX idx_product_brand_season ON product(brand_name, season);