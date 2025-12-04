# Development Setup Guide

## SSL Certificate Generation (Local Development Only)

For HTTPS development testing, generate a self-signed certificate:

### On Windows (PowerShell):
```powershell
# Install OpenSSL if you don't have it
choco install openssl -y

# Generate certificate valid for 365 days
openssl req -x509 -newkey rsa:4096 -nodes -out cert.crt -keyout cert.key -days 365
```

### On macOS/Linux:
```bash
# Generate certificate valid for 365 days
openssl req -x509 -newkey rsa:4096 -nodes -out cert.crt -keyout cert.key -days 365
```

When prompted, fill in the details (you can press Enter to skip most fields):
- Country: US (or your country)
- State: Your State
- City: Your City
- Organization: Your Organization
- Common Name: localhost (important!)
- Email: your@email.com

The generated files (`cert.crt` and `cert.key`) are in `.gitignore` and won't be committed.

## Running the Development Server with HTTPS

```bash
python manage.py runsslserver
```

## Production

Heroku handles SSL automatically with Let's Encrypt. No certificate files needed!
