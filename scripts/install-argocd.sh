#!/usr/bin/env bash
set -euo pipefail

ARGOCD_NAMESPACE="argocd"
ARGOCD_VERSION="v2.12.0"

echo "Installing ArgoCD ${ARGOCD_VERSION}..."

kubectl create namespace "$ARGOCD_NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

kubectl apply -n "$ARGOCD_NAMESPACE" \
  -f "https://raw.githubusercontent.com/argoproj/argo-cd/${ARGOCD_VERSION}/manifests/install.yaml"

echo "Waiting for ArgoCD server to be ready..."
kubectl rollout status deployment/argocd-server -n "$ARGOCD_NAMESPACE" --timeout=300s

# Patch ArgoCD server to use NodePort for local access
kubectl patch svc argocd-server -n "$ARGOCD_NAMESPACE" \
  -p '{"spec": {"type": "NodePort", "ports": [{"port": 443, "targetPort": 8080, "nodePort": 30443}]}}'

echo "ArgoCD installed successfully."
echo ""
echo "Get initial admin password:"
echo "  kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d"
echo ""
echo "Access ArgoCD UI at: https://localhost:30443"