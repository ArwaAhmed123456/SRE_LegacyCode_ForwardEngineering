Spring Boot backend for SG Technologies POS (starter)

Quick start (requires Java 21 and MongoDB):

1. Configure MongoDB URI in `src/main/resources/application.properties` or set `SPRING_DATA_MONGODB_URI` env var.
2. Build and run:

```powershell
cd backend
mvn clean package
java -jar target/pos-backend-0.1.0.jar
```

3. Migrate legacy data (optional) into Mongo using the provided Python script in `../scripts`:

```powershell
python ..\scripts\migrate_to_mongo.py --mongo-uri mongodb://localhost:27017/posdb
```

API endpoints (examples):
- GET /api/items
- POST /api/items
- GET /api/employees

This is a starter skeleton. Implement additional business rules, validation and endpoints as needed.