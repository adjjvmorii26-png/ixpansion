#!/usr/bin/env bash
# ============================================================================
#  Nexus Observatory Boot System
#  Entry point for orchestrating observatory services and modules.
#
#  Usage:
#    ./nexus_boot.sh boot          Start all modules (default)
#    ./nexus_boot.sh stop          Signal running instance to shut down
#    ./nexus_boot.sh status        Show current state
#    ./nexus_boot.sh doctor        Run diagnostics
#    ./nexus_boot.sh --dry-run     Preview without executing
#    ./nexus_boot.sh -v            Verbose output
# ============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
readonly NEXUS_VERSION="0.3.0"
readonly NEXUS_NAME="Nexus Observatory"
readonly NEXUS_LOCK_FILE="/tmp/nexus-observatory.lock"
readonly NEXUS_PID_FILE="/tmp/nexus-observatory.pid"
readonly NEXUS_LOG_FILE="${TMPDIR:-/tmp}/nexus-observatory-boot.log"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export NEXUS_OBSERVATORY_HOME="$SCRIPT_DIR"
readonly MODULES_DIR="$SCRIPT_DIR/modules.d"

# ---------------------------------------------------------------------------
# CLI state
# ---------------------------------------------------------------------------
DRY_RUN=false
VERBOSE=false
SUBCOMMAND="boot"

# ---------------------------------------------------------------------------
# Colors & formatting
# ---------------------------------------------------------------------------
if [[ -t 1 ]] && [[ "${TERM:-}" != "dumb" ]]; then
    readonly C_RESET=$'\e[0m'
    readonly C_BOLD=$'\e[1m'
    readonly C_DIM=$'\e[2m'
    readonly C_RED=$'\e[31m'
    readonly C_GREEN=$'\e[32m'
    readonly C_YELLOW=$'\e[33m'
    readonly C_BLUE=$'\e[34m'
    readonly C_MAGENTA=$'\e[35m'
    readonly C_CYAN=$'\e[36m'
    readonly C_WHITE=$'\e[37m'
else
    readonly C_RESET="" C_BOLD="" C_DIM="" C_RED="" C_GREEN="" \
              C_YELLOW="" C_BLUE="" C_MAGENTA="" C_CYAN="" C_WHITE=""
fi

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
_log() {
    local level="$1" color="$2"; shift 2
    local timestamp
    timestamp="$(date '+%Y-%m-%dT%H:%M:%S%z')"
    printf '%s[%s]%s %s%s%s %s\n' \
        "$C_DIM" "$timestamp" "$C_RESET" \
        "$color$C_BOLD" "$level" "$C_RESET" \
        "$*"
    # Also append to log file (without colors)
    printf '[%s] [%s] %s\n' "$timestamp" "$level" "$*" >> "$NEXUS_LOG_FILE" 2>/dev/null || true
}

log_info()    { _log "INFO" "$C_BLUE" "$@"; }
log_ok()      { _log " OK " "$C_GREEN" "$@"; }
log_warn()    { _log "WARN" "$C_YELLOW" "$@"; }
log_error()   { _log "FAIL" "$C_RED" "$@"; }
log_debug() {
    if $VERBOSE; then _log "DBUG" "$C_DIM" "$@"; fi
}
log_module()  { _log "BOOT" "$C_MAGENTA" "$@"; }

# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
print_banner() {
    cat <<'BANNER'

         ___   ___  ______ _____ __  __ ____   ___________
        / _ \ / _ \ | ___ \_   _|  \/  |  _ \ |__  /  ___|
       / /_\ \/_\ \| |/ /  || | | |\/| | |_) |  / /\___ \
      |  _  |  _  || |\ \  | | | |  | |  _ <  / /_ ___) |
      |_| |_|_| |_||_| \_\ |_| |_|  |_|_| \_\/____|____/

BANNER
    printf '  %s%s v%s%s\n\n' "$C_CYAN" "$NEXUS_NAME" "$NEXUS_VERSION" "$C_RESET"
}

# ---------------------------------------------------------------------------
# Constellation boot animation
# ---------------------------------------------------------------------------
constellation() {
    if ! [[ -t 1 ]]; then return; fi
    local frames=(
        "     *           "
        "    * *    *     "
        "   *   *  * *    "
        "  *  ✦  *   *  ✦ "
        "   *   *  * *    "
        "    * *    *     "
    )
    printf '%s' "$C_DIM"
    for frame in "${frames[@]}"; do
        printf '\r  %s' "$frame"
        sleep 0.08
    done
    printf '\r%s' "$C_RESET"
}

