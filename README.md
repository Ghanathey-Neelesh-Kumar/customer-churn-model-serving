# Customer Churn Model Serving — Zero to Production-Oriented Deployment

A complete, beginner-friendly reference project on how a trained machine-learning model becomes a prediction API and is then deployed through increasingly capable environments:

```text
Standalone model artifact
        ↓
FastAPI prediction service
        ↓
Local development
        ↓
Virtual machine deployment
        ↓
Docker container
        ↓
Amazon ECR
        ↓
Kubernetes Deployment and Service
        ↓
Health probes, scaling, updates, rollback and Gateway API
```

This repository is deliberately independent. It does not require experiments, databases, buckets, clusters, or MLflow infrastructure from an earlier course section.

---

## What students will learn

By completing the repository in order, students will learn to:

1. Generate a reproducible customer-churn dataset.
2. Train and persist a complete scikit-learn pipeline.
3. Validate a saved model before serving it.
4. Build a typed FastAPI prediction service.
5. Add health, readiness and model-information endpoints.
6. Test valid, invalid, high-risk and low-risk requests.
7. Run the service locally with Uvicorn.
8. Run the API as a Linux service with `systemd`.
9. Expose the API through Nginx.
10. Build a secure, non-root Docker image.
11. Push the image to Amazon ECR.
12. Deploy the image to Kubernetes.
13. Configure startup, readiness and liveness probes.
14. Add CPU/memory requests, limits and horizontal scaling.
15. Expose the service using Gateway API.
16. Perform rolling updates and rollbacks.

---

## Business use case

The API receives information about one customer and estimates whether that customer may leave the company.

Example request:

```json
{
  "tenure_months": 3,
  "monthly_charges": 105.0,
  "support_calls": 8,
  "contract_type": "Month-to-month",
  "internet_service": "Fiber optic",
  "payment_method": "Electronic check"
}
```

Example response:

```json
{
  "request_id": "7cc2bb42-1f0f-4782-b7cc-5648c3857afd",
  "prediction": "Customer may churn",
  "churn_probability": 0.87,
  "risk_level": "High",
  "model_name": "customer-churn-classifier",
  "model_version": "1.0.0"
}
```

The model is educational and uses synthetic data. It must not be used for real customer decisions.

---

## Repository structure

```text
customer-churn-model-serving/
├── app/                         FastAPI application
│   ├── main.py                  API creation, startup and endpoints
│   ├── schemas.py               Request and response validation
│   ├── settings.py              Environment-based configuration
│   ├── model_loader.py          Safe model loading and metadata checks
│   └── predictor.py             Prediction and risk-level logic
├── model/                       Generated model artifact and metadata
├── training/                    Independent data generation and training
│   ├── generate_data.py
│   ├── train_model.py
│   └── validate_model.py
├── sample_requests/             Repeatable API examples
├── scripts/                     Local API tests and load generation
├── tests/                       Automated unit/API tests
├── vm/                          EC2/Linux VM deployment resources
├── docker/                      Container guidance
├── kubernetes/                  Namespace, Deployment, Service, HPA
│   └── gateway/                 Gateway API resources
├── docs/                        Lecture mapping and troubleshooting
├── Dockerfile
├── compose.yaml
├── Makefile
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .dockerignore
└── .gitignore
```

---

## Prerequisites

- Python 3.12 or 3.13
- Git
- `curl`
- Docker Desktop for the container lectures
- AWS CLI for EC2/ECR lectures
- `kubectl` and a Kubernetes cluster for Kubernetes lectures

The local FastAPI lessons require only Python.

## Clone the repository

```bash
git clone https://github.com/Ghanathey-Neelesh-Kumar/customer-churn-model-serving.git
cd customer-churn-model-serving
```

---

# Part 1 — Local project setup

## 1. Create and activate a virtual environment

### Windows Git Bash

```bash
python -m venv .venv
source .venv/Scripts/activate
```

### PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

---

