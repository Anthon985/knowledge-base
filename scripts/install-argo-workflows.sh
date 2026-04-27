#!/usr/bin/env bash
set -euo pipefail

ARGO_NAMESPACE="argo"
ARGO_VERSION="v3.5.10"

echo "Installing Argo Workflows ${ARGO_VERSION}..."

kubectl create namespace "$ARGO_NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

kubectl apply -n "$ARGO_NAMESPACE" \
  -f "https://github.com/argoproj/argo-workflows/releases/download/${ARGO_VERSION}/install.yaml"

echo "Waiting for Argo Workflows controller to be ready..."
kubectl rollout status deployment/workflow-controller -n "$ARGO_NAMESPACE" --timeout=300s

# Patch Argo Server to use NodePort
kubectl patch svc argo-server -n "$ARGO_NAMESPACE" \
  -p '{"spec": {"type": "NodePort", "ports": [{"port": 2746, "targetPort": 2746, "nodePort": 30746}]}}' 2>/dev/null || true

# Create doc-processor ConfigMap in argo namespace
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: doc-processor-config
  namespace: $ARGO_NAMESPACE
data:
  MINIO_ENDPOINT: "minio.knowledge-base:9000"
  MINIO_ACCESS_KEY: "minioadmin"
  MINIO_SECRET_KEY: "minioadmin"
  MINIO_BUCKET: "documents"
  QDRANT_HOST: "qdrant.knowledge-base"
  QDRANT_PORT: "6333"
  QDRANT_COLLECTION: "document_chunks"
  ELASTICSEARCH_URL: "http://elasticsearch.knowledge-base:9200"
  ELASTICSEARCH_INDEX: "document_chunks"
  DATABASE_URL: "postgresql://postgres:postgres@postgresql.knowledge-base:5432/knowledgebase"
  EMBEDDING_MODEL: "BAAI/bge-base-zh-v1.5"
  CHUNK_SIZE: "512"
  CHUNK_OVERLAP: "100"
EOF

echo "Argo Workflows installed successfully."
echo ""
echo "Argo Workflows UI: https://localhost:30746"