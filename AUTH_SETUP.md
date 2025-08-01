# Authentication System Setup Guide

This Case Opening Sheet Manager includes enterprise-grade authentication with:
- Email verification for new accounts
- Time-limited PIN codes for quick access
- JWT token-based sessions
- Domain restriction to @pd15.org and @pd15.state.fl.us emails

## Email Configuration

### 1. Organizational Email Setup

The system uses the **15th Judicial Circuit Public Defender's Office** email infrastructure:

- **SMTP Server**: Office365/Outlook (`smtp-mail.outlook.com`)
- **Email Domain**: @pd15.org or @pd15.state.fl.us
- **Purpose**: Sends verification codes and PINs TO users' work emails

### 2. Administrator Setup Required

**The system administrator must configure a dedicated service email account** such as:
- `casemanager@pd15.org`
- `system@pd15.org`
- `noreply@pd15.state.fl.us`

This service account will send verification emails TO users who register with their @pd15.org or @pd15.state.fl.us addresses.

### 3. Environment Variables

Create a `.env` file in the project root with:

```bash
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=casemanager@pd15.org
SMTP_PASSWORD=service-account-password
JWT_SECRET=your-secure-random-jwt-secret
```

**Important**: Add `.env` to your `.gitignore` to keep credentials secure.

### 4. Office365 Service Account Setup

The IT administrator should:

1. Create a dedicated service account (e.g., `casemanager@pd15.org`)
2. Assign appropriate mailbox permissions
3. Enable SMTP authentication for the service account
4. Provide credentials to application administrator

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

### 1. Add Secrets to Streamlit Cloud

In your Streamlit Cloud dashboard:

1. Go to your app settings
2. Click "Secrets"
3. Add:

```toml
[default]
SMTP_SERVER = "smtp-mail.outlook.com"
SMTP_PORT = "587"
SMTP_USERNAME = "casemanager@pd15.org"
SMTP_PASSWORD = "service-account-password"
JWT_SECRET = "your-secure-random-jwt-secret"
```

### 2. Update Authentication Module

For Streamlit Cloud, modify `modules/auth.py` to use Streamlit secrets:

```python
# Replace environment variable calls with:
smtp_username = st.secrets.get("SMTP_USERNAME")
smtp_password = st.secrets.get("SMTP_PASSWORD")
jwt_secret = st.secrets.get("JWT_SECRET", "fallback-secret")
```

## Authentication Flow

### 1. New User Registration
1. User enters username, email (@pd15.org or @pd15.state.fl.us), and password
2. System validates email domain (only organization emails allowed)
3. **Verification email sent FROM** `casemanager@pd15.org` **TO** user's work email
4. User receives 6-digit verification code (10-minute expiry)
5. User enters code to activate account

### 2. Standard Login
1. User enters username/password
2. System generates JWT token (24-hour expiry)
3. User gains access to application

### 3. Quick PIN Login
1. User enters username
2. **PIN email sent FROM** `casemanager@pd15.org` **TO** user's registered work email
3. User receives 6-digit PIN (5-minute expiry)
4. User enters PIN for instant access

### 4. Email Flow Diagram
```
Registration/PIN Request Flow:
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│ User registers  │────▶│ System sends     │────▶│ User receives email │
│ with work email │     │ FROM org account │     │ at work address     │
│ john@pd15.org   │     │ TO john@pd15.org │     │ with verification   │
└─────────────────┘     └──────────────────┘     └─────────────────────┘
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