## 2. Generate the educational dataset

```bash
python training/generate_data.py
```

This creates:

```text
data/customer_churn.csv
```

The generator uses a fixed random seed by default, so students can reproduce the same dataset.

---

## 3. Train the complete model pipeline

```bash
python training/train_model.py
```

The script saves:

```text
model/customer_churn_model.joblib
model/model_metadata.json
model/evaluation_metrics.json
```

The persisted object is a complete scikit-learn pipeline containing:

- numeric missing-value handling;
- numeric scaling;
- categorical missing-value handling;
- one-hot encoding;
- logistic-regression classification.

Keeping preprocessing and estimation together reduces training-serving skew.

> Security: `joblib` uses pickle-based persistence. Load model files only from trusted sources. Never load an untrusted model artifact.

---

## 4. Validate the saved model

```bash
python training/validate_model.py
```

The validation script loads the artifact, checks its prediction interface and tests high-risk and low-risk examples before the API is started.

---

# Part 2 — Run the prediction service locally

## 1. Start the API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

FastAPI automatically provides interactive OpenAPI documentation.

## 2. Check the service endpoints

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/ready
curl http://127.0.0.1:8000/model-info
```

Endpoint responsibilities:

| Endpoint | Purpose |
|---|---|
| `GET /health` | Confirms that the application process is running. |
| `GET /ready` | Confirms that the trusted model artifact is loaded. |
| `GET /model-info` | Returns model name, version, algorithm and features. |
| `POST /predict` | Validates input and returns churn inference. |

## 3. Send a high-risk request

### Git Bash/Linux/macOS

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  --data-binary @sample_requests/high_risk_customer.json
```

### PowerShell

```powershell
Invoke-RestMethod \
  -Uri http://127.0.0.1:8000/predict \
  -Method Post \
  -ContentType "application/json" \
  -InFile sample_requests/high_risk_customer.json
```

## 4. Use the reusable API test script

```bash
python scripts/test_api.py --base-url http://127.0.0.1:8000
```

Test a specific request:

```bash
python scripts/test_api.py \
  --base-url http://127.0.0.1:8000 \
  --request-file sample_requests/low_risk_customer.json
```

---

# Part 3 — Automated tests

Run all tests:

```bash
pytest -q
```

The tests verify:

- health and readiness responses;
- model metadata;
- valid prediction responses;
- invalid input rejection;
- probability range;
- stable response fields.

Run static checks:

```bash
ruff check .
```

---

# Part 4 — Configuration

Copy the example file:

```bash
cp .env.example .env
```

Available settings:

```text
APP_NAME
APP_VERSION
MODEL_PATH
MODEL_METADATA_PATH
LOG_LEVEL
HIGH_RISK_THRESHOLD
MEDIUM_RISK_THRESHOLD
```

The application reads configuration from environment variables. Secrets must never be committed.

---

# Part 5 — Virtual-machine deployment

The `vm/` directory contains:

```text
vm/
├── customer-churn-api.service   systemd unit
├── nginx.conf                   reverse-proxy example
├── deploy.sh                    manual deployment helper
├── user-data.sh                 first-boot automation template
└── README.md                    exact VM walkthrough
```

Start with:

```bash
cat vm/README.md
```

The recommended VM architecture is:

```text
Client → Security Group → Nginx → Uvicorn/FastAPI → model pipeline
```

Use an IAM role rather than storing AWS keys on the instance.

---

# Part 6 — Docker

Build the image:

```bash
docker build -t customer-churn-api:1.0.0 .
```

Run it:

```bash
docker run --rm -p 8000:8000 customer-churn-api:1.0.0
```

Test it:

```bash
curl http://127.0.0.1:8000/ready
```

The image:

- uses a slim Python base;
- installs dependencies before copying changing source code;
- runs as a non-root user;
- contains a container health check;
- starts one Uvicorn process per container;
- uses environment-based configuration.

---

# Part 7 — Push to Amazon ECR

Set values:

