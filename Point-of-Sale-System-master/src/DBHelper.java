import java.sql.*;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.io.IOException;
import java.nio.file.Files;

public class DBHelper {
    private static final String DB_FILE = "db/pos.db";
    private static final String SCHEMA_FILE = "db/schema.sql";

    public static Connection getConnection() throws SQLException {
        String url = "jdbc:sqlite:" + DB_FILE;
        return DriverManager.getConnection(url);
    }

    // Initialize DB by running the schema SQL if DB file doesn't exist or tables missing
    public static void initDatabase() throws SQLException, IOException {
        Path dbPath = Paths.get(DB_FILE);
        Path schemaPath = Paths.get(SCHEMA_FILE);
        boolean dbExists = Files.exists(dbPath);
        try (Connection conn = getConnection()) {
            // Only initialize schema when the DB file does not exist yet and schema.sql is present
            if (!dbExists && Files.exists(schemaPath)) {
                String sql = new String(Files.readAllBytes(schemaPath));
                try (Statement stmt = conn.createStatement()) {
                    stmt.executeUpdate("PRAGMA foreign_keys = ON;");
                    stmt.executeUpdate(sql);
                }
            }
        }
    }

    // Quick test main
    public static void main(String[] args) throws Exception {
        try {
            initDatabase();
            try (Connection c = getConnection()) {
                System.out.println("Connected to DB: " + c.getMetaData().getURL());
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
