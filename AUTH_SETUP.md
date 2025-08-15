# Authentication System Setup Guide

This Case Opening Sheet Manager now includes enterprise-grade authentication with:
- Email verification for new accounts
- Time-limited PIN codes for quick access
- JWT token-based sessions
- Domain restriction to @pd15.org and @pd15.state.fl.us emails

## Email Configuration

### 1. Set up Email Provider

The system supports any SMTP server. For Gmail:

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Select "Mail" and generate password
3. Use this app password (not your regular password)

### 2. Environment Variables

Create a `.env` file in the project root with:

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
JWT_SECRET=your-secure-random-jwt-secret
```

**Important**: Add `.env` to your `.gitignore` to keep credentials secure.

### 3. Alternative Email Providers

#### Microsoft Outlook/Office365:
```bash
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

#### SendGrid:
```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

## Local Development

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
# Windows
set SMTP_USERNAME=your-email@gmail.com
set SMTP_PASSWORD=your-app-password
set JWT_SECRET=your-secret-key

# Linux/Mac
export SMTP_USERNAME=your-email@gmail.com
export SMTP_PASSWORD=your-app-password
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
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = "587"
SMTP_USERNAME = "your-email@gmail.com"
SMTP_PASSWORD = "your-gmail-app-password"
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
1. User enters username, email, password
2. System validates email domain (@pd15.org or @pd15.state.fl.us)
3. Verification code sent to email (10-minute expiry)
4. User enters code to activate account

### 2. Standard Login
1. User enters username/password
2. System generates JWT token (24-hour expiry)
3. User gains access to application

### 3. Quick PIN Login
1. User enters username
2. System sends 6-digit PIN to registered email (5-minute expiry)
3. User enters PIN for instant access

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