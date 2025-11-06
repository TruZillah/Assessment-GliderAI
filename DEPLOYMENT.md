# Production Deployment Guide

This guide walks you through deploying the Assessment-GliderAI application in a production environment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Docker Deployment (Recommended)](#docker-deployment-recommended)
3. [Manual Deployment](#manual-deployment)
4. [Configuration](#configuration)
5. [Security Best Practices](#security-best-practices)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required
- Python 3.8+ (for manual deployment)
- Docker & Docker Compose (for container deployment)
- SSL certificates (for HTTPS in production)

### Recommended
- Domain name
- Reverse proxy (Nginx)
- Linux server (Ubuntu 20.04+ or similar)

---

## Docker Deployment (Recommended)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/TruZillah/Assessment-GliderAI.git
   cd Assessment-GliderAI
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your values
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Verify it's running**
   ```bash
   docker-compose ps
   curl http://localhost:8000/api/ask/status
   ```

### With Nginx and SSL

1. **Obtain SSL certificates**
   - Use Let's Encrypt: `certbot certonly --standalone -d yourdomain.com`
   - Or place your certificates in `./ssl/` directory

2. **Update nginx.conf**
   - Uncomment the HTTPS server block
   - Update server_name with your domain
   - Point to your SSL certificate paths

3. **Start with Nginx**
   ```bash
   docker-compose up -d
   ```

### Docker Commands

```bash
# View logs
docker-compose logs -f app

# Restart service
docker-compose restart app

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Access container shell
docker-compose exec app /bin/bash
```

---

## Manual Deployment

### Linux/WSL with systemd

1. **Install dependencies**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv nginx
   ```

2. **Setup application**
   ```bash
   sudo mkdir -p /opt/assessment-gliderai
   cd /opt/assessment-gliderai
   git clone https://github.com/TruZillah/Assessment-GliderAI.git .
   
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   nano .env  # Add your API keys
   ```

4. **Setup systemd service**
   ```bash
   sudo cp assessment.service /etc/systemd/system/
   sudo nano /etc/systemd/system/assessment.service  # Update paths
   
   sudo mkdir -p /var/log/assessment
   sudo chown www-data:www-data /var/log/assessment
   
   sudo systemctl daemon-reload
   sudo systemctl enable assessment
   sudo systemctl start assessment
   ```

5. **Configure Nginx**
   ```bash
   sudo cp nginx.conf /etc/nginx/sites-available/assessment
   sudo ln -s /etc/nginx/sites-available/assessment /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

6. **Setup SSL with Let's Encrypt**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

### Windows with Waitress

1. **Install Python dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

2. **Create startup script** (`start-production.bat`)
   ```batch
   @echo off
   set OPENAI_API_KEY=sk-your-key
   set ADMIN_PASSWORD=your-password
   set FLASK_ENV=production
   python -m waitress --listen=*:8000 app:app
   pause
   ```

3. **Run as Windows Service (using NSSM)**
   ```cmd
   # Download NSSM from https://nssm.cc/
   nssm install AssessmentApp
   # Set the path to python.exe and arguments in NSSM GUI
   # Add environment variables in the Environment tab
   nssm start AssessmentApp
   ```

---

## Configuration

### Environment Variables

Create a `.env` file with the following:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4

# Admin Panel Security
ADMIN_PASSWORD=change-this-to-secure-password

# Flask Configuration
FLASK_ENV=production
```

### Using the Admin Panel

1. Access: `http://your-domain.com/admin.html`
2. Login with your `ADMIN_PASSWORD`
3. Configure OpenAI API key through the web interface
4. Test the key before saving
5. Select your preferred OpenAI model

---

## Security Best Practices

### Essential Security Measures

1. **Change Default Passwords**
   - Set a strong `ADMIN_PASSWORD` (minimum 16 characters)
   - Use environment variables, not hardcoded values

2. **Enable HTTPS/SSL**
   - Use Let's Encrypt for free SSL certificates
   - Redirect all HTTP traffic to HTTPS
   - Enable HSTS headers

3. **Firewall Configuration**
   ```bash
   sudo ufw allow 22/tcp    # SSH
   sudo ufw allow 80/tcp    # HTTP
   sudo ufw allow 443/tcp   # HTTPS
   sudo ufw enable
   ```

4. **Keep Secrets Safe**
   - Never commit `.env` to version control
   - Use secret managers in cloud environments
   - Rotate API keys regularly

5. **Regular Updates**
   ```bash
   pip install --upgrade -r requirements.txt
   docker-compose pull  # For Docker deployments
   ```

6. **Limit Admin Access**
   - Consider IP whitelisting for `/admin.html`
   - Use strong authentication
   - Monitor admin panel access logs

### Nginx Security Headers

Add to your nginx.conf:

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

---

## Monitoring and Maintenance

### Health Checks

The application includes a health check endpoint:

```bash
curl http://localhost:8000/api/ask/status
```

Expected response:
```json
{
  "enabled": true,
  "message": "enabled"
}
```

### Logging

**Docker:**
```bash
docker-compose logs -f app
```

**systemd:**
```bash
sudo journalctl -u assessment -f
tail -f /var/log/assessment/access.log
tail -f /var/log/assessment/error.log
```

### Log Rotation

Create `/etc/logrotate.d/assessment`:

```
/var/log/assessment/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
    sharedscripts
    postrotate
        systemctl reload assessment
    endscript
}
```

### Backups

Backup the `.env` file securely:

```bash
# Encrypt and backup
gpg -c .env
cp .env.gpg /path/to/secure/backup/

# Restore
gpg -d .env.gpg > .env
```

### Performance Monitoring

1. **Resource Usage**
   ```bash
   docker stats  # Docker
   htop          # System-wide
   ```

2. **Application Metrics**
   - Monitor response times
   - Track error rates
   - Watch for memory leaks

---

## Troubleshooting

### Common Issues

**Issue: Container won't start**
```bash
docker-compose logs app
# Check for missing environment variables or port conflicts
```

**Issue: 502 Bad Gateway (Nginx)**
```bash
# Check if app is running
systemctl status assessment
# Check Nginx configuration
sudo nginx -t
# Check logs
tail -f /var/log/nginx/error.log
```

**Issue: Admin panel shows "Unauthorized"**
- Verify `ADMIN_PASSWORD` is set correctly
- Check browser dev console for errors
- Clear browser cache and session storage

**Issue: OpenAI API calls failing**
- Test the API key: Use admin panel test feature
- Check if you have quota/credits on OpenAI account
- Verify network connectivity to api.openai.com

**Issue: High memory usage**
- Reduce `--workers` count in Gunicorn
- Check for memory leaks with `top` or `htop`
- Restart the service periodically if needed

### Debug Mode (Development Only)

Never use in production, but for testing:

```bash
# Temporarily enable debug mode
export FLASK_ENV=development
python app.py
```

### Getting Support

- Check application logs first
- Review this documentation
- Open an issue on GitHub with logs and error messages
- Include: OS, Python version, deployment method

---

## Upgrading

### Docker Deployment

```bash
docker-compose down
git pull origin main
docker-compose up -d --build
```

### Manual Deployment

```bash
sudo systemctl stop assessment
cd /opt/assessment-gliderai
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl start assessment
```

---

## Production Checklist

Before going live:

- [ ] SSL/HTTPS enabled and working
- [ ] `ADMIN_PASSWORD` changed from default
- [ ] `OPENAI_API_KEY` configured
- [ ] Firewall configured (only 80, 443, SSH open)
- [ ] Backups configured
- [ ] Log rotation enabled
- [ ] Health checks working
- [ ] Admin panel accessible and tested
- [ ] Domain DNS configured correctly
- [ ] Security headers enabled in Nginx
- [ ] Service auto-starts on reboot
- [ ] Monitoring/alerting set up (optional but recommended)

---

For more information, see the main [README.md](README.md) file.
