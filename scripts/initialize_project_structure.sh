#!/bin/bash

# SKYSCOPESENTINEL Project Initialization Script
# ---------------------------------------------
# This script creates the standard directory structure for the SKYSCOPE project.
# It uses 'mkdir -p' to create parent directories as needed and to avoid errors
# if the directories already exist.

echo "Initializing SKYSCOPESENTINEL project directory structure..."

# Define base directory (current directory where the script is run from, assuming it's project root)
BASE_DIR="."

# Define project directories
DOCS_DIR="$BASE_DIR/docs"
WEBSITE_DIR="$BASE_DIR/website"
SCRIPTS_DIR="$BASE_DIR/scripts" # This script itself will be here
TOKEN_CONCEPT_DIR="$BASE_DIR/token_conceptual_design"
# Add more directories here as the project evolves, e.g.:
# SMART_CONTRACTS_DIR="$BASE_DIR/smart_contracts"
# AI_MODEL_DIR="$BASE_DIR/ai_model"
# TESTS_DIR="$BASE_DIR/tests"

# Create the directories
mkdir -p "$DOCS_DIR"
mkdir -p "$WEBSITE_DIR"
mkdir -p "$SCRIPTS_DIR"
mkdir -p "$TOKEN_CONCEPT_DIR"
# mkdir -p "$SMART_CONTRACTS_DIR"
# mkdir -p "$AI_MODEL_DIR"
# mkdir -p "$TESTS_DIR"

echo ""
echo "Project directory structure created/ensured:"
echo "  - $DOCS_DIR"
echo "  - $WEBSITE_DIR"
echo "  - $SCRIPTS_DIR"
echo "  - $TOKEN_CONCEPT_DIR"
# echo "  - $SMART_CONTRACTS_DIR (Example, currently commented out)"
# echo "  - $AI_MODEL_DIR (Example, currently commented out)"
# echo "  - $TESTS_DIR (Example, currently commented out)"
echo ""
echo "Initialization complete."
echo "You can add more directories to this script as your project grows."
