#!/usr/bin/env python3
"""
Simple migration script to import existing text files in `Database/` into an SQLite database `pos.db`.
Run from the project root (where `Database/` and `db/schema.sql` live):

    python db/migrate.py

This script is idempotent for the basic imports (it creates tables if not present).
"""
import sqlite3
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parent.parent
DB_DIR = ROOT / 'db'
DATA_DIR = ROOT / 'Database'
DB_PATH = DB_DIR / 'pos.db'

SQL_SCHEMA = DB_DIR / 'schema.sql'

conn = sqlite3.connect(str(DB_PATH))
conn.execute('PRAGMA foreign_keys = ON;')
cur = conn.cursor()

# Create schema
with open(SQL_SCHEMA, 'r', encoding='utf-8') as f:
    schema_sql = f.read()
cur.executescript(schema_sql)
conn.commit()

# Import employees
emp_file = DATA_DIR / 'employeeDatabase.txt'
if emp_file.exists():
    with emp_file.open('r', encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            parts = line.split()  # id role first last password
            if len(parts) >= 5:
                emp_id, role, first, last, password = parts[:5]
            elif len(parts) == 4:
                emp_id, role, first, last = parts
                password = None
            else:
                continue
            cur.execute('INSERT OR REPLACE INTO employees(employee_id, role, first_name, last_name, password) VALUES(?,?,?,?,?)',
                        (emp_id, role, first, last, password))
    conn.commit()

# Import items
item_file = DATA_DIR / 'itemDatabase.txt'
if item_file.exists():
    with item_file.open('r', encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 4:
                item_id = int(parts[0])
                name = parts[1]
                price = float(parts[2])
                qty = int(parts[3])
                cur.execute('INSERT OR REPLACE INTO items(item_id, name, price, quantity) VALUES(?,?,?,?)',
                            (item_id, name, price, qty))
    conn.commit()

# Import rentals
rental_file = DATA_DIR / 'rentalDatabase.txt'
if rental_file.exists():
    with rental_file.open('r', encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 4:
                rid = int(parts[0])
                name = parts[1]
                price = float(parts[2])
                qty = int(parts[3])
                cur.execute('INSERT OR REPLACE INTO rentals(rental_id, name, price, quantity) VALUES(?,?,?,?)',
                            (rid, name, price, qty))
    conn.commit()

# Import coupons
coupon_file = DATA_DIR / 'couponNumber.txt'
if coupon_file.exists():
    with coupon_file.open('r', encoding='utf-8') as f:
        for line in f:
            code = line.strip()
            if code:
                cur.execute('INSERT OR IGNORE INTO coupons(code, used) VALUES(?,0)', (code,))
    conn.commit()

# Import customers and user rentals
user_file = DATA_DIR / 'userDatabase.txt'
if user_file.exists():
    with user_file.open('r', encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            parts = line.split()
            phone = parts[0]
            cur.execute('INSERT OR IGNORE INTO customers(phone) VALUES(?)', (phone,))
            rentals = parts[1:]
            for r in rentals:
                # format: itemID,MM/DD/YY,boolean
                try:
                    item_id, date_str, returned_str = r.split(',')
                    returned = 1 if returned_str.lower() in ('true','1','yes') else 0
                    cur.execute('INSERT INTO user_rentals(customer_phone, item_id, rented_date, returned) VALUES(?,?,?,?)',
                                (phone, int(item_id), date_str, returned))
                except Exception:
                    continue
    conn.commit()

# Import saleInvoiceRecord: this is looser, we'll create invoices separated by timestamp lines
sale_file = DATA_DIR / 'saleInvoiceRecord.txt'
if sale_file.exists():
    with sale_file.open('r', encoding='utf-8') as f:
        lines = [l.rstrip() for l in f]
    i = 0
    current_invoice_id = None
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        # detect timestamp-like line: YYYY- or starts with digits and '-'
        if (len(line) >= 4 and line[0].isdigit() and ('-' in line or ':' in line)):
            created_at = line
            cur.execute('INSERT INTO invoices(created_at, total_with_tax) VALUES(?,NULL)', (created_at,))
            current_invoice_id = cur.lastrowid
            i += 1
            # read following item lines until Total with tax
            while i < len(lines) and not lines[i].startswith('Total with tax') and lines[i].strip():
                parts = lines[i].split()
                # expecting: id name qty price
                if len(parts) >= 4:
                    item_id = parts[0]
                    item_name = parts[1]
                    qty = int(parts[2])
                    price = float(parts[3])
                    cur.execute('INSERT INTO invoice_items(invoice_id, item_id, item_name, quantity, price) VALUES(?,?,?,?,?)',
                                (current_invoice_id, int(item_id) if item_id.isdigit() else None, item_name, qty, price))
                i += 1
            # read Total with tax if present
            if i < len(lines) and lines[i].startswith('Total with tax'):
                try:
                    total = float(lines[i].split(':',1)[1].strip())
                    cur.execute('UPDATE invoices SET total_with_tax=? WHERE invoice_id=?', (total, current_invoice_id))
                except Exception:
                    pass
        else:
            i += 1
    conn.commit()

print('Migration complete. DB created at', DB_PATH)
conn.close()
