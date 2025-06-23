#!/bin/bash

# Configuration
REPO_URL="https://github.com/Aahil52/sensor-system.git"
DEST_DIR="/opt/sensor-system"
VENV_DIR="$DEST_DIR/.venv"

# Detect install vs update
if [ -d "$DEST_DIR" ]; then
    echo "Existing installation detected. Updating..."

    # Stop services from deployed directory
    echo "Stopping services..."
    for SERVICE_FILE in $DEST_DIR/services/*.service; do
        SERVICE_NAME=$(basename "$SERVICE_FILE")
        sudo systemctl stop "$SERVICE_NAME"
    done

    # Pull latest code
    echo "Pulling latest changes..."
    cd $DEST_DIR
    sudo git pull

    # Update dependencies
    echo "Updating Python dependencies..."
    sudo $VENV_DIR/bin/pip install -r requirements.txt

else
    echo "No installation found. Performing fresh install..."

    # Clone project
    sudo git clone $REPO_URL $DEST_DIR

    # Create virtual environment
    echo "Creating virtual environment..."
    sudo python3 -m venv $VENV_DIR

    # Install dependencies
    echo "Installing Python dependencies..."
    sudo $VENV_DIR/bin/pip install -r $DEST_DIR/requirements.txt
fi

# Copy updated service files every time
echo "Installing service files..."
sudo cp $DEST_DIR/services/*.service /etc/systemd/system/

# Reload systemd
echo "Reloading systemd..."
sudo systemctl daemon-reload

# Enable and start services (always)
echo "Enabling and restarting services..."
for SERVICE_FILE in $DEST_DIR/services/*.service; do
    SERVICE_NAME=$(basename "$SERVICE_FILE")
    sudo systemctl enable "$SERVICE_NAME"
    sudo systemctl restart "$SERVICE_NAME"
done

# Show final status
echo "Deployment complete! Service status:"
for SERVICE_FILE in $DEST_DIR/services/*.service; do
    SERVICE_NAME=$(basename "$SERVICE_FILE")
    echo "Status of $SERVICE_NAME:"
    sudo systemctl status "$SERVICE_NAME" --no-pager
done
