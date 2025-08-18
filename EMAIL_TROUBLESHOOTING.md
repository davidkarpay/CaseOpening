# Email Verification Troubleshooting Guide

## Problem: "Failed to send verification email. Please try again." Error

This guide will help you resolve email verification issues when registering with your @pd15.org account.

## Quick Fix: Development/Testing Mode

**I've just enabled mock mode for you!** The application will now display verification codes directly in the UI instead of trying to send real emails.

### What Changed:
- Created `.env` file with `EMAIL_MOCK_MODE=true`
- Verification codes will now appear on screen
- No real emails will be sent during development

### How to Test:
1. **Restart the Streamlit application** (Important!)
2. Try registering again with your @pd15.org email
3. You should now see the verification code displayed in the UI instead of getting an error
4. Copy the 6-digit code and use it to complete registration

## Production Email Setup (For Real Email Sending)

If you want to enable actual email sending, follow these steps:

### Option 1: Use Encrypted Credentials (Recommended)
1. **Go to Settings Page**: Navigate to ⚙️ Settings in the sidebar
2. **Configure SMTP**: Use the secure credential setup form
3. **Required Information**:
   - Your administrator email: `dkarpay@pd15.org`
   - Master password (12+ characters, you choose this)
   - SMTP username: Your office email (`dkarpay@pd15.org`)
   - SMTP password: Your email password or app-specific password

### Option 2: Environment Variables
Edit the `.env` file and add:
```env
EMAIL_MOCK_MODE=false
SMTP_USERNAME=dkarpay@pd15.org
SMTP_PASSWORD=your-email-password
```

## Understanding the Email System

### Mock Mode (Development)
- ✅ **Enabled by default** (I just set this up)
- Shows verification codes in the UI
- Perfect for testing and development
- No real emails sent

### Production Mode
- Sends real emails via Office365/Outlook SMTP
- Requires valid SMTP credentials
- Uses secure encrypted storage
- Requires master password to unlock

## Current Configuration Status

You can check your current configuration by:
1. Going to ⚙️ **Settings** page
2. Looking at the **📧 Email Configuration Status** section
3. You should see:
   - Mock Mode: ✅ Enabled
   - Secure Storage: Status depends on setup
   - Session Unlocked: Status depends on credentials

## Troubleshooting Steps

### Step 1: Restart Application
```bash
# Stop current Streamlit session (Ctrl+C)
# Then restart:
streamlit run case-opening-app.py
```

### Step 2: Check Mock Mode
- Look for "📧 **Development Mode**: Email sent to..." messages
- Verification codes should appear as "🔑 **Your Code**: 123456"

### Step 3: If Still Not Working
Check for these common issues:

1. **Environment variables not loaded**
   - Make sure `.env` file is in the project root
   - Restart the application after creating `.env`

2. **Python dotenv not installed**
   ```bash
   pip install python-dotenv
   ```

3. **File permissions**
   - Ensure the application can read the `.env` file

### Step 4: Manual Environment Setup
If `.env` file isn't working, set environment variable manually:

**Windows Command Prompt:**
```cmd
set EMAIL_MOCK_MODE=true
streamlit run case-opening-app.py
```

**Windows PowerShell:**
```powershell
$env:EMAIL_MOCK_MODE = "true"
streamlit run case-opening-app.py
```

## Expected Behavior After Fix

### Registration Process:
1. Enter your @pd15.org email and password
2. Click "Register"
3. You should see:
   - ✅ "Registration successful! Please check your email for a verification code."
   - 📧 "**Development Mode**: Email sent to dkarpay@pd15.org"
   - 🔑 "**Your Code**: 123456" (actual 6-digit number)
   - ⚠️ "**Remember this code** - you'll need it on the next screen!"

4. Copy the code and enter it on the verification page
5. Complete registration successfully

## Need Production Email?

For production use with real emails:

1. **Get Office365 App Password**:
   - Go to Microsoft 365 admin center
   - Generate app-specific password for SMTP
   - This is more secure than using your main password

2. **Configure in Settings Page**:
   - Use the secure credential setup
   - Enter your app password (not main password)
   - Set a strong master password for encryption

3. **Disable Mock Mode**:
   - Change `EMAIL_MOCK_MODE=false` in `.env`
   - Restart application

## Support

If you're still having issues:
1. Check the Streamlit console for detailed error messages
2. Verify your @pd15.org domain is exactly `@pd15.org` (not `@pd15.state.fl.us`)
3. Try the mock mode first to verify the registration flow works
4. Then configure production email if needed

The mock mode should resolve your immediate issue and let you test the application fully!