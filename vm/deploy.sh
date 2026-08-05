#!/usr/bin/env bash
set -euo pipefail

APP_DIR=/opt/customer-churn-model-serving
cd "$APP_DIR"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
[ -f model/customer_churn_model.joblib ] || python training/generate_data.py
[ -f model/customer_churn_model.joblib ] || python training/train_model.py
python training/validate_model.py
sudo cp vm/customer-churn-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now customer-churn-api
