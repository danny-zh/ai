---
name: k8s-troubleshooting
description: Use when troubleshooting Kubernetes issues including pod failures, networking problems, resource constraints, or debugging K8s components.
---

# Kubernetes Troubleshooting

Use this skill when diagnosing and resolving Kubernetes issues.

## Pod Issues

```bash
# Check pod status
kubectl get pods -n <namespace>

# Detailed pod info (events, conditions)
kubectl describe pod <pod-name> -n <namespace>

# View pod logs
kubectl logs <pod-name> -n <namespace>
kubectl logs <pod-name> -n <namespace> --previous  # previous container logs

# Execute into pod for debugging
kubectl exec -it <pod-name> -n <namespace> -- /bin/sh

# Check resource usage
kubectl top pods -n <namespace>
```

## Common Pod Problems

- **CrashLoopBackOff**: Check logs, verify environment variables, check resource limits
- **ImagePullBackOff**: Verify image name, check registry credentials, confirm network access
- **Pending**: Check resource availability, node selectors, taints/tolerations
- **OOMKilled**: Increase memory limits or optimize application

## Networking Issues

```bash
# Check services
kubectl get svc -A
kubectl describe svc <service-name> -n <namespace>

# Check endpoints
kubectl get endpoints <service-name> -n <namespace>

# DNS resolution test from within a pod
kubectl exec -it <pod-name> -- nslookup <service-name>.<namespace>.svc.cluster.local

# Network policy check
kubectl get networkpolicies -n <namespace>
```

## Node Issues

```bash
# Check node status
kubectl get nodes
kubectl describe node <node-name>

# Check node resources
kubectl top nodes

# Drain node for maintenance
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# Cordon node (mark unschedulable)
kubectl cordon <node-name>
```

## Debugging Commands

```bash
# Get all resources in namespace
kubectl get all -n <namespace>

# Check component health
kubectl get componentstatuses

# View events sorted by time
kubectl get events -n <namespace> --sort-by='.lastTimestamp'

# Check RBAC permissions
kubectl auth can-i <verb> <resource> -n <namespace>
```

## Resource Issues

```bash
# Check resource quotas
kubectl get resourcequotas -n <namespace>

# Check limit ranges
kubectl get limitranges -n <namespace>

# Check persistent volumes
kubectl get pv,pvc -n <namespace>
```
