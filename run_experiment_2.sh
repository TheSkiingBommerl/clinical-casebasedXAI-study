#!/usr/bin/env bash

# Ensure the .venv contains the latest packages
uv sync

# Activate the environment
source .venv/bin/activate

# Set this environment variable to bypass the login.
# Valid suffixes are _0_0 up to _0_7
export CF_BYPASS_LOGIN=participant_0_1

streamlit run \
    website/decision_support_tool/app.py
