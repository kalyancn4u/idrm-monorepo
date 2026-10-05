#!/bin/bash

# 1. Define arrays of target services categorized by type
DEVS_AND_DBs=(
    "elasticsearch.service"
    "snap.jenkins.jenkins.service"
    "postgresql.service"
    "postgresql@16-main.service"
    "redis-server.service"
    "docker.service"
    "docker.socket"
    "containerd.service"
    "nginx.service"
    "ssh.service"
)

MONITORING_STACK=(
    "prometheus.service"
    "prometheus-node-exporter.service"
    "grafana-server.service"
    "snap.grafana.grafana.service"
    "glances.service"
)

# Combine both categories into one master list
TARGET_SERVICES=("${DEVS_AND_DBs[@]}" "${MONITORING_STACK[@]}")

echo "=== Starting System Service Cleanup ==="
echo "This will immediately stop the services and prevent them from starting at boot."
echo ""

# 2. Loop through each service to stop and disable it
for service in "${TARGET_SERVICES[@]}"; do
    # Check if the service is currently loaded on the system to avoid unnecessary errors
    if systemctl list-unit-files "$service" >/dev/null 2>&1; then
        echo "Processing: $service"
        # --now flags both disables (boot) and stops (runtime) the service instantly
        sudo systemctl disable --now "$service"
    else
        echo "Skipping: $service (Not found/installed)"
    fi
done

# 3. Clean up left-over failed states or lingering sockets if necessary
echo ""
echo "=== Resetting Failed Systemd States ==="
sudo systemctl reset-failed

# 4. Verify everything was successfully stopped
echo ""
echo "=== Verification: Remaining Active Status ==="
echo "Checking if any targeted services are still running..."
echo "--------------------------------------------------------"
systemctl list-units --type=service --state=running | grep -E "elastic|jenkins|postgres|redis|docker|containerd|nginx|ssh|prometheus|grafana|glances" || echo "Success! All targeted services are completely stopped and out of RAM."
echo "--------------------------------------------------------"
