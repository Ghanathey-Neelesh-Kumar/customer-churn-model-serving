# Virtual-machine deployment

This folder supports the VM lectures. The example assumes Ubuntu and a repository cloned to `/opt/customer-churn-model-serving`.

## Architecture

```text
Client → port 80/Nginx → 127.0.0.1:8000/Uvicorn → FastAPI → trusted model artifact
```

## Manual outline

1. Create an Ubuntu VM.
2. Attach a least-privilege IAM role when AWS access is needed.
3. Allow SSH only from your IP.
4. Allow HTTP from the intended client network.
5. Clone the repository into `/opt/customer-churn-model-serving`.
6. Create a virtual environment and install requirements.
7. Train or securely copy the trusted model artifact.
8. Install the supplied systemd unit.
9. Install the supplied Nginx configuration.
10. Test health, readiness and prediction endpoints.

## Commands

```bash
sudo mkdir -p /opt/customer-churn-model-serving
sudo chown -R "$USER":"$USER" /opt/customer-churn-model-serving
# Clone or copy the repository here.
cd /opt/customer-churn-model-serving
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python training/generate_data.py
python training/train_model.py
python training/validate_model.py
```

Install service:

```bash
sudo cp vm/customer-churn-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now customer-churn-api
sudo systemctl status customer-churn-api
journalctl -u customer-churn-api -f
```

Install Nginx:

```bash
sudo apt-get update
sudo apt-get install -y nginx
sudo cp vm/nginx.conf /etc/nginx/sites-available/customer-churn-api
sudo ln -s /etc/nginx/sites-available/customer-churn-api /etc/nginx/sites-enabled/customer-churn-api
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

Test:

```bash
curl http://127.0.0.1/health
```

Do not expose port 8000 publicly when Nginx is the public entry point.