```bash
export AWS_REGION=eu-north-1
export AWS_ACCOUNT_ID=<YOUR_ACCOUNT_ID>
export ECR_REPOSITORY=customer-churn-api
export IMAGE_TAG=1.0.0
```

Create the repository:

```bash
aws ecr create-repository \
  --repository-name "$ECR_REPOSITORY" \
  --region "$AWS_REGION"
```

Authenticate Docker:

```bash
aws ecr get-login-password --region "$AWS_REGION" | \
  docker login \
    --username AWS \
    --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
```

Tag and push:

```bash
docker tag \
  customer-churn-api:$IMAGE_TAG \
  "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$IMAGE_TAG"

docker push \
  "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$IMAGE_TAG"
```

Do not rely only on `latest`. Use immutable tags such as semantic versions or Git commit IDs.

---

# Part 8 — Kubernetes

Edit the image in:

```text
kubernetes/deployment.yaml
```

Apply the resources:

```bash
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
```

Inspect:

```bash
kubectl get all -n churn-serving
kubectl describe deployment customer-churn-api -n churn-serving
kubectl logs deployment/customer-churn-api -n churn-serving
```

Test with port forwarding:

```bash
kubectl port-forward \
  -n churn-serving \
  service/customer-churn-api \
  8000:80
```

Then:

```bash
curl http://127.0.0.1:8000/ready
```

Apply autoscaling after a metrics server is available:

```bash
kubectl apply -f kubernetes/hpa.yaml
kubectl get hpa -n churn-serving
```

The Deployment includes:

- startup, readiness and liveness probes;
- resource requests and limits;
- a non-root security context;
- rolling-update strategy;
- graceful termination;
- two replicas.

---

# Part 9 — Rolling update and rollback

The Deployment already uses a `RollingUpdate` strategy. For the course's local kind lab, build the new image, tag it with the exact image reference used by the Deployment, and load it into kind before changing the Deployment image.

Example for a private ECR-style image reference:

```bash
docker build -t customer-churn-api:1.1.0 .
docker tag customer-churn-api:1.1.0 <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/customer-churn-api:1.1.0
kind load docker-image <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/customer-churn-api:1.1.0 --name churn-serving
```

The image reference passed to `kubectl set image` must exactly match the image tag loaded into kind. The Deployment uses `imagePullPolicy: IfNotPresent` for this local demonstration.

Update the image:

```bash
kubectl set image \
  deployment/customer-churn-api \
  api=<ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/customer-churn-api:1.1.0 \
  -n churn-serving
```

Watch the rollout:

```bash
kubectl rollout status deployment/customer-churn-api -n churn-serving
kubectl get pods -n churn-serving
```

View revision history:

```bash
kubectl rollout history deployment/customer-churn-api -n churn-serving
```

Rollback:

```bash
kubectl rollout undo deployment/customer-churn-api -n churn-serving
kubectl rollout status deployment/customer-churn-api -n churn-serving
```

---

# Part 10 — Gateway API

The course lab uses **Envoy Gateway** with the local kind cluster. Install the Gateway API standard CRDs first, then the Envoy Gateway controller.

### Install Gateway API CRDs

```bash
VERSION="v1.6.2"
kubectl apply --server-side -f "https://github.com/kubernetes-sigs/gateway-api/releases/download/${VERSION}/standard-install.yaml"
```

### Install Envoy Gateway

```bash
helm install eg oci://docker.io/envoyproxy/gateway-helm \
  --version v1.9.1 \
  -n envoy-gateway-system \
  --create-namespace

kubectl wait --timeout=5m -n envoy-gateway-system deployment/envoy-gateway --for=condition=Available
```

### Apply the Gateway resources

The repository includes the `GatewayClass` used in the course lab:

```bash
kubectl apply -f kubernetes/gateway/gatewayclass.yaml
kubectl apply -f kubernetes/gateway/gateway.yaml
kubectl apply -f kubernetes/gateway/httproute.yaml
```

