# Course lecture map — Customer Churn Model Serving

This repository is the hands-on project for **Sections 6–9** of the MLOps Zero to Hero course. The same Customer Churn model and FastAPI application are carried from local development through a virtual machine, Docker, Amazon ECR, and Kubernetes.

## Section 6 — Model deployment and local serving

| Lecture | Title | Repository material |
|---|---|---|
| 1 | What is Model Deployment and Model Serving? | Conceptual |
| 2 | Model Deployment vs Model Serving vs Inference | Conceptual |
| 3 | Online, Batch, Asynchronous and Streaming Inference | Conceptual |
| 4 | How a Production Prediction Request Flows | Conceptual |
| 5 | Customer Churn Model Serving Project — Setup and Repository Walkthrough | `README.md`, project tree |
| 6 | Preparing and Validating the Model Artifact | `training/`, `model/` |
| 7 | Building the FastAPI Prediction Service | `app/` |
| 8 | Running and Testing the Prediction Service Locally | `scripts/test_api.py`, `sample_requests/`, `tests/` |

## Section 7 — Virtual-machine model serving

| Lecture | Title | Repository material |
|---|---|---|
| 1 | Virtual-Machine Model Serving Architecture | Architecture in course slides |
| 2 | Creating and Connecting to an Amazon EC2 Instance | AWS Console / SSH |
| 3 | Deploying the Customer Churn Prediction Service to EC2 | `vm/deploy.sh`, `requirements.txt`, `app/`, `model/` |
| 4 | Running the Prediction API as a Linux Service with systemd | `vm/customer-churn-api.service` |
| 5 | Exposing the Prediction API with Nginx | `vm/nginx.conf` |
| 6 | Testing and Troubleshooting the Complete VM Deployment | `scripts/test_api.py`, `vm/README.md` |
| 7 | Cleaning Up the EC2 Deployment and Section Recap | AWS Console / SSH cleanup |

The `vm/user-data.sh` file is an optional reference; it is not a separate core lecture in the course.

## Section 8 — Containerising the model-serving application

| Lecture | Title | Repository material |
|---|---|---|
| 1 | Why Containers Are Used for Model Serving | Conceptual |
| 2 | Containerizing the Customer Churn Prediction Service | `Dockerfile`, `.dockerignore` |
| 3 | Building and Running the Docker Container Locally | `Dockerfile` |
| 4 | Testing the Containerized Prediction API | `scripts/test_api.py`, `sample_requests/` |
| 5 | Creating an Amazon ECR Repository | AWS Console / AWS CLI |
| 6 | Tagging and Pushing the Docker Image to Amazon ECR | AWS CLI / Docker |
| 7 | Section 8 Recap and Preparing for Kubernetes | Conceptual |

## Section 9 — Kubernetes model serving

Apply the resources in the order below. The course lab uses a local `kind` cluster named `churn-serving` and the namespace `churn-serving`.

| Lecture | Title | Repository material |
|---|---|---|
| 1 | Why Kubernetes? From One Container to a Managed Application | Conceptual |
| 2 | Kubernetes Architecture — Control Plane and Worker Nodes | Conceptual |
| 3 | Kubernetes Model Serving Architecture — Pods, Deployments and Services | Conceptual |
| 4 | Creating the Kubernetes Cluster and Namespace | `kubernetes/namespace.yaml` |
| 5 | Deploying the Customer Churn API to Kubernetes | `kubernetes/configmap.yaml`, `kubernetes/deployment.yaml`, `kubernetes/service.yaml` |
| 6 | Keeping the Prediction Service Healthy with Kubernetes Probes | `kubernetes/deployment.yaml` |
| 7 | Exposing and Testing the Prediction Service with a Kubernetes Service | `kubernetes/service.yaml`, `scripts/test_api.py` |
| 8 | Scaling the Prediction API — Replicas and Automatic Scaling | `kubernetes/hpa.yaml` |
| 9 | Updating the Model Serving Application Without Downtime | Deployment rolling-update strategy |
| 10 | Exposing the Prediction API with Kubernetes Gateway API | `kubernetes/gateway/` |
| 11 | Section 9 Conclusion — From Container to Kubernetes Platform | Recap |

### Gateway API files

- `kubernetes/gateway/gatewayclass.yaml` — Envoy Gateway's `GatewayClass`, named `eg`.
- `kubernetes/gateway/gateway.yaml` — the HTTP Gateway in `churn-serving`.
- `kubernetes/gateway/httproute.yaml` — routes requests to the application Service.

The course's local kind walkthrough uses Envoy Gateway. Other Kubernetes distributions may require a different Gateway API controller and exposure method.

## Troubleshooting references

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md). Keep the request path in mind:

```text
Gateway → HTTPRoute → Service → Pods → Logs / Events
```

## Section 10 — KServe

KServe is taught as a separate section and has its own companion repository:

[KServe — MLOps Zero to Hero](https://github.com/Ghanathey-Neelesh-Kumar/KServe-MLOps-Zero-to-Hero-series)

This repository remains focused on the custom FastAPI serving approach in Sections 6–9.
