#!/usr/bin/env bash
# The project's searches for old code that breaks its rules. The refactor-issues skill runs this file.
# Run from the project root. It prints one line per file and check that hits:
# <path> <TAB> <check> <TAB> <rule file> <TAB> <hits>
# A hit is a candidate, not a proven break: the skill reads the file to confirm it.
# Rules that only reading can check go in docs/agents/refactor-checks.md, one line each.

set -u
shopt -s nullglob

# Folders no check looks in, such as code that a tool writes. Each is a path from the project root.
# Fill it here, such as SKIP=(src/generated).
SKIP=()

# Drops the lines whose path is inside a folder of SKIP.
not_skipped() {
    local line skip
    while IFS= read -r line; do
        for skip in "${SKIP[@]}"; do
            [[ "$line" == "$skip"/* ]] && continue 2
        done
        printf '%s\n' "$line"
    done
}

# check <name> <rule file> <pattern> <glob> <multiline:0|1> <folders...>
# Finds a pattern inside files. Another script may define check first, such as the scan.sh
# of laravel-refactor-issues: then its own is used, and SKIP does not apply to it.
if ! declare -F check >/dev/null; then
    check() {
        local name=$1 rule=$2 pattern=$3 glob=$4 multiline=$5
        shift 5
        local dirs=()
        for dir in "$@"; do [ -e "$dir" ] && dirs+=("$dir"); done
        [ ${#dirs[@]} -eq 0 ] && return
        local flags=-rcHP
        [ "$multiline" = 1 ] && flags=-rcHPz
        grep $flags --include="$glob" -e "$pattern" "${dirs[@]}" 2>/dev/null \
            | awk -F: -v n="$name" -v r="$rule" '$NF > 0 { path = $0; sub(/:[0-9]+$/, "", path); print path "\t" n "\t" r "\t" $NF }' \
            | not_skipped
    }
fi

# check_path <name> <rule file> <path pattern> <folders...>
# Finds files by their path, for a rule about a file's name or folder. The pattern is a
# Perl regular expression on the whole path, such as '/[^/]*[A-Z_][^/]*\.ts$' for a name
# that is not kebab-case, or '.' for every file of an old folder.
check_path() {
    local name=$1 rule=$2 pattern=$3
    shift 3
    local dirs=()
    for dir in "$@"; do [ -e "$dir" ] && dirs+=("$dir"); done
    [ ${#dirs[@]} -eq 0 ] && return
    find "${dirs[@]}" -type f 2>/dev/null | sed 's#^\./##' | grep -P -e "$pattern" | not_skipped \
        | awk -v n="$name" -v r="$rule" '{ print $0 "\t" n "\t" r "\t1" }'
}

# One check per rule a search can find. The second field names the rule's file. For example:
# check console-log code.md 'console\.log\(' '*.ts' 0 src
# check_path not-kebab-case CONTRIBUTING.md '/[^/]*[A-Z_][^/]*\.ts$' src
# check_path old-folder code.md '.' src/utils