Inspect the resources:

```bash
kubectl get gatewayclass
kubectl get gateway,httproute -n churn-serving
kubectl get svc -n envoy-gateway-system
```

On kind, the generated Envoy proxy Service can be tested with port-forwarding. Use the Service name shown by the previous command:

```bash
kubectl port-forward -n envoy-gateway-system service/<ENVOY-PROXY-SERVICE> 8080:80
```

In another terminal, test the route:

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/ready
python scripts/test_api.py --base-url http://127.0.0.1:8080
```

For EKS, GKE, AKS or another cluster, install a compatible Gateway API controller and adapt the GatewayClass and exposure method to that environment.

---

# Lecture mapping

The repository supports the course sequence below.

## Section 6 — Foundations and local serving

1. What is Model Deployment and Model Serving?
2. Model Deployment vs Model Serving vs Inference
3. Online, Batch, Asynchronous and Streaming Inference
4. How a Production Prediction Request Flows
5. Customer Churn Model Serving Project — Setup and Repository Walkthrough
6. Preparing and Validating the Model Artifact
7. Building the FastAPI Prediction Service
8. Running and Testing the Prediction Service Locally

## Section 7 — Virtual-machine model serving

1. Virtual-Machine Model Serving Architecture
2. Creating and Connecting to an Amazon EC2 Instance
3. Deploying the Customer Churn Prediction Service to EC2
4. Running the Prediction API as a Linux Service with systemd
5. Exposing the Prediction API with Nginx
6. Testing and Troubleshooting the Complete VM Deployment
7. Cleaning Up the EC2 Deployment and Section Recap

## Section 8 — Containerising the model-serving application

1. Why Containers Are Used for Model Serving
2. Containerizing the Customer Churn Prediction Service
3. Building and Running the Docker Container Locally
4. Testing the Containerized Prediction API
5. Creating an Amazon ECR Repository
6. Tagging and Pushing the Docker Image to Amazon ECR
7. Section 8 Recap and Preparing for Kubernetes

## Section 9 — Kubernetes model serving

1. Why Kubernetes? From One Container to a Managed Application
2. Kubernetes Architecture — Control Plane and Worker Nodes
3. Kubernetes Model Serving Architecture — Pods, Deployments and Services
4. Creating the Kubernetes Cluster and Namespace
5. Deploying the Customer Churn API to Kubernetes
6. Keeping the Prediction Service Healthy with Kubernetes Probes
7. Exposing and Testing the Prediction Service with a Kubernetes Service
8. Scaling the Prediction API — Replicas and Automatic Scaling
9. Updating the Model Serving Application Without Downtime
10. Exposing the Prediction API with Kubernetes Gateway API
11. Section 9 Conclusion — From Container to Kubernetes Platform

A more detailed instructor mapping is available in `docs/LECTURE_MAP.md`.

---

# Security notes

- Treat model files as executable-like trusted artifacts.
- Never load an untrusted `joblib` or pickle file.
- Do not commit `.env`, cloud keys, private keys or passwords.
- Use IAM roles for AWS workloads.
- Run containers as a non-root user.
- Do not expose stack traces to API clients.
- Avoid logging sensitive customer payloads.
- Validate every request.
- Pin and scan dependencies before real production use.

---

# Troubleshooting

See:

```text
docs/TROUBLESHOOTING.md
```

Common checks:

```bash
python training/validate_model.py
pytest -q
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/ready
```

---

# Cleanup

Local:

```bash
rm -rf .venv .pytest_cache .ruff_cache
```

Docker:

```bash
docker compose down
docker image rm customer-churn-api:1.0.0
```

Kubernetes:

```bash
kubectl delete namespace churn-serving
```

Cloud resources should be deleted after demonstrations to avoid charges.

---

## Educational disclaimer

This repository demonstrates engineering patterns. The dataset and predictions are synthetic and are not suitable for real retention, financial, employment, insurance, or other consequential decisions.
