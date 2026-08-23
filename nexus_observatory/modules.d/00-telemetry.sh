#!/usr/bin/env bash
# Telemetry module — collects boot metrics and system info.

module_boot() {
    local kernel arch uptime
    kernel="$(uname -r)"
    arch="$(uname -m)"
    uptime="$(uptime -p 2>/dev/null || echo 'unknown')"
    printf '    %stelemetry%s  kernel=%s arch=%s uptime=%s\n' \
        "$C_CYAN" "$C_RESET" "$kernel" "$arch" "$uptime"
}
