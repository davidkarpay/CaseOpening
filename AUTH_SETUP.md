# Authentication System Setup Guide

This Case Opening Sheet Manager includes secure authentication for **15th Judicial Circuit Public Defender's Office** staff:

## Authentication Features
- **Account Creation**: Only @pd15.org and @pd15.state.fl.us email addresses allowed
- **Email Verification**: Required for all new accounts
- **Two Login Methods**:
  1. Email + Password (standard login)
  2. Quick PIN Login (6-digit code sent to email)

## Administrator Setup

### 1. Email Configuration Required

The system administrator must configure a dedicated service email account:
- **Service Account**: `casemanager@pd15.org` (or similar)
- **SMTP Server**: Office365/Outlook (`smtp-mail.outlook.com`)
- **Purpose**: Sends verification codes and PINs to staff emails

### 2. Environment Variables

Set these environment variables or create a `.env` file:

```bash
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=casemanager@pd15.org
SMTP_PASSWORD=service-account-password
JWT_SECRET=your-secure-random-jwt-secret
```

### 3. Service Account Setup

The IT administrator must:
1. Create dedicated service account (e.g., `casemanager@pd15.org`)
2. Enable SMTP authentication for the account
3. Provide credentials to application administrator

## Local Development

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
# Windows
set SMTP_USERNAME=casemanager@pd15.org
set SMTP_PASSWORD=service-account-password
set JWT_SECRET=your-secret-key

# Linux/Mac
export SMTP_USERNAME=casemanager@pd15.org
export SMTP_PASSWORD=service-account-password
export JWT_SECRET=your-secret-key
```

### 3. Run the Application
```bash
streamlit run case-opening-app.py
```

## Streamlit Cloud Deployment

Add these secrets in your Streamlit Cloud dashboard:

```toml
[default]
SMTP_SERVER = "smtp-mail.outlook.com"
SMTP_PORT = "587"
SMTP_USERNAME = "casemanager@pd15.org"
SMTP_PASSWORD = "service-account-password"
JWT_SECRET = "your-secure-random-jwt-secret"
```

## How It Works

### 1. Account Creation
1. User enters username, **@pd15.org or @pd15.state.fl.us email**, and password
2. System validates email domain (rejects non-PD emails)
3. Verification email sent to user's work email
4. User enters 6-digit code to activate account (10-minute expiry)

### 2. Login Options
**Option A - Email + Password:**
1. User enters email and password
2. Immediate access granted

**Option B - Quick PIN Login:**
1. User enters email address
2. 6-digit PIN sent to their work email (5-minute expiry)
3. User enters PIN for instant access

### 3. Email Flow
```
System Email Account → User's Work Email
casemanager@pd15.org → john@pd15.org
    (Verification codes & PINs)
```

## Security Features

- **Password Hashing**: SHA-256 with random salt
- **JWT Tokens**: HMAC-SHA256 signed, 24-hour expiry
- **Time-Limited Codes**: All verification codes and PINs expire
- **Domain Restriction**: Only @pd15.org and @pd15.state.fl.us emails allowed
- **Session Management**: Automatic token verification and cleanup
- **Data Encryption**: All sensitive data hashed/encrypted

## Data Storage

User data is stored in JSON files in the `/data` directory:
- `users.json`: Active user accounts
- `pending_users.json`: Unverified registrations (auto-cleanup)
- `login_pins.json`: Active PIN codes (auto-cleanup)

## Troubleshooting

### Email Not Sending
1. Check SMTP credentials
2. Verify app password (not regular password for Gmail)
3. Check firewall/network restrictions
4. Test with different SMTP provider

### Token Issues
1. Verify JWT_SECRET is set consistently
2. Check token expiry (24 hours)
3. Clear browser cache/session

### Domain Restrictions
1. Ensure email ends with @pd15.org or @pd15.state.fl.us
2. Check for typos in email address
3. Contact administrator if domain should be added

## Admin Tasks

### Add New Allowed Domain
Edit `modules/auth.py`:
```python
self.allowed_domains = ['@pd15.org', '@pd15.state.fl.us', '@newdomain.com']
```

### Reset User Password
Delete user from `data/users.json` and have them re-register.

### View User Activity
Check `lastLogin` timestamps in `data/users.json`.

## Production Considerations

1. **Database**: Consider migrating to PostgreSQL for production
2. **Backup**: Regular backups of `/data` directory
3. **Monitoring**: Log authentication attempts
4. **Rate Limiting**: Add rate limiting for PIN requests
5. **SSL/HTTPS**: Ensure all traffic is encrypted
6. **Secrets Management**: Use proper secrets management service