-- ============================================================
-- setup_database.sql
-- Member 1: Database Logic (Hiếu)
--
-- HOW TO RUN:
--   Option 1: Open in SQL Server Management Studio (SSMS)
--             and press F5 / click "Execute"
--   Option 2: Command line:
--             sqlcmd -S localhost -U sa -P YourPassword -i setup_database.sql
-- ============================================================


-- ============================================================
-- 1. CREATE DATABASE
-- ============================================================
IF NOT EXISTS (
    SELECT name FROM sys.databases WHERE name = 'PronunciationDB'
)
BEGIN
    CREATE DATABASE PronunciationDB;
    PRINT 'Database PronunciationDB created.';
END
ELSE
    PRINT 'Database PronunciationDB already exists.';
GO

USE PronunciationDB;
GO


-- ============================================================
-- 2. CREATE TABLE: Users
-- ============================================================
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Users'
)
BEGIN
    CREATE TABLE Users (
        UserID    INT           IDENTITY(1,1) PRIMARY KEY,
        Username  NVARCHAR(100) NOT NULL UNIQUE,
        Password  NVARCHAR(256) NOT NULL,        -- stores SHA-256 hash from Python
        CreatedAt DATETIME      DEFAULT GETDATE()
    );
    PRINT 'Table Users created.';
END
ELSE
    PRINT 'Table Users already exists.';
GO


-- ============================================================
-- 3. CREATE TABLE: History
-- ============================================================
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'History'
)
BEGIN
    CREATE TABLE History (
        HistoryID   INT           IDENTITY(1,1) PRIMARY KEY,
        UserID      INT           NOT NULL
                                  REFERENCES Users(UserID) ON DELETE CASCADE,
        TargetText  NVARCHAR(500),
        UserText    NVARCHAR(500),
        Score       FLOAT,
        Similarity  NVARCHAR(20),
        PracticedAt DATETIME      DEFAULT GETDATE()
    );
    PRINT 'Table History created.';
END
ELSE
    PRINT 'Table History already exists.';
GO


-- ============================================================
-- 4. STORED PROCEDURES
-- ============================================================

-- 4a. Register a new user
CREATE OR ALTER PROCEDURE sp_RegisterUser
    @Username NVARCHAR(100),
    @Password NVARCHAR(256)       -- pass the SHA-256 hash from Python
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS (SELECT 1 FROM Users WHERE Username = @Username)
    BEGIN
        SELECT -1 AS UserID, 'Username already taken.' AS Message;
        RETURN;
    END

    INSERT INTO Users (Username, Password)
    VALUES (@Username, @Password);

    SELECT SCOPE_IDENTITY() AS UserID, 'Account created successfully.' AS Message;
END
GO


-- 4b. Login (validate credentials)
CREATE OR ALTER PROCEDURE sp_LoginUser
    @Username NVARCHAR(100),
    @Password NVARCHAR(256)
AS
BEGIN
    SET NOCOUNT ON;

    SELECT UserID, Username, 'Login successful.' AS Message
    FROM   Users
    WHERE  Username = @Username
      AND  Password = @Password;

    -- Returns 0 rows if credentials are wrong (Python checks for empty result)
END
GO


-- 4c. Save a practice result
CREATE OR ALTER PROCEDURE sp_SavePracticeResult
    @UserID    INT,
    @Target    NVARCHAR(500),
    @UserText  NVARCHAR(500),
    @Score     FLOAT,
    @Similarity NVARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO History (UserID, TargetText, UserText, Score, Similarity)
    VALUES (@UserID, @Target, @UserText, @Score, @Similarity);

    SELECT SCOPE_IDENTITY() AS NewHistoryID;
END
GO


-- 4d. Load history for a user (newest first)
CREATE OR ALTER PROCEDURE sp_LoadHistory
    @UserID INT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        HistoryID,
        CONVERT(NVARCHAR(16), PracticedAt, 120) AS PracticedAt,
        TargetText,
        UserText,
        Score,
        Similarity
    FROM   History
    WHERE  UserID = @UserID
    ORDER  BY PracticedAt DESC;
END
GO


-- 4e. Get aggregate stats for a user
CREATE OR ALTER PROCEDURE sp_GetUserStats
    @UserID INT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        COUNT(*)                                      AS TotalAttempts,
        ISNULL(ROUND(AVG(Score), 1), 0)              AS AverageScore,
        ISNULL(MAX(Score), 0)                         AS BestScore,
        CONVERT(NVARCHAR(16), MAX(PracticedAt), 120)  AS LastPracticed
    FROM History
    WHERE UserID = @UserID;
END
GO


-- 4f. Delete a single history entry (ownership-safe)
CREATE OR ALTER PROCEDURE sp_DeleteHistoryEntry
    @HistoryID INT,
    @UserID    INT
AS
BEGIN
    SET NOCOUNT ON;

    DELETE FROM History
    WHERE HistoryID = @HistoryID
      AND UserID    = @UserID;

    SELECT @@ROWCOUNT AS RowsDeleted;
END
GO


-- ============================================================
-- 5. VERIFY — quick check after running the script
-- ============================================================
SELECT
    t.name        AS TableName,
    c.name        AS ColumnName,
    tp.name       AS DataType,
    c.max_length  AS MaxLength,
    c.is_nullable AS IsNullable
FROM sys.tables t
JOIN sys.columns c  ON t.object_id = c.object_id
JOIN sys.types   tp ON c.user_type_id = tp.user_type_id
WHERE t.name IN ('Users', 'History')
ORDER BY t.name, c.column_id;
GO

PRINT '===== setup_database.sql completed successfully =====';
GO
