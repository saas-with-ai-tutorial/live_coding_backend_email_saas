#!/usr/bin/env python3
"""
Simple test script for GmailHelper.

Before running:
1. Copy env.template to .env
2. Fill in your Gmail credentials in .env file

Run:
    python test_gmail.py
"""

from src.core.gmail_helper import GmailHelper


def main():
    print("=" * 60)
    print("Gmail Helper Test")
    print("=" * 60)
    
    try:
        # Test with context manager (auto connect/disconnect)
        with GmailHelper() as gmail:
            
            # Get available folders
            print("\n📁 Listing available folders...")
            folders = gmail.get_folders()
            if folders:
                print(f"Found {len(folders)} folders:")
                for folder in folders[:10]:  # Show first 10
                    print(f"  - {folder}")
            
            # Read latest 5 emails
            print("\n📧 Reading latest 5 emails...")
            emails = gmail.read_latest_emails(n=5)
            
            if not emails:
                print("No emails found!")
            else:
                print(f"\nFound {len(emails)} emails:\n")
                
                for i, email_data in enumerate(emails, 1):
                    print(f"{i}. {email_data['subject']}")
                    print(f"   From: {email_data['from_name']} <{email_data['from']}>")
                    print(f"   Date: {email_data['date']}")
                    print(f"   Unread: {'Yes ✉️' if email_data['is_unread'] else 'No ✅'}")
                    print(f"   Snippet: {email_data['snippet'][:100]}...")
                    print()
            
            # Read only unread emails
            print("\n📬 Checking for unread emails...")
            unread_emails = gmail.read_latest_emails(n=10, unread_only=True)
            print(f"Found {len(unread_emails)} unread emails")
            
            if unread_emails:
                print("\nUnread emails:")
                for email_data in unread_emails[:3]:  # Show first 3
                    print(f"  ✉️  {email_data['subject']}")
                    print(f"     From: {email_data['from_name']}")
        
        print("\n" + "=" * 60)
        print("✅ Test completed successfully!")
        print("=" * 60)
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease follow these steps:")
        print("1. Copy env.template to .env")
        print("2. Add your Gmail credentials to .env file")
        print("3. Get App Password from: https://myaccount.google.com/apppasswords")
        
    except ConnectionError as e:
        print(f"\n❌ Connection Error: {e}")
        print("\nPlease check:")
        print("1. Your internet connection")
        print("2. Your Gmail credentials in .env file")
        print("3. That 2-factor authentication is enabled")
        print("4. That you're using an App Password, not your regular password")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
