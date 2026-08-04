#!/usr/bin/env bash
# Re-copy the local ccu plugin into Claude Code's plugin cache.
# `claude plugin update` skips re-copying while the version number is
# unchanged, so a refresh is uninstall + install from the local marketplace.
set -euo pipefail

claude plugin uninstall ccu@ccu >/dev/null 2>&1 || true
claude plugin install ccu@ccu

echo "Refreshed ccu@ccu — start a new Claude Code session to pick up changes."
