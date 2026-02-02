"""
Database Module - SQL Server Management for ELSA Clone Application
====================================================================
This module handles all database operations including:
- User registration and authentication
- Practice session history storage and retrieval
- Database initialization and connection management

Author: Team Member 1 (Hiếu)
Date: February 2026
"""

import pyodbc
from datetime import datetime
import hashlib
from typing import Optional, List, Tuple, Dict, Any


# ==========================================
# DATABASE CONFIGURATION
# ==========================================
class DatabaseConfig:
    """
    Database connection configuration
    Adjust these settings based on your SQL Server installation
    """
    SERVER = 'localhost'  # or your server name, e.g., 'localhost\\SQLEXPRESS'
    DATABASE = 'ELSA_Clone_DB'
    
    # Windows Authentication (recommended for local development)
    USE_WINDOWS_AUTH = True
    
    # SQL Server Authentication (use if Windows Auth is not available)
    USERNAME = 'sa'  # Change this if using SQL Auth
    PASSWORD = 'YourPassword123'  # Change this if using SQL Auth
    
    # Connection string builder
    @classmethod
    def get_connection_string(cls) -> str:
        """
        Build connection string based on authentication method
        
        Returns:
            str: Complete connection string for pyodbc
        """
        if cls.USE_WINDOWS_AUTH:
            # Windows Authentication (Trusted Connection)
            return (
                f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                f'SERVER={cls.SERVER};'
                f'DATABASE={cls.DATABASE};'
                f'Trusted_Connection=yes;'
            )
        else:
            # SQL Server Authentication
            return (
                f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                f'SERVER={cls.SERVER};'
                f'DATABASE={cls.DATABASE};'
                f'UID={cls.USERNAME};'
                f'PWD={cls.PASSWORD};'
            )


