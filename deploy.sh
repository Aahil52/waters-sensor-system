#!/bin/bash

set -e  # Exit on any error

# Configuration
REPO_URL="https://github.com/Aahil52/sensor-system.git"
VENV_DIR=".venv"
SERVICE_FILE="sensor-system-sampler.service"

log() {
    echo "[INFO] $1"
}

if systemctl is-active --quiet $SERVICE_FILE; then
    log "Service is running. Stopping it for update..."
    sudo systemctl stop "$SERVICE_FILE"
else
    log "Service is not running."
fi

if [ ! -d "$VENV_DIR" ]; then
    log "Virtual environment not found. Creating..."
    python3 -m venv "$VENV_DIR"
else
    log "Virtual environment already exists."
fi

log "Installing/updating Python dependencies..."
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r requirements.txt

if [ ! -f ".env" ]; then
    log "Environment file (.env) not found."
    log "Please create one from the template:"
    log "  cp .env.example .env"
    exit 1
else
    log "Environment file found."
fi

log "Installing systemd service file..."
sudo cp "$SERVICE_FILE" /etc/systemd/system/

log "Reloading systemd..."
sudo systemctl daemon-reload

log "Enabling and restarting service..."
sudo systemctl enable "$SERVICE_FILE"
sudo systemctl restart "$SERVICE_FILE"

log "Deployment complete! Showing service status:"
echo "--------------------------------------------"
sudo systemctl status "$SERVICE_FILE" --no-pager
echo "--------------------------------------------"

log "Service deployed and running."
log "You can check the logs using: journalctl -u $SERVICE_FILE -f"