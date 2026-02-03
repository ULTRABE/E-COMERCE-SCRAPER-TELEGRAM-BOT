#!/usr/bin/env python3
"""
Quick test script to verify bot components work correctly
"""

import sys
import os

def test_imports():
    print("Testing imports...")
    try:
        import config
        print("✓ config imported")
        
        from database import Database
        print("✓ database imported")
        
        try:
            from auth_manager import AuthManager
            print("✓ auth_manager imported")
        except ImportError as e:
            print(f"⚠ auth_manager import warning: {e} (telegram module not installed)")
        
        try:
            from keyword_manager import KeywordManager
            print("✓ keyword_manager imported")
        except ImportError as e:
            print(f"⚠ keyword_manager import warning: {e} (telegram module not installed)")
        
        from message_formatter import MessageFormatter
        print("✓ message_formatter imported")
        
        from deal_processor import DealProcessor
        print("✓ deal_processor imported")
        
        from scrapers import ALL_SCRAPERS
        print(f"✓ scrapers imported ({len(ALL_SCRAPERS)} scrapers)")
        
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_database():
    print("\nTesting database...")
    try:
        import config
        from database import Database
        db = Database()
        print("✓ Database initialized")
        
        # Test authorization
        db.authorize_chat(12345, "Test Chat", 67890)
        assert db.is_chat_authorized(12345), "Chat should be authorized"
        print("✓ Authorization works")
        
        # Test keywords
        db.set_keywords(12345, ["test", "keyword"])
        keywords = db.get_keywords(12345)
        assert keywords == ["test", "keyword"], "Keywords should match"
        print("✓ Keyword filtering works")
        
        # Test deal history
        assert not db.is_duplicate_deal("test_hash"), "First deal should not be duplicate"
        db.add_deal("test_hash", "Test Product", "Test Site")
        assert db.is_duplicate_deal("test_hash"), "Second same deal should be duplicate"
        print("✓ Duplicate detection works")
        
        # Clean up
        if os.path.exists(config.DATABASE_PATH):
            os.remove(config.DATABASE_PATH)
        print("✓ Database tests passed")
        
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

def test_message_formatter():
    print("\nTesting message formatter...")
    try:
        from message_formatter import MessageFormatter
        
        deal = {
            'product_name': 'Test Product',
            'deal_price': 999,
            'original_price': 1999,
            'discount': 50,
            'url': 'https://example.com',
            'site': 'Test Site'
        }
        
        message = MessageFormatter.format_deal(deal)
        assert '999' in message, "Deal price should be in message"
        assert '1,999' in message, "Original price should be in message"
        assert '50%' in message, "Discount should be in message"
        print("✓ Message formatting works")
        
        return True
    except Exception as e:
        print(f"✗ Message formatter error: {e}")
        return False

def test_deal_processor():
    print("\nTesting deal processor...")
    try:
        import config
        from database import Database
        from deal_processor import DealProcessor
        
        db = Database()
        processor = DealProcessor(db)
        
        deals = [
            {
                'product_name': 'Product 1',
                'deal_price': 999,
                'original_price': 1999,
                'discount': 50,
                'url': 'https://example.com/1',
                'site': 'Site 1'
            },
            {
                'product_name': 'Product 2',
                'deal_price': 1499,
                'original_price': 2999,
                'discount': 50,
                'url': 'https://example.com/2',
                'site': 'Site 2'
            }
        ]
        
        processed = processor.process_deals(deals)
        assert len(processed) == 2, "Should have 2 unique deals"
        print("✓ Deal processing works")
        
        # Test duplicate filtering
        processed_again = processor.process_deals(deals)
        assert len(processed_again) == 0, "Should have 0 deals (all duplicates)"
        print("✓ Duplicate filtering works")
        
        # Clean up
        if os.path.exists(config.DATABASE_PATH):
            os.remove(config.DATABASE_PATH)
        
        return True
    except Exception as e:
        print(f"✗ Deal processor error: {e}")
        return False

def main():
    print("=" * 50)
    print("Testing Indian E-commerce Deal Bot")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_database,
        test_message_formatter,
        test_deal_processor,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    if failed == 0:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
