#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="kb-local"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "  Knowledge Base - Local Dev Setup"
echo "========================================"

# --- 1. Check prerequisites ---
echo ""
echo "[1/5] Checking prerequisites..."

for cmd in docker kind kubectl; do
  if ! command -v "$cmd" &> /dev/null; then
    echo "ERROR: '$cmd' is not installed. Please install it first."
    exit 1
  fi
done
echo "  All prerequisites found."

# --- 2. Create Kind cluster ---
echo ""
echo "[2/5] Creating Kind cluster '$CLUSTER_NAME'..."

if kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
  echo "  Cluster '$CLUSTER_NAME' already exists, skipping."
else
  cat <<EOF | kind create cluster --name "$CLUSTER_NAME" --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    extraPortMappings:
      - containerPort: 30080
        hostPort: 30080
        protocol: TCP
      - containerPort: 30443
        hostPort: 30443
        protocol: TCP
EOF
  echo "  Cluster created."
fi

kubectl cluster-info --context "kind-${CLUSTER_NAME}"

# --- 3. Install ArgoCD ---
echo ""
echo "[3/5] Installing ArgoCD..."
bash "$SCRIPT_DIR/install-argocd.sh"

# --- 4. Install Argo Workflows ---
echo ""
echo "[4/5] Installing Argo Workflows..."
bash "$SCRIPT_DIR/install-argo-workflows.sh"

# --- 5. Build and load images ---
echo ""
echo "[5/5] Building application images..."

echo "  Building frontend..."
docker build -f "$PROJECT_DIR/docker/frontend.Dockerfile" \
  -t kb-frontend:dev "$PROJECT_DIR/apps/frontend" 2>/dev/null || echo "  (frontend build skipped - run npm install first)"

echo "  Building api-server..."
docker build -f "$PROJECT_DIR/docker/api-server.Dockerfile" \
  -t kb-api-server:dev "$PROJECT_DIR/apps/api-server" 2>/dev/null || echo "  (api-server build skipped)"

echo "  Building doc-processor..."
docker build -f "$PROJECT_DIR/docker/doc-processor.Dockerfile" \
  -t kb-doc-processor:dev "$PROJECT_DIR/apps/doc-processor" 2>/dev/null || echo "  (doc-processor build skipped)"

echo "  Loading images into Kind cluster..."
kind load docker-image kb-frontend:dev --name "$CLUSTER_NAME" 2>/dev/null || true
kind load docker-image kb-api-server:dev --name "$CLUSTER_NAME" 2>/dev/null || true
kind load docker-image kb-doc-processor:dev --name "$CLUSTER_NAME" 2>/dev/null || true

echo ""
echo "========================================"
echo "  Setup complete!"
echo ""
echo "  ArgoCD UI:   https://localhost:30443"
echo "  ArgoCD password: kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d"
echo ""
echo "  Next steps:"
echo "    1. kubectl apply -f deploy/argocd/projects/knowledge-base.yaml"
echo "    2. kubectl apply -f deploy/argocd/app-of-apps.yaml"
echo "========================================"