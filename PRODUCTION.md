# Production Deployment Guide

## Server Requirements

- Ubuntu 20.04 LTS or later
- Python 3.8 or later
- PostgreSQL 12 or later
- Nginx
- Let's Encrypt for SSL

## Installation Steps

1. Install system dependencies:
```bash
sudo apt update
sudo apt install python3-venv python3-dev postgresql postgresql-contrib nginx certbot python3-certbot-nginx
```

2. Configure PostgreSQL:
```bash
sudo -u postgres psql
CREATE DATABASE your_db_name;
CREATE USER your_db_user WITH PASSWORD 'your_db_password';
ALTER ROLE your_db_user SET client_encoding TO 'utf8';
ALTER ROLE your_db_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE your_db_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE your_db_name TO your_db_user;
\q
```

3. Configure Nginx:
```bash
sudo nano /etc/nginx/sites-available/djangogramm
```

Add the following configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /path/to/your/djangogramm;
    }

    location /media/ {
        root /path/to/your/djangogramm;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

4. Enable the site and get SSL certificate:
```bash
sudo ln -s /etc/nginx/sites-available/djangogramm /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

5. Configure Gunicorn:

The project includes pre-configured Gunicorn service files in the `systemd` directory:

- `systemd/gunicorn.service` - Gunicorn service configuration
- `systemd/gunicorn.socket` - Gunicorn socket configuration

Copy these files to systemd:
```bash
sudo cp systemd/gunicorn.service /etc/systemd/system/
sudo cp systemd/gunicorn.socket /etc/systemd/system/
```

6. Start and enable Gunicorn:
```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
```

## Security Considerations

1. Keep your .env file secure and never commit it to version control
2. Regularly update your system and dependencies
3. Use strong passwords for all services

4. Configure firewall:
```bash
# Deny all incoming connections by default
sudo ufw default deny incoming

# Allow all outgoing connections
sudo ufw default allow outgoing

# Allow SSH (port 22)
sudo ufw allow ssh

# Allow HTTP (port 80)
sudo ufw allow http

# Allow HTTPS (port 443)
sudo ufw allow https

# Enable firewall
sudo ufw --force enable

# Check status
sudo ufw status
```

The firewall configuration is also included in the `install_prod.sh` script and will be automatically set up during installation.

## Monitoring

1. Set up log rotation:
```bash
sudo nano /etc/logrotate.d/djangogramm
```

Add the following configuration:
```
/path/to/your/djangogramm/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 your_user www-data
    sharedscripts
    postrotate
        systemctl reload gunicorn
    endscript
}
```

2. Monitor system resources:
```bash
sudo apt install htop
```

## Logging Configuration

### 1. Django Logging

Add the following configuration to your `settings/prod.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django/django.log',
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'logs/django/error.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### 2. Gunicorn Logging

Update your `systemd/gunicorn.service`:

```ini
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=your_user
Group=www-data
WorkingDirectory=/path/to/your/djangogramm
ExecStart=/path/to/your/djangogramm/venv/bin/gunicorn \
    --access-logfile logs/gunicorn/access.log \
    --error-logfile logs/gunicorn/error.log \
    --log-level info \
    --workers 3 \
    --bind unix:/run/gunicorn.sock \
    djangogramm.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 3. Nginx Logging

Update your Nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    access_log /path/to/your/djangogramm/logs/nginx/access.log;
    error_log /path/to/your/djangogramm/logs/nginx/error.log;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /path/to/your/djangogramm;
    }

    location /media/ {
        root /path/to/your/djangogramm;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

### 4. Log Rotation

The project uses logrotate for automatic log rotation. Configuration is automatically set up during installation in `/etc/logrotate.d/djangogramm`:

```
/path/to/your/djangogramm/logs/*/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 your_user www-data
    sharedscripts
    postrotate
        systemctl reload gunicorn
    endscript
}
```

### 5. Monitoring Logs

1. Django logs:
```bash
# General logs
tail -f logs/django/django.log

# Error logs
tail -f logs/django/error.log
```

2. Gunicorn logs:
```bash
# Access logs
tail -f logs/gunicorn/access.log

# Error logs
tail -f logs/gunicorn/error.log

# Systemd logs
sudo journalctl -u gunicorn
```

3. Nginx logs:
```bash
# Access logs
tail -f logs/nginx/access.log

# Error logs
tail -f logs/nginx/error.log

# System logs
sudo tail -f /var/log/nginx/error.log
```

### 6. Log Analysis

For log analysis, you can use tools like:

1. `grep` for basic filtering:
```bash
# Find all errors
grep "ERROR" logs/django/error.log

# Find specific IP addresses
grep "192.168.1.1" logs/nginx/access.log
```

2. `awk` for more complex analysis:
```bash
# Count requests by status code
awk '{print $9}' logs/nginx/access.log | sort | uniq -c

# Find slow requests
awk '$NF > 1 {print $0}' logs/nginx/access.log
```

3. `goaccess` for real-time web log analysis:
```bash
# Install goaccess
sudo apt install goaccess

# Analyze Nginx logs
goaccess logs/nginx/access.log
```

## Environment Variables

Make sure to set the following environment variables in your `.env` file:

1. Database settings:
```
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=127.0.0.1
DB_PORT=5432
```

2. Domain settings:
```
DOMAIN_NAME=your-domain.com
HOST_NAME=www.your-domain.com
```

3. SSL settings:
```
SSL_CERT_PATH=/etc/letsencrypt/live/your-domain.com/fullchain.pem
SSL_KEY_PATH=/etc/letsencrypt/live/your-domain.com/privkey.pem
```

4. Service settings:
```
CLOUDINARY_URL=your_cloudinary_url
MAILJET_API_KEY=your_mailjet_api_key
MAILJET_SECRET_KEY=your_mailjet_secret_key
```

## Troubleshooting

1. Check Nginx logs:
```bash
sudo tail -f /var/log/nginx/error.log
```

2. Check Gunicorn logs:
```bash
sudo journalctl -u gunicorn
```

3. Check application logs:
```bash
tail -f /path/to/your/djangogramm/logs/django.log
```

4. Common issues:
   - Permission denied: Check file permissions and ownership
   - 502 Bad Gateway: Check if Gunicorn is running
   - SSL issues: Check certificate paths and permissions
   - Database connection: Verify database credentials and connection
   - Firewall issues: Check if ports are open with `sudo ufw status`

## Gunicorn Socket Configuration

The project uses a socket-based configuration for Gunicorn, which provides better performance and reliability. The socket file is created at `/run/gunicorn.sock` and is managed by systemd.

To check the status of the Gunicorn socket:
```bash
sudo systemctl status gunicorn.socket
```

To restart Gunicorn:
```bash
sudo systemctl restart gunicorn
```

To view Gunicorn logs:
```bash
sudo journalctl -u gunicorn
``` 