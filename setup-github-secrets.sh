#!/bin/bash

# Script to set up GitHub secrets for the Pharia skill build and publish workflow
# Usage: ./setup-github-secrets.sh

set -e

echo "Setting up GitHub secrets for Pharia skill workflow..."

# Source the environment variables from .env.fish
# Convert fish shell syntax to bash
source <(sed 's/set -x/export/g' blusql/.env.fish | grep -E '^export')

# Set the repository (update if needed)
REPO="2mawi2/blusql"

echo "Setting secrets for repository: $REPO"

# Function to set a secret
set_secret() {
    local name=$1
    local value=$2
    if [ -z "$value" ]; then
        echo "Warning: $name is empty, skipping..."
        return
    fi
    echo "Setting secret: $name"
    echo "$value" | gh secret set "$name" --repo="$REPO"
}

# Set all required secrets
set_secret "PHARIA_AI_TOKEN" "$PHARIA_AI_TOKEN"
set_secret "PHARIAOS_MANAGER_URL" "$PHARIAOS_MANAGER_URL"
set_secret "IMAGE_REGISTRY" "$IMAGE_REGISTRY"
set_secret "IMAGE_REPOSITORY" "$IMAGE_REPOSITORY"
set_secret "IMAGE_REGISTRY_USER" "$IMAGE_REGISTRY_USER"
set_secret "IMAGE_REGISTRY_PASSWORD" "$IMAGE_REGISTRY_PASSWORD"
set_secret "SKILL_REGISTRY" "$SKILL_REGISTRY"
set_secret "SKILL_REPOSITORY" "$SKILL_REPOSITORY"
set_secret "SKILL_REGISTRY_USER" "$SKILL_REGISTRY_USER"
set_secret "SKILL_REGISTRY_TOKEN" "$SKILL_REGISTRY_TOKEN"
set_secret "PHARIA_KERNEL_ADDRESS" "$PHARIA_KERNEL_ADDRESS"
set_secret "PHARIA_STUDIO_ADDRESS" "$PHARIA_STUDIO_ADDRESS"

echo "All secrets have been set successfully!"
echo ""
echo "You can verify the secrets by running:"
echo "gh secret list --repo=$REPO"