#!/usr/bin/env python3
"""
Simple utility to encrypt/decrypt .env files
Usage: python encrypt_env.py encrypt/decrypt
"""
import sys
import os
from cryptography.fernet import Fernet

def generate_key():
    """Generate a key and save it to a file"""
    key = Fernet.generate_key()
    with open('.env.key', 'wb') as key_file:
        key_file.write(key)
    print("🔑 Key generated and saved to .env.key")
    print("⚠️  Keep this key file secure and separate from your repository!")
    return key

def load_key():
    """Load key from file"""
    try:
        with open('.env.key', 'rb') as key_file:
            return key_file.read()
    except FileNotFoundError:
        print("❌ Key file not found. Run 'generate_key' first.")
        return None

def encrypt_env():
    """Encrypt .env file"""
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return
    
    key = load_key() or generate_key()
    fernet = Fernet(key)
    
    with open('.env', 'rb') as file:
        file_data = file.read()
    
    encrypted_data = fernet.encrypt(file_data)
    
    with open('.env.encrypted', 'wb') as file:
        file.write(encrypted_data)
    
    print("✅ .env file encrypted to .env.encrypted")
    print("🗑️  You can now delete the original .env file")

def decrypt_env():
    """Decrypt .env file"""
    if not os.path.exists('.env.encrypted'):
        print("❌ .env.encrypted file not found")
        return
    
    key = load_key()
    if not key:
        return
    
    fernet = Fernet(key)
    
    with open('.env.encrypted', 'rb') as file:
        encrypted_data = file.read()
    
    try:
        decrypted_data = fernet.decrypt(encrypted_data)
        
        with open('.env', 'wb') as file:
            file.write(decrypted_data)
        
        print("✅ .env file decrypted successfully")
    except Exception as e:
        print(f"❌ Decryption failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python encrypt_env.py [encrypt|decrypt|generate_key]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "encrypt":
        encrypt_env()
    elif command == "decrypt":
        decrypt_env()
    elif command == "generate_key":
        generate_key()
    else:
        print("❌ Invalid command. Use: encrypt, decrypt, or generate_key")