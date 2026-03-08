"""
Unit tests for Kudos System with PostgreSQL
"""

import unittest
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from app.modules.kudos_system import KudosSystem, User, Kudos, Base

# Load test environment
load_dotenv('.env.test')

class TestKudosSystemPostgres(unittest.TestCase):
    """Test Kudos System with PostgreSQL database"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database once"""
        # Use test database
        test_db_url = os.getenv(
            'TEST_DATABASE_URL',
            'postgresql://postgres:postgres@localhost:5432/kudos_test_db'
        )
        
        # Create engine for test setup
        cls.engine = create_engine(test_db_url)
        
        # Create all tables
        Base.metadata.create_all(cls.engine)
        
        # Initialize system with test DB
        cls.system = KudosSystem(test_db_url)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test database"""
        Base.metadata.drop_all(cls.engine)
    
    def setUp(self):
        """Set up test data"""
        self.session = self.system.get_session()
        
        # Clean up existing data
        self.session.query(ModerationLog).delete()
        self.session.query(Kudos).delete()
        self.session.query(User).delete()
        self.session.commit()
        
        # Create test users
        self.user1 = self.system.create_user(
            username="testuser1",
            email="test1@example.com",
            full_name="Test User 1",
            department="Engineering",
            is_admin=False
        )
        
        self.user2 = self.system.create_user(
            username="testuser2",
            email="test2@example.com",
            full_name="Test User 2",
            department="Marketing",
            is_admin=False
        )
        
        self.admin = self.system.create_user(
            username="admin",
            email="admin@example.com",
            full_name="Admin User",
            department="IT",
            is_admin=True
        )
    
    def tearDown(self):
        """Clean up after each test"""
        self.session.close()
    
    def test_create_user_postgres(self):
        """Test user creation with PostgreSQL"""
        user = self.system.create_user(
            username="newuser",
            email="new@example.com",
            full_name="New User",
            department="Sales"
        )
        
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.email, "new@example.com")
        
        # Test duplicate username
        with self.assertRaises(ValueError):
            self.system.create_user(
                username="newuser",
                email="another@example.com",
                full_name="Another User"
            )
    
    def test_send_kudos_postgres(self):
        """Test sending kudos with PostgreSQL"""
        kudos = self.system.send_kudos(
            sender_id=self.user1.id,
            receiver_id=self.user2.id,
            message="Great work!"
        )
        
        self.assertIsNotNone(kudos.id)
        self.assertTrue(kudos.is_visible)
        
        # Test self-kudos prevention
        with self.assertRaises(ValueError):
            self.system.send_kudos(
                sender_id=self.user1.id,
                receiver_id=self.user1.id,
                message="To myself"
            )
    
    def test_public_feed_postgres(self):
        """Test public feed with PostgreSQL"""
        # Send multiple kudos
        for i in range(5):
            self.system.send_kudos(
                sender_id=self.user1.id,
                receiver_id=self.user2.id,
                message=f"Kudos {i}"
            )
        
        feed = self.system.get_public_feed(limit=3)
        self.assertEqual(len(feed), 3)
        self.assertEqual(feed[0]['message'], "Kudos 4")  # Most recent first
    
    def test_moderation_postgres(self):
        """Test moderation with PostgreSQL transaction"""
        kudos = self.system.send_kudos(
            sender_id=self.user1.id,
            receiver_id=self.user2.id,
            message="Questionable content"
        )
        
        # Test hide
        result = self.system.moderate_kudos(
            kudos_id=kudos.id,
            moderator_id=self.admin.id,
            action='hide',
            reason='Inappropriate'
        )
        
        self.assertTrue(result)
        
        # Verify hidden
        feed = self.system.get_public_feed()
        self.assertNotIn(kudos.id, [k['id'] for k in feed])
        
        # Test restore
        result = self.system.moderate_kudos(
            kudos_id=kudos.id,
            moderator_id=self.admin.id,
            action='restore'
        )
        
        self.assertTrue(result)
        
        # Verify restored
        feed = self.system.get_public_feed()
        self.assertIn(kudos.id, [k['id'] for k in feed])
    
    def test_statistics_postgres(self):
        """Test statistics with PostgreSQL aggregation"""
        # Create some data
        for i in range(3):
            self.system.send_kudos(
                sender_id=self.user1.id,
                receiver_id=self.user2.id,
                message=f"Test {i}"
            )
        
        stats = self.system.get_statistics()
        
        self.assertGreaterEqual(stats['total_users'], 3)
        self.assertGreaterEqual(stats['total_kudos'], 3)
        self.assertIn('top_receivers', stats)
    
    def test_concurrent_transactions(self):
        """Test concurrent kudos sending (PostgreSQL transaction isolation)"""
        import threading
        
        results = []
        
        def send_kudos_thread():
            try:
                kudos = self.system.send_kudos(
                    sender_id=self.user1.id,
                    receiver_id=self.user2.id,
                    message="Concurrent test"
                )
                results.append(True)
            except:
                results.append(False)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            t = threading.Thread(target=send_kudos_thread)
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # All should succeed with proper transaction isolation
        self.assertEqual(len(results), 5)
        self.assertTrue(all(results))

if __name__ == '__main__':
    unittest.main()