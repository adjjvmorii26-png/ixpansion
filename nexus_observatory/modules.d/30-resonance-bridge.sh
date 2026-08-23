#!/usr/bin/env bash
# Resonance Bridge — surface ALEPH's cross-engine pulse in the observatory.

module_boot() {
    local home="${NEXUS_OBSERVATORY_HOME:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
    local latest="$home/telemetry/resonance.jsonl.latest"
    local color="$C_CYAN"

    if [[ ! -f "$latest" ]]; then
        printf '    %sresonance%s  silent lattice (run bridges/resonance_loom.py)\n' \
            "$C_YELLOW" "$C_RESET"
        return 0
    fi

    local signature mood chaos tick
    signature="$(sed -n 's/.*"short_signature":"\([^"]*\)".*/\1/p' "$latest" | head -1)"
    mood="$(sed -n 's/.*"mood":"\([^"]*\)".*/\1/p' "$latest" | head -1)"
    chaos="$(sed -n 's/.*"chaos":\([0-9.]*\).*/\1/p' "$latest" | head -1)"
    tick="$(sed -n 's/.*"tick":\([0-9]*\).*/\1/p' "$latest" | head -1)"

    [[ -z "$signature" ]] && { color="$C_RED"; signature="invalid"; }
    printf '    %sresonance%s  tick=%s mood=%s chaos=%s signature=%s\n' \
        "$color" "$C_RESET" "${tick:-0}" "${mood:-unknown}" \
        "${chaos:-0}" "$signature"
}
