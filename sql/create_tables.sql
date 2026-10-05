CREATE TABLE IF NOT EXISTS canonical_customers (
    id BIGSERIAL PRIMARY KEY,
    customer_id TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth DATE,
    phone TEXT,
    email TEXT,
    address TEXT,
    city TEXT,
    state_province TEXT,
    postal_code TEXT,
    country TEXT,
    source_system TEXT NOT NULL,
    migrated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_canonical_customers_customer_id
    ON canonical_customers (customer_id);

CREATE INDEX IF NOT EXISTS idx_canonical_customers_email
    ON canonical_customers (email);

CREATE INDEX IF NOT EXISTS idx_canonical_customers_phone
    ON canonical_customers (phone);