# ---------------------------------------------------------------------------
# Dependency checks
# ---------------------------------------------------------------------------
require() {
    if ! command -v "$1" &>/dev/null; then
        log_error "required command not found: $1"
        return 1
    fi
    log_debug "dependency satisfied: $1"
}

check_dependencies() {
    log_info "checking dependencies..."
    local missing=0
    for dep in bash date; do
        if ! require "$dep"; then
            missing=$((missing + 1))
        fi
    done
    if ((missing > 0)); then
        log_error "$missing dependency(ies) missing"
        return 1
    fi
    log_ok "all dependencies present"
}

# ---------------------------------------------------------------------------
# Process lock
# ---
acquire_lock() {
    if [[ -f "$NEXUS_LOCK_FILE" ]]; then
        local old_pid
        old_pid="$(cat "$NEXUS_LOCK_FILE")"
        if kill -0 "$old_pid" 2>/dev/null; then
            log_error "another instance is already running (PID: $old_pid)"
            exit 1
        fi
        log_warn "removing stale lock file (PID: $old_pid)"
        rm -f "$NEXUS_LOCK_FILE"
    fi
    echo $$ > "$NEXUS_LOCK_FILE"
    log_debug "lock acquired (PID: $$)"
}

release_lock() {
    rm -f "$NEXUS_LOCK_FILE" 2>/dev/null || true
    log_debug "lock released"
}

# ---------------------------------------------------------------------------
# Signal handling
# ---
SHUTDOWN_REQUESTED=false

on_signal() {
    local signal_name="$1"
    log_warn "received SIG${signal_name}, initiating graceful shutdown..."
    SHUTDOWN_REQUESTED=true
    release_lock
    log_info "shutdown complete"
    exit 0
}

trap 'on_signal INT'  INT
trap 'on_signal TERM' TERM
trap 'release_lock'    EXIT

# ---------------------------------------------------------------------------
# Module discovery & loading
# ---
discover_modules() {
    local modules=()
    if [[ -d "$MODULES_DIR" ]]; then
        for f in "$MODULES_DIR"/*.sh; do
            [[ -f "$f" ]] && modules+=("$f")
        done
    fi
    printf '%s\n' "${modules[@]:-}"
}

load_module() {
    local module_path="$1"
    local module_name
    module_name="$(basename "$module_path" .sh)"

    log_module "loading module: $module_name"

    if $DRY_RUN; then
        log_debug "(dry-run) would source: $module_path"
        return 0
    fi

    # Source in a subshell to isolate side effects
    if ! (
        export MODULE_PATH="$module_path"
        export MODULE_NAME="$module_name"
        # shellcheck disable=SC1090
        source "$module_path"
        if declare -f module_boot >/dev/null 2>&1; then
            module_boot
        else
            log_warn "module '$module_name' has no boot() function, skipping"
        fi
    ) 2>&1; then
        log_error "module '$module_name' failed to load"
        return 1
    fi
    log_ok "module '$module_name' loaded"
}

boot_modules() {
    local start_time end_time duration
    start_time="$(date +%s%3N)"

    local module_list
    mapfile -t module_list < <(discover_modules)

    if [[ ${#module_list[@]} -eq 0 ]] || [[ -z "${module_list[0]}" ]]; then
        log_warn "no modules found in $MODULES_DIR"
        log_info "drop .sh files into $MODULES_DIR to extend the boot sequence"
        return 0
    fi

    local loaded=0 failed=0 total=${#module_list[@]}
    for module_path in "${module_list[@]}"; do
        constellation &
        local anim_pid=$!
        if load_module "$module_path"; then
            loaded=$((loaded + 1))
        else
            failed=$((failed + 1))
        fi
        kill "$anim_pid" 2>/dev/null && wait "$anim_pid" 2>/dev/null || true
        if $SHUTDOWN_REQUESTED; then break; fi
    done

    end_time="$(date +%s%3N)"
    duration=$((end_time - start_time))

    printf '\n'
    log_info "boot summary: ${loaded}/${total} modules ok, ${failed} failed, ${duration}ms"
    if ((failed > 0)); then
        return 1
    fi
}

# ---------------------------------------------------------------------------
# Health checks
# ---
check_disk_space() {
    local min_pct=90
    local usage
    usage="$(df / | awk 'NR==2 {print $5}' | tr -d '%')"
    if ((usage >= min_pct)); then
        log_error "disk usage at ${usage}% (threshold: ${min_pct}%)"
        return 1
    fi
    log_ok "disk usage: ${usage}%"
}

check_memory() {
    if command -v free &>/dev/null; then
        local mem_available_kb
        mem_available_kb="$(free | awk '/^Mem:/ {print $7}')"
        local mem_available_mb=$((mem_available_kb / 1024))
        if ((mem_available_mb < 128)); then
            log_error "available memory low: ${mem_available_mb}MB"
            return 1
        fi
        log_ok "memory available: ${mem_available_mb}MB"
    else
        log_debug "'free' not found, skipping memory check"
    fi
}

check_network() {
    if command -v curl &>/dev/null; then
        if curl -sf --connect-timeout 3 https://httpbin.org/status/200 &>/dev/null; then
            log_ok "network reachable"
        else
            log_warn "network unreachable or slow"
        fi
    else
        log_debug "'curl' not found, skipping network check"
    fi
}

run_health_checks() {
    log_info "running health checks..."
    check_disk_space
    check_memory
    check_network
    log_ok "health checks complete"
}

# ---------------------------------------------------------------------------
# Doctor diagnostics
# --
doctor() {
    print_banner
    log_info "running diagnostics..."

    local issues=0

    # Check dependencies
    if check_dependencies; then :; else issues=$((issues + 1)); fi

    # Check permissions
    if [[ -w "$SCRIPT_DIR" ]]; then
        log_ok "write access: $SCRIPT_DIR"
    else
        log_error "no write access to $SCRIPT_DIR"
        issues=$((issues + 1))
    fi

    # Check modules directory
    if [[ -d "$MODULES_DIR" ]]; then
        log_ok "modules dir exists: $MODULES_DIR"
    else
        log_warn "modules dir missing (will create on first boot)"
    fi

    # Health checks
    run_health_checks

    # Summary
    printf '\n'
    if ((issues == 0)); then
        printf '  %s✓ All systems nominal.%s\n\n' "$C_GREEN$C_BOLD" "$C_RESET"
    else
        printf '  %s✗ %d issue(s) detected.%s\n\n' "$C_RED$C_BOLD" "$issues" "$C_RESET"
    fi
}

# ---------------------------------------------------------------------------
# Status
# ---
show_status() {
    if [[ -f "$NEXUS_LOCK_FILE" ]]; then
        local pid
        pid="$(cat "$NEXUS_LOCK_FILE")"
        if kill -0 "$pid" 2>/dev/null; then
            printf '  %s● RUNNING%s  (PID: %s)\n' "$C_GREEN" "$C_RESET" "$pid"
        else
            printf '  %s○ STALE LOCK%s  (PID: %s, process gone)\n' "$C_YELLOW" "$C_RESET" "$pid"
        fi
    else
        printf '  %s○ STOPPED%s\n' "$C_DIM" "$C_RESET"
    fi

    # List available modules
    local count=0
    for f in "$MODULES_DIR"/*.sh; do
        if [[ -f "$f" ]]; then
            printf '    module: %s\n' "$(basename "$f" .sh)"
            count=$((count + 1))
        fi
    done
    printf '  modules: %d\n' "$count"
}

# ---------------------------------------------------------------------------
# Usage
# --
usage() {
    cat <<USAGE
${C_BOLD}${NEXUS_NAME} v${NEXUS_VERSION}${C_RESET}

Usage: $(basename "$0") [command] [options]

Commands:
  boot       Start all modules (default)
  stop       Remove lock file (signals shutdown)
  status     Show current state and loaded modules
  doctor     Run full diagnostics
  help       Show this help message

Options:
  -n, --dry-run   Preview actions without executing
  -v, --verbose   Enable debug-level logging
  -h, --help      Show this help message

Modules:
  Place executable .sh files in $MODULES_DIR/
  Each file may define a \`module_boot\` function that will
  be called during the boot sequence.
USAGE
}

# ---------------------------------------------------------------------------
# Argument parsing
# --
while [[ $# -gt 0 ]]; do
    case "$1" in
        boot|stop|status|doctor|help)
            SUBCOMMAND="$1"; shift ;;
        -n|--dry-run) DRY_RUN=true; shift ;;
        -v|--verbose) VERBOSE=true; shift ;;
        -h|--help)    usage; exit 0 ;;
        *)            log_error "unknown argument: $1"; usage; exit 1 ;;
    esac
done

# ---------------------------------------------------------------------------
# Main dispatch
# --
main() {
    case "$SUBCOMMAND" in
        help)   usage ;;
        status) show_status ;;
        doctor) doctor ;;
        stop)
            release_lock
            log_ok "stopped"
            ;;
        boot)
            print_banner
            acquire_lock
            check_dependencies
            run_health_checks
            boot_modules
            log_ok "boot complete"
            ;;
    esac
}

main "$@"
