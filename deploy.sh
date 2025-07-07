#!/bin/bash

set -e  # Exit on any error

# Configuration
REPO_URL="https://github.com/Aahil52/sensor-system.git"
DEST_DIR="/opt/sensor-system"
VENV_DIR="$DEST_DIR/.venv"
SERVICE_FILE="sensor-system-sampler.service"

log() {
    echo "[INFO] $1"
}

# Detect install vs update
if [ -d "$DEST_DIR" ]; then
    log "Existing installation detected. Updating..."

    log "Stopping service..."
    sudo systemctl stop "$SERVICE_FILE" || log "Service may not have been running."

    log "Pulling latest changes..."
    cd "$DEST_DIR"
    sudo git pull

    log "Updating Python dependencies..."
    sudo "$VENV_DIR/bin/pip" install -r requirements.txt
else
    log "No installation found. Performing fresh install..."

    if [ ! -f ".env" ]; then
        log "Missing .env file!"
        log "Please create one from the template:"
        log "  cp .env.example .env"
        exit 1
    fi

    log "Cloning repository..."
    sudo git clone "$REPO_URL" "$DEST_DIR"

    log "Creating virtual environment..."
    sudo python3 -m venv "$VENV_DIR"

    log "Installing Python dependencies..."
    sudo "$VENV_DIR/bin/pip" install -r "$DEST_DIR/requirements.txt"

    log "Setting up environment variables..."
    sudo cp ".env" "$DEST_DIR/.env"
fi

log "Installing systemd service file..."
sudo cp "$DEST_DIR/$SERVICE_FILE" /etc/systemd/system/

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