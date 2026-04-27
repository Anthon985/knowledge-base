#!/usr/bin/env bash
set -euo pipefail

echo "Seeding test data..."

# Wait for MinIO to be ready
echo "Waiting for MinIO..."
kubectl wait --for=condition=ready pod -l app=minio -n knowledge-base --timeout=120s

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
kubectl wait --for=condition=ready pod -l app=postgresql -n knowledge-base --timeout=120s

# Create a test document via port-forwarding
echo "Creating test document..."
kubectl port-forward svc/api-server 8000:8000 -n knowledge-base &
PF_PID=$!
sleep 3

# Upload a test file
echo "Hello, this is a test document for the knowledge base system." > /tmp/test-doc.txt
curl -s -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@/tmp/test-doc.txt" || echo "Upload skipped (API not ready)"
rm -f /tmp/test-doc.txt

kill $PF_PID 2>/dev/null || true

echo "Seed data complete."