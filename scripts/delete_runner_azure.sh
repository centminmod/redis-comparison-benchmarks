#!/bin/bash
set -euo pipefail

################################################################################
# delete_runner_azure.sh
#
# Deletes the Azure VM that was used as a self-hosted GitHub Actions runner.
################################################################################

# 1. Usage: delete_runner_azure.sh <VM_NAME>
# 2. Required environment variables:
#    - AZURE_CREDENTIALS    : JSON string for Azure Service Principal.
#    - AZURE_RESOURCE_GROUP : Name of the Azure Resource Group.
################################################################################

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <VM_NAME>"
  exit 1
fi

VM_NAME="$1"

# Validate secrets
for var in AZURE_CREDENTIALS AZURE_RESOURCE_GROUP; do
  if [[ -z "${!var:-}" ]]; then
    echo "ERROR: $var is not set. Aborting."
    exit 1
  fi
done

# 1. Log in to Azure via Service Principal
echo "🔐 Logging into Azure CLI..."
echo "${AZURE_CREDENTIALS}" > azure_credentials.json
az login --service-principal --json-auth azure_credentials.json > /dev/null

# 2. Delete the VM (asynchronously)
echo "🗑️  Deleting Azure VM: ${VM_NAME}"
az vm delete \
  --resource-group "${AZURE_RESOURCE_GROUP}" \
  --name "${VM_NAME}" \
  --yes \
  --no-wait

echo "✅ Delete request sent for VM: ${VM_NAME}."