# Troubleshooting

## Model file missing

```bash
python training/generate_data.py
python training/train_model.py
python training/validate_model.py
```

## Checksum mismatch

The model file and metadata do not belong together. Regenerate both with `training/train_model.py`. Do not bypass the check.

## API fails at startup

```bash
python training/validate_model.py
uvicorn app.main:app --log-level debug
```

## HTTP 422 from `/predict`

FastAPI rejected the input schema. Compare the request with the files in `sample_requests/`.

## Port 8000 is already in use

Run on another port:

```bash
uvicorn app.main:app --port 8001
```

## Docker container is unhealthy

```bash
docker ps
docker logs <CONTAINER_ID>
docker inspect <CONTAINER_ID>
```

## Kubernetes Pods do not start

```bash
kubectl get pods -n churn-serving
kubectl describe pod <POD> -n churn-serving
kubectl logs <POD> -n churn-serving
```

Check that the image placeholder has been replaced and the cluster can pull from the registry.

## Readiness fails

The `/ready` endpoint fails when the model did not load. Inspect application logs and model paths.

## HPA shows unknown CPU

Install and verify a Kubernetes metrics server, then confirm resource requests exist in the Deployment.

## Gateway has no address

A Gateway resource alone is not enough. A compatible Gateway controller and GatewayClass must be installed.
