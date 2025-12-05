# Legacy System Documentation (Reverse-Engineered)

## 1. System Overview
The SG Technologies Point-of-Sale (POS) system is a desktop Java Swing application (NetBeans/Ant project) that supports sales, rentals, returns and employee management. Data persistence is implemented using plain text files kept in the `Database/` folder. The UI is implemented in Swing classes, with `POSSystem`/`Register` serving as entry points.

## 2. Module Inventory (mapping of key files to modules)
- UI / Presentation
  - `src/Login_Interface.java` — Login screen, authentication flow
  - `src/Cashier_Interface.java` — Cashier menu / navigation
  - `src/Admin_Interface.java` — Admin menu and employee management UI
  - `src/Transaction_Interface.java`, `EnterItem_Interface.java`, `Payment_Interface.java` — Transaction flows
- Business Logic
  - `src/PointOfSale.java` (abstract) — core POS operations (add, remove, totals)
  - `src/POS.java`, `src/POR.java`, `src/POH.java` — concrete implementations for sale, rental, and other modes
  - `src/Management.java`, `src/EmployeeManagement.java` — employee logic and user management
  - `src/Inventory.java`, `src/Item.java` — inventory operations
  - `src/ReturnItem.java`, `src/Rental.java`, `src/Sale.java` — transaction domains
- Data Access / Persistence
  - `Database/*.txt` — plain-text persistence files
  - `src/DBHelper.java` — helper to integrate with `db/pos.db` (SQLite) if used
  - `db/migrate.py` and `db/schema.sql` — existing SQLite migration artifacts
- Tests & Misc
  - `tests/EmployeeTest.java` — unit tests (JUnit not yet wired)
  - `SGTechnologies.jar` — packaged jar

## 3. High-level Control Flow
1. `Register` (main) -> launches `Login_Interface`.
2. On successful login, user is routed to `Cashier_Interface` or `Admin_Interface` according to role.
3. Cashier creates transactions by opening `Transaction_Interface` and adding items (via `EnterItem_Interface`), ending with `Payment_Interface` which writes invoices/records to file.
4. Employee management flows invoke `EmployeeManagement` to add/update/delete entries in `Database/employeeDatabase.txt`.

## 4. Identified Code & Data Smells
- Data persistence in plain text: brittle parsing, no transactional guarantees, hard to query
- Compiled `.class` files committed to `bin/` — increases repo noise and causes merge conflicts
- Use of deprecated APIs (`JPasswordField.getText()`) — partially fixed
- Lack of dependency manager: Ant + NetBeans project is harder to reproduce than Maven/Gradle
- Minimal or no automated tests wired into CI

## 5. Current Limitations
- No centralized database; cross-referencing (invoices, rentals) is manual and fragile
- UI is monolithic Swing code intermixed with business logic — limited separation of concerns
- No REST API or service layer for integrating other clients
- No CI/CD or reproducible builds beyond local Ant/NetBeans

## 6. Files-to-Module Mapping (quick table)
| File | Module | Notes |
|------|--------|-------|
| src/Login_Interface.java | UI | Login handling, uses `POSSystem.logIn` |
| src/EmployeeManagement.java | Business | Reads/writes `Database/employeeDatabase.txt` |
| db/migrate.py | Data Migration | Creates SQLite DB from text files |
| src/DBHelper.java | Data Access | SQLite helper (unused in many flows) |

## 7. Recommendations for Forward Engineering
- Migrate all data to a centralized DB (MongoDB chosen for speed in prototyping since data is semi-structured and we will build a REST API). If relational constraints are required, use PostgreSQL.
- Separate layers: REST controllers (Spring Boot), services (business logic), repositories (MongoDB via Spring Data or JPA for SQL), and a React frontend.
- Convert build to Maven for the backend and npm for frontend; add GitHub Actions for build/test.
- Create an automated migration pipeline (Python scripts) to import legacy text files into MongoDB and validate data integrity.

## 8. Next Documentation Deliverables (planned)
- Extracted UML class diagrams (PlantUML) for the main domain objects
- Sequence diagrams for login and transaction checkout flows
- Mapping of refactorings with before/after code snippets

