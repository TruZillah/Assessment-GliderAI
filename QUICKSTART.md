# Quick Reference Guide

## Quick Start

### Windows
```cmd
start.bat
```

### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

## Important URLs

- **Main Application**: http://127.0.0.1:5000
- **Admin Panel**: http://127.0.0.1:5000/admin.html

## Default Credentials

- **Admin Password**: `admin123` (⚠️ CHANGE THIS IMMEDIATELY!)

## First-Time Setup

1. Run `start.bat` (Windows) or `start.sh` (Linux/Mac)
2. Edit `.env` file with your OpenAI API key
3. Access admin panel at http://127.0.0.1:5000/admin.html
4. Change admin password
5. Configure OpenAI settings

## Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed production deployment instructions.

### Quick Docker Deploy

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values
nano .env

# Start with Docker Compose
docker-compose up -d

# Access at http://localhost:8000
```

## Admin Panel Features

✅ Configure OpenAI API key via web interface  
✅ Test API key validity  
✅ Switch between OpenAI models  
✅ View configuration status  
✅ Auto-save to .env file  

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | - | No* |
| `OPENAI_MODEL` | Model to use | `gpt-4` | No |
| `ADMIN_PASSWORD` | Admin panel password | `admin123` | **Yes** |
| `FLASK_ENV` | Environment | `development` | No |

*Required for AI assistant features

## Common Commands

### Development
```bash
# Start dev server
python app.py

# Run tests
python run_tests.py
```

### Docker
```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild
docker-compose up -d --build
```

### Production (systemd)
```bash
# Start service
sudo systemctl start assessment

# Stop service
sudo systemctl stop assessment

# View logs
sudo journalctl -u assessment -f
```

## Troubleshooting

**Admin panel shows "Unauthorized"**
- Check `ADMIN_PASSWORD` in .env
- Clear browser cache/session storage

**AI features not working**
- Set `OPENAI_API_KEY` in admin panel
- Test key using the test button
- Check OpenAI account has credits

**Port already in use**
- Change port in app.py (last line)
- Or kill process using the port

## Security Checklist

- [ ] Change `ADMIN_PASSWORD` from default
- [ ] Don't commit `.env` file
- [ ] Use HTTPS in production
- [ ] Keep dependencies updated
- [ ] Review admin panel access logs

## Getting Help

1. Check [README.md](README.md) for full documentation
2. See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment guides
3. Review application logs
4. Open issue on GitHub with details

## License

MIT License - See LICENSE file for details
