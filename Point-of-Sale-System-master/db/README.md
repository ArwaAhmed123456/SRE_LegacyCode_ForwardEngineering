This folder contains the database schema and a migration helper for the Point-of-Sale project.

Files:
- `schema.sql` - SQLite schema to create tables for employees, items, rentals, customers, coupons, invoices, etc.
- `migrate.py` - Python script that reads the existing `Database/*.txt` files and inserts records into `db/pos.db`.

How to use (recommended):
1. Make sure you have Python 3 installed.
2. From the project root run:

   python db/migrate.py

   This will create `db/pos.db` and populate it from the text files. The script is conservative and inserts with `INSERT OR REPLACE`/`INSERT OR IGNORE` when possible.

Java integration:
- A lightweight `src/DBHelper.java` is added. It uses the `sqlite-jdbc` driver to open `db/pos.db`.
- Download the sqlite-jdbc JAR (e.g., `sqlite-jdbc-3.36.0.3.jar`) and add it to the project's classpath / NetBeans Libraries.
- Example run (from project root):

  javac -cp "lib/sqlite-jdbc.jar;" -d bin src/DBHelper.java
  java -cp "bin;lib/sqlite-jdbc.jar;" DBHelper

Notes:
- The migration script is a best-effort importer based on the existing file formats; edge cases may require manual fixes.
- Next steps: modify the Java code paths that read/write `Database/*.txt` (e.g., `EmployeeManagement.java`, `POSSystem.java`, `Transaction_Interface.java`) to use `DBHelper`/JDBC queries. If you want, I can implement those changes incrementally.
