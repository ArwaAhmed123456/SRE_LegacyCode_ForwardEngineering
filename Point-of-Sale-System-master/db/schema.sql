-- SQLite schema for Point of Sale System

PRAGMA foreign_keys = ON;

-- Employees
CREATE TABLE IF NOT EXISTS employees (
  employee_id TEXT PRIMARY KEY,
  role TEXT NOT NULL,
  first_name TEXT,
  last_name TEXT,
  password TEXT
);

-- Items (for sale)
CREATE TABLE IF NOT EXISTS items (
  item_id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  price REAL NOT NULL,
  quantity INTEGER NOT NULL
);

-- Rental items (kept separate for clarity)
CREATE TABLE IF NOT EXISTS rentals (
  rental_id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  price REAL NOT NULL,
  quantity INTEGER NOT NULL
);

-- Customers / Users (by phone number in original files)
CREATE TABLE IF NOT EXISTS customers (
  phone TEXT PRIMARY KEY
);

-- User rentals (one row per rented item instance)
CREATE TABLE IF NOT EXISTS user_rentals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_phone TEXT NOT NULL REFERENCES customers(phone) ON DELETE CASCADE,
  item_id INTEGER NOT NULL,
  rented_date TEXT,
  returned INTEGER NOT NULL DEFAULT 0
);

-- Coupons
CREATE TABLE IF NOT EXISTS coupons (
  code TEXT PRIMARY KEY,
  used INTEGER NOT NULL DEFAULT 0
);

-- Sales invoices (header)
CREATE TABLE IF NOT EXISTS invoices (
  invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  total_with_tax REAL
);

-- Invoice line items
CREATE TABLE IF NOT EXISTS invoice_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  invoice_id INTEGER NOT NULL REFERENCES invoices(invoice_id) ON DELETE CASCADE,
  item_id INTEGER,
  item_name TEXT,
  quantity INTEGER,
  price REAL
);

-- Optional: a simple metadata table to track imports / versions
CREATE TABLE IF NOT EXISTS metadata (
  key TEXT PRIMARY KEY,
  value TEXT
);
