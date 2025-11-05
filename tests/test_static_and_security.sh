#!/usr/bin/env bash
set -e
flake8 .
bandit -r . -lll

