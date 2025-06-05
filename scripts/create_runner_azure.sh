#!/bin/bash
set -euo pipefail

################################################################################
# create_runner_azure.sh
#
# Provisions an Ubuntu VM on Azure, installs the GitHub runner software, and
# registers it as an ephemeral runner for the specified GitHub repository.
################################################################################

# 1. Required environment variables (must be exported before running)
#    - AZURE_CREDENTIALS      : JSON string for Azure Service Principal.
#    - AZURE_RESOURCE_GROUP   : Name of the Azure Resource Group (e.g., "gha-runners-rg").
#    - AZURE_LOCATION         : Azure region (e.g., "eastus2").
#    - GITHUB_REPOSITORY      : "owner/repo" format (e.g., "alice/my-repo").
#    - PAT_GITHUB             : GitHub Personal Access Token with Actions permissions.
#
# 2. Optional environment variables
#    - VM_SIZE                : Azure VM size (default: "Standard_D8alds_v6").
#    - ADMIN_USER             : VM admin username (default: "azureuser").
################################################################################

# Validate mandatory variables
for var in AZURE_CREDENTIALS AZURE_RESOURCE_GROUP AZURE_LOCATION GITHUB_REPOSITORY PAT_GITHUB; do
  if [[ -z "${!var:-}" ]]; then
    echo "ERROR: $var is not set. Aborting."
    exit 1
  fi
done

# Set defaults if not provided
VM_SIZE="${VM_SIZE:-Standard_D8alds_v6}"
ADMIN_USER="${ADMIN_USER:-azureuser}"

# 1. Log in to Azure using Service Principal credentials
echo "🔐 Logging into Azure CLI..."
echo "${AZURE_CREDENTIALS}" > azure_credentials.json
az login --service-principal --json-auth azure_credentials.json > /dev/null

# 2. Fetch GitHub runner registration token (expires in 1 hour)
echo "⏳ Requesting GitHub runner registration token..."
REG_TOKEN=$(curl -s -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer ${PAT_GITHUB}" \
  "https://api.github.com/repos/${GITHUB_REPOSITORY}/actions/runners/registration-token" \
  | jq -r .token)

if [[ -z "$REG_TOKEN" ]]; then
  echo "ERROR: Failed to retrieve GitHub runner registration token."
  exit 1
fi
echo "✅ Received registration token."

# 3. Generate a unique VM name
TIMESTAMP=$(date +%s)
VM_NAME="gha-runner-${GITHUB_REPOSITORY//\//-}-${TIMESTAMP}"
echo "🏷️  VM Name: ${VM_NAME}"

# 4. Create a cloud-init script for first-boot configuration
cat <<'CLOUDINIT' > cloud-init-runner.sh
#!/bin/bash
set -euo pipefail

# Install prerequisites
apt-get update -y && apt-get install -y curl jq

# Download the latest GitHub runner (Linux x64)
latest_url=$(curl -s https://api.github.com/repos/actions/runner/releases/latest \
  | jq -r '.assets[] | select(.name | test("linux-x64")) | .browser_download_url')
curl -o actions-runner.tar.gz -L "${latest_url}"

# Unpack into the admin user's home directory
mkdir -p /home/${ADMIN_USER}/actions-runner
tar xzf actions-runner.tar.gz -C /home/${ADMIN_USER}/actions-runner
cd /home/${ADMIN_USER}/actions-runner

# Configure the runner (unattended, ephemeral)
./config.sh --unattended \
  --url https://github.com/${GITHUB_REPOSITORY} \
  --token ${REG_TOKEN} \
  --labels azure-runner \
  --name $(hostname) \
  --ephemeral

# Set correct ownership so the service runs under the admin user
chown -R ${ADMIN_USER}:${ADMIN_USER} /home/${ADMIN_USER}/actions-runner

# Install as a systemd service and start it
./svc.sh install
./svc.sh start
CLOUDINIT

# 5. Provision the VM with Azure CLI, passing the cloud-init script
echo "🚀 Creating Azure VM: ${VM_NAME}"
az vm create \
  --resource-group "${AZURE_RESOURCE_GROUP}" \
  --name "${VM_NAME}" \
  --image Canonical:ubuntu-24_04-lts:server:latest \
  --size "${VM_SIZE}" \
  --admin-username "${ADMIN_USER}" \
  --generate-ssh-keys \
  --custom-data cloud-init-runner.sh \
  --location "${AZURE_LOCATION}" \
  --no-wait \
  -o json > create_vm_output.json

# 6. Extract the VM’s resource ID (for potential debugging)
VM_ID=$(jq -r '.id' create_vm_output.json)
echo "🔖 VM provisioning initiated. VM ID: ${VM_ID}"

# 7. Export the VM name so the workflow can capture it
echo "VM_NAME=${VM_NAME}" >> provision_output.env

echo "✅ Provision script complete. The runner should appear in GitHub shortly."