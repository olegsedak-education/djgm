#!/bin/bash

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy example.env to .env
cp example.env .env

# Create logs directory structure
mkdir -p logs/django
mkdir -p logs/gunicorn
mkdir -p logs/nginx

# Create log files
touch logs/django/django.log
touch logs/django/error.log
touch logs/gunicorn/access.log
touch logs/gunicorn/error.log
touch logs/nginx/access.log
touch logs/nginx/error.log

# Apply migrations
python manage.py migrate

# Create superuser if not exists
if [ ! -f "superuser_created" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput
    touch superuser_created
fi

# Collect static files
python manage.py collectstatic --noinput

# Create gunicorn socket directory
sudo mkdir -p /run/gunicorn

# Copy systemd service files
sudo cp systemd/gunicorn.service /etc/systemd/system/
sudo cp systemd/gunicorn.socket /etc/systemd/system/

# Configure logrotate
sudo tee /etc/logrotate.d/djangogramm << EOF
/path/to/your/djangogramm/logs/*/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 $USER www-data
    sharedscripts
    postrotate
        systemctl reload gunicorn
    endscript
}
EOF

# Reload systemd
sudo systemctl daemon-reload

# Start and enable Gunicorn
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket

# Configure firewall
echo "Configuring firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw --force enable
echo "Firewall configured successfully"

# Set proper permissions
sudo chown -R $USER:www-data .
sudo chmod -R 755 .
sudo chmod -R 775 logs media static

echo "Production installation completed successfully!" 