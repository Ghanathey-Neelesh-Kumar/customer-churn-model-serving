#!/usr/bin/env bash
set -euxo pipefail

# Replace before use.
REPOSITORY_URL="https://github.com/<USERNAME>/customer-churn-model-serving.git"
APP_DIR="/opt/customer-churn-model-serving"

apt-get update
apt-get install -y python3 python3-venv git nginx

git clone "$REPOSITORY_URL" "$APP_DIR"
chown -R ubuntu:ubuntu "$APP_DIR"

sudo -u ubuntu bash -lc "cd '$APP_DIR' && python3 -m venv .venv && source .venv/bin/activate && python -m pip install -r requirements.txt && python training/generate_data.py && python training/train_model.py && python training/validate_model.py"

cp "$APP_DIR/vm/customer-churn-api.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now customer-churn-api

cp "$APP_DIR/vm/nginx.conf" /etc/nginx/sites-available/customer-churn-api
ln -sf /etc/nginx/sites-available/customer-churn-api /etc/nginx/sites-enabled/customer-churn-api
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx
