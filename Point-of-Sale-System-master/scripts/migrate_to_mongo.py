#!/usr/bin/env python3
"""
Migrate legacy `Database/*.txt` files into MongoDB collections.
Run from project root:

    python scripts/migrate_to_mongo.py --mongo-uri mongodb://localhost:27017/posdb

Requires: pymongo
"""
import argparse
from pathlib import Path
from pymongo import MongoClient
import sys

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'Database'

parser = argparse.ArgumentParser()
parser.add_argument('--mongo-uri', default='mongodb://localhost:27017/posdb')
args = parser.parse_args()

client = MongoClient(args.mongo_uri)
db = client.get_default_database()

# Employees
emp_file = DATA_DIR / 'employeeDatabase.txt'
if emp_file.exists():
    with emp_file.open('r', encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line: continue
            parts = line.split()
            if len(parts) >= 5:
                emp_id, role, first, last, password = parts[:5]
            elif len(parts) == 4:
                emp_id, role, first, last = parts
                password = None
            else:
                continue
            db.employees.update_one({'employee_id': emp_id}, {'$set': {
                'employee_id': emp_id, 'role': role, 'first_name': first, 'last_name': last, 'password': password
            }}, upsert=True)

# Items
item_file = DATA_DIR / 'itemDatabase.txt'
if item_file.exists():
    with item_file.open('r', encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line: continue
            parts = line.split()
            if len(parts) >= 4:
                item_id = int(parts[0])
                name = parts[1]
                price = float(parts[2])
                qty = int(parts[3])
                db.items.update_one({'item_id': item_id}, {'$set': {'item_id': item_id, 'name': name, 'price': price, 'quantity': qty}}, upsert=True)

# Rentals
rental_file = DATA_DIR / 'rentalDatabase.txt'
if rental_file.exists():
    with rental_file.open('r', encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line: continue
            parts = line.split()
            if len(parts) >= 4:
                rid = int(parts[0])
                name = parts[1]
                price = float(parts[2])
                qty = int(parts[3])
                db.rentals.update_one({'rental_id': rid}, {'$set': {'rental_id': rid, 'name': name, 'price': price, 'quantity': qty}}, upsert=True)

# Coupons
coupon_file = DATA_DIR / 'couponNumber.txt'
if coupon_file.exists():
    with coupon_file.open('r', encoding='utf-8') as f:
        for line in f:
            code = line.strip()
            if code:
                db.coupons.update_one({'code': code}, {'$set': {'code': code, 'used': False}}, upsert=True)

# Users and user rentals
user_file = DATA_DIR / 'userDatabase.txt'
if user_file.exists():
    with user_file.open('r', encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line: continue
            parts = line.split()
            phone = parts[0]
            db.customers.update_one({'phone': phone}, {'$set': {'phone': phone}}, upsert=True)
            rentals = parts[1:]
            for r in rentals:
                try:
                    item_id, date_str, returned_str = r.split(',')
                    returned = True if returned_str.lower() in ('true','1','yes') else False
                    db.user_rentals.insert_one({'customer_phone': phone, 'item_id': int(item_id), 'rented_date': date_str, 'returned': returned})
                except Exception:
                    continue

# Sales/invoices import (best effort)
sale_file = DATA_DIR / 'saleInvoiceRecord.txt'
if sale_file.exists():
    with sale_file.open('r', encoding='utf-8') as f:
        lines = [l.rstrip() for l in f]
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if (len(line) >= 4 and line[0].isdigit() and ('-' in line or ':' in line)):
            created_at = line
            invoice = {'created_at': created_at, 'items': [], 'total_with_tax': None}
            i += 1
            while i < len(lines) and not lines[i].startswith('Total with tax') and lines[i].strip():
                parts = lines[i].split()
                if len(parts) >= 4:
                    item_id = parts[0]
                    item_name = parts[1]
                    qty = int(parts[2])
                    price = float(parts[3])
                    invoice['items'].append({'item_id': int(item_id) if item_id.isdigit() else None, 'item_name': item_name, 'quantity': qty, 'price': price})
                i += 1
            if i < len(lines) and lines[i].startswith('Total with tax'):
                try:
                    total = float(lines[i].split(':',1)[1].strip())
                    invoice['total_with_tax'] = total
                except Exception:
                    pass
            db.invoices.insert_one(invoice)
        else:
            i += 1

print('Migration complete. Data inserted into MongoDB at', args.mongo_uri)