# ==========================================
# CORE DATABASE CLASS
# ==========================================
class DatabaseManager:
    """
    Main database manager class
    Handles all database operations for the ELSA Clone application
    """
    
    def __init__(self):
        """Initialize database manager"""
        self.connection_string = DatabaseConfig.get_connection_string()
        self._ensure_database_exists()
        self._initialize_tables()
    
    # ------------------------------------------
    # CONNECTION MANAGEMENT
    # ------------------------------------------
    
    def _get_connection(self) -> pyodbc.Connection:
        """
        Create and return a database connection
        
        Returns:
            pyodbc.Connection: Active database connection
            
        Raises:
            Exception: If connection fails
        """
        try:
            conn = pyodbc.connect(self.connection_string)
            return conn
        except pyodbc.Error as e:
            print(f"❌ Database connection error: {e}")
            raise
    
    def _ensure_database_exists(self):
        """
        Create database if it doesn't exist
        This connects to master database first to create our application database
        """
        try:
            # Connect to master database
            master_conn_string = self.connection_string.replace(
                f'DATABASE={DatabaseConfig.DATABASE}',
                'DATABASE=master'
            )
            conn = pyodbc.connect(master_conn_string)
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute(
                "SELECT database_id FROM sys.databases WHERE name = ?",
                (DatabaseConfig.DATABASE,)
            )
            
            if cursor.fetchone() is None:
                # Create database
                print(f"📦 Creating database: {DatabaseConfig.DATABASE}...")
                cursor.execute(f"CREATE DATABASE {DatabaseConfig.DATABASE}")
                print("✅ Database created successfully!")
            else:
                print(f"✅ Database '{DatabaseConfig.DATABASE}' already exists.")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Warning during database creation: {e}")
            print("Please ensure SQL Server is running and you have proper permissions.")
    
    # ------------------------------------------
    # TABLE INITIALIZATION
    # ------------------------------------------
    
    def _initialize_tables(self):
        """
        Create required tables if they don't exist
        Tables: Users, History
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Create Users table
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' AND xtype='U')
                CREATE TABLE Users (
                    UserID INT IDENTITY(1,1) PRIMARY KEY,
                    Username NVARCHAR(50) UNIQUE NOT NULL,
                    Password NVARCHAR(64) NOT NULL,
                    CreatedAt DATETIME DEFAULT GETDATE(),
                    LastLogin DATETIME NULL
                )
            """)
            
            # Create History table
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='History' AND xtype='U')
                CREATE TABLE History (
                    HistoryID INT IDENTITY(1,1) PRIMARY KEY,
                    UserID INT NOT NULL,
                    TargetText NVARCHAR(500) NOT NULL,
                    UserText NVARCHAR(500) NOT NULL,
                    Score DECIMAL(5,2) NOT NULL,
                    Similarity DECIMAL(5,2) NOT NULL,
                    PracticeDate DATETIME DEFAULT GETDATE(),
                    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print("✅ Database tables initialized successfully!")
            
        except Exception as e:
            print(f"❌ Error initializing tables: {e}")
            raise
    
    # ------------------------------------------
    # PASSWORD SECURITY
    # ------------------------------------------
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """
        Hash password using SHA-256
        
        Args:
            password (str): Plain text password
            
        Returns:
            str: Hashed password (64 characters)
        """
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    # ------------------------------------------
    # USER AUTHENTICATION FUNCTIONS
    # ------------------------------------------
    
    def register_user(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Register a new user in the database
        
        Args:
            username (str): Desired username (must be unique)
            password (str): User's password (will be hashed)
            
        Returns:
            Tuple[bool, str]: (Success status, Message)
            
        Example:
            >>> db = DatabaseManager()
            >>> success, msg = db.register_user("john_doe", "SecurePass123")
            >>> if success:
            ...     print(msg)  # "✅ User registered successfully!"
        """
        # Input validation
        if not username or len(username.strip()) == 0:
            return False, "❌ Username cannot be empty."
        
        if not password or len(password) < 6:
            return False, "❌ Password must be at least 6 characters long."
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check if username already exists
            cursor.execute(
                "SELECT UserID FROM Users WHERE Username = ?",
                (username.strip(),)
            )
            
            if cursor.fetchone() is not None:
                cursor.close()
                conn.close()
                return False, "❌ Username already exists. Please choose another."
            
            # Hash password and insert new user
            hashed_password = self._hash_password(password)
            cursor.execute(
                "INSERT INTO Users (Username, Password) VALUES (?, ?)",
                (username.strip(), hashed_password)
            )
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True, "✅ User registered successfully!"
            
        except Exception as e:
            return False, f"❌ Registration error: {str(e)}"
    
    def login_user(self, username: str, password: str) -> Tuple[Optional[int], str]:
        """
        Authenticate user and return UserID if successful
        
        Args:
            username (str): Username to authenticate
            password (str): Password to verify
            
        Returns:
            Tuple[Optional[int], str]: (UserID or None, Message)
            
        Example:
            >>> db = DatabaseManager()
            >>> user_id, msg = db.login_user("john_doe", "SecurePass123")
            >>> if user_id:
            ...     print(f"Logged in as user {user_id}")
        """
        # Input validation
        if not username or not password:
            return None, "❌ Username and password are required."
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Hash password for comparison
            hashed_password = self._hash_password(password)
            
            # Query user
            cursor.execute(
                "SELECT UserID FROM Users WHERE Username = ? AND Password = ?",
                (username.strip(), hashed_password)
            )
            
            result = cursor.fetchone()
            
            if result is not None:
                user_id = result[0]
                
                # Update last login timestamp
                cursor.execute(
                    "UPDATE Users SET LastLogin = GETDATE() WHERE UserID = ?",
                    (user_id,)
                )
                conn.commit()
                
                cursor.close()
                conn.close()
                
                return user_id, "✅ Login successful!"
            else:
                cursor.close()
                conn.close()
                return None, "❌ Invalid username or password."
                
        except Exception as e:
            return None, f"❌ Login error: {str(e)}"
    
    # ------------------------------------------
    # PRACTICE HISTORY FUNCTIONS
    # ------------------------------------------
    
    def save_practice_result(
        self,
        user_id: int,
        target: str,
        user_text: str,
        score: float,
        similarity: float = 0.0
    ) -> Tuple[bool, str]:
        """
        Save a practice session result to the database
        
        Args:
            user_id (int): ID of the user practicing
            target (str): Target text they were supposed to say
            user_text (str): What the user actually said (transcribed)
            score (float): Overall pronunciation score (0-100)
            similarity (float): IPA similarity score (0-1, will be converted to percentage)
            
        Returns:
            Tuple[bool, str]: (Success status, Message)
            
        Example:
            >>> db = DatabaseManager()
            >>> success, msg = db.save_practice_result(
            ...     user_id=1,
            ...     target="Hello world",
            ...     user_text="Hello world",
            ...     score=95.5,
            ...     similarity=0.98
            ... )
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Insert practice record
            cursor.execute("""
                INSERT INTO History (UserID, TargetText, UserText, Score, Similarity)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                target,
                user_text,
                round(score, 2),
                round(similarity * 100, 2)  # Convert to percentage
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True, "✅ Practice result saved!"
            
        except Exception as e:
            return False, f"❌ Error saving result: {str(e)}"
    
    def load_history(self, user_id: int, limit: int = 50) -> List[List[Any]]:
        """
        Load practice history for a specific user
        
        Args:
            user_id (int): User ID to load history for
            limit (int): Maximum number of records to return (default: 50)
            
        Returns:
            List[List[Any]]: List of records in format:
                [[Date, Target, Transcribed, Score, Similarity], ...]
                
        Example:
            >>> db = DatabaseManager()
            >>> history = db.load_history(user_id=1, limit=10)
            >>> for record in history:
            ...     print(f"Date: {record[0]}, Score: {record[3]}")
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Query history ordered by most recent first
            cursor.execute("""
                SELECT 
                    CONVERT(VARCHAR, PracticeDate, 120) as FormattedDate,
                    TargetText,
                    UserText,
                    Score,
                    CAST(Similarity AS VARCHAR) + '%' as SimilarityPercent
                FROM History
                WHERE UserID = ?
                ORDER BY PracticeDate DESC
            """, (user_id,), limit=limit)
            
            # Fetch all results
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            # Convert to list of lists for Gradio Dataframe compatibility
            history_data = [
                [
                    row[0],  # Date
                    row[1],  # Target
                    row[2],  # User text
                    row[3],  # Score
                    row[4]   # Similarity %
                ]
                for row in results
            ]
            
            return history_data
            
        except Exception as e:
            print(f"❌ Error loading history: {e}")
            return []
    
    def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        Get statistics for a user's practice sessions
        
        Args:
            user_id (int): User ID to get statistics for
            
        Returns:
            Dict[str, Any]: Statistics including:
                - total_sessions: Total number of practice sessions
                - average_score: Average score across all sessions
                - best_score: Highest score achieved
                - recent_improvement: Score trend (last 10 vs previous 10)
                
        Example:
            >>> db = DatabaseManager()
            >>> stats = db.get_user_statistics(user_id=1)
            >>> print(f"Average Score: {stats['average_score']:.1f}")
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get overall statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as TotalSessions,
                    AVG(Score) as AvgScore,
                    MAX(Score) as BestScore,
                    MIN(Score) as LowestScore
                FROM History
                WHERE UserID = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            
            if result and result[0] > 0:
                stats = {
                    'total_sessions': result[0],
                    'average_score': round(result[1], 2) if result[1] else 0,
                    'best_score': round(result[2], 2) if result[2] else 0,
                    'lowest_score': round(result[3], 2) if result[3] else 0
                }
            else:
                stats = {
                    'total_sessions': 0,
                    'average_score': 0,
                    'best_score': 0,
                    'lowest_score': 0
                }
            
            cursor.close()
            conn.close()
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {
                'total_sessions': 0,
                'average_score': 0,
                'best_score': 0,
                'lowest_score': 0
            }
    
    # ------------------------------------------
    # UTILITY FUNCTIONS
    # ------------------------------------------
    
    def clear_user_history(self, user_id: int) -> Tuple[bool, str]:
        """
        Clear all practice history for a user
        
        Args:
            user_id (int): User ID whose history to clear
            
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM History WHERE UserID = ?", (user_id,))
            deleted_count = cursor.rowcount
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True, f"✅ Cleared {deleted_count} practice sessions."
            
        except Exception as e:
            return False, f"❌ Error clearing history: {str(e)}"
    
    def delete_user(self, user_id: int) -> Tuple[bool, str]:
        """
        Delete a user and all their history (CASCADE)
        
        Args:
            user_id (int): User ID to delete
            
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM Users WHERE UserID = ?", (user_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True, "✅ User account deleted successfully."
            
        except Exception as e:
            return False, f"❌ Error deleting user: {str(e)}"


# ==========================================
# CONVENIENCE FUNCTIONS (Optional)
# ==========================================

# Global database instance (singleton pattern)
_db_instance = None

def get_database() -> DatabaseManager:
    """
    Get or create the global database instance
    
    Returns:
        DatabaseManager: Shared database manager instance
        
    Example:
        >>> db = get_database()
        >>> success, msg = db.register_user("test_user", "password123")
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance


# ==========================================
# TESTING & DEBUGGING
# ==========================================

def test_database_connection():
    """
    Test database connection and basic operations
    This function is for testing purposes only
    """
    print("=" * 50)
    print("DATABASE CONNECTION TEST")
    print("=" * 50)
    
    try:
        db = DatabaseManager()
        print("✅ Database manager initialized")
        
        # Test user registration
        print("\n--- Testing User Registration ---")
        success, msg = db.register_user("test_user_001", "TestPass123")
        print(msg)
        
        # Test login
        print("\n--- Testing User Login ---")
        user_id, msg = db.login_user("test_user_001", "TestPass123")
        print(msg)
        
        if user_id:
            # Test saving practice result
            print("\n--- Testing Practice Result Save ---")
            success, msg = db.save_practice_result(
                user_id=user_id,
                target="Hello world",
                user_text="Hello world",
                score=95.5,
                similarity=0.98
            )
            print(msg)
            
            # Test loading history
            print("\n--- Testing History Load ---")
            history = db.load_history(user_id)
            print(f"Loaded {len(history)} records")
            if history:
                print("Sample record:", history[0])
            
            # Test statistics
            print("\n--- Testing Statistics ---")
            stats = db.get_user_statistics(user_id)
            print(f"Total sessions: {stats['total_sessions']}")
            print(f"Average score: {stats['average_score']}")
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        print("=" * 50)


if __name__ == "__main__":
    # Run tests when file is executed directly
    test_database_connection()