#!/usr/bin/env bash
# Prints one line per file and check that hits: <path> <TAB> <check> <TAB> <convention file> <TAB> <hits>.
# Run from the project root. A hit is a candidate, not a proven break: the skill reads the file to confirm it.
# A text or comment check looks for letters outside English, such as Arabic: English text needs reading.

set -u
shopt -s nullglob

# check <name> <convention> <pattern> <glob> <multiline:0|1> <dirs...>
check() {
    local name=$1 convention=$2 pattern=$3 glob=$4 multiline=$5
    shift 5
    local dirs=()
    for dir in "$@"; do [ -e "$dir" ] && dirs+=("$dir"); done
    [ ${#dirs[@]} -eq 0 ] && return
    local flags=-rcHP
    [ "$multiline" = 1 ] && flags=-rcHPz
    grep $flags --include="$glob" -e "$pattern" "${dirs[@]}" 2>/dev/null \
        | awk -F: -v n="$name" -v c="$convention" '$NF > 0 { path = $0; sub(/:[0-9]+$/, "", path); print path "\t" n "\t" c "\t" $NF }'
}

CONTROLLERS=(app/Http/Controllers Modules/*/app/Http/Controllers)
REQUESTS=(app/Http/Requests Modules/*/app/Http/Requests)
SERVICES=(app/Services Modules/*/app/Services)
MODELS=(app/Models Modules/*/app/Models)
ENUMS=(app/Enums Modules/*/app/Enums)
POLICIES=(app/Policies Modules/*/app/Policies)
VIEWS=(resources/views Modules/*/resources/views)
ROUTES=(routes Modules/*/routes)
APP=(app Modules/*/app)

# folders.md: every file in an old folder of its table, a Form Request outside an area folder, and an exception outside app/Exceptions
OLD_FOLDERS=($(grep -oP '^\| `\Kapp/[^`]+(?=` \|)' .claude/rules/laravel/folders.md 2>/dev/null))
[ ${#OLD_FOLDERS[@]} -gt 0 ] && check old-folder folders.md '^<\?php' '*.php' 0 "${OLD_FOLDERS[@]}"
for request in app/Http/Requests/*.php; do
    printf '%s\trequest-outside-area\tfolders.md\t1\n' "$request"
done
for exception in $(grep -rlP 'class \w+ extends \w*Exception\b' "${APP[@]}" 2>/dev/null | grep -v '/Exceptions/'); do
    printf '%s\texception-outside-folder\tfolders.md\t1\n' "$exception"
done

# naming.md: a file whose name holds a word its own glossary says to avoid ("live search" matches LiveSearch, live_search,
# live-search). Each glossary holds for its own context only: the core's for the core, a module's for that module. A word
# that is itself a term of the same glossary is skipped, and so is one marked "(alone)", which only reading can judge.
avoided_words() {
    local glossary=$1
    local terms
    terms=$(grep -oP '^\*\*\K[^*]+(?=\*\*:)' "$glossary" | tr -d ' ' | tr 'A-Z' 'a-z')
    grep -h '^_Avoid_:' "$glossary" | sed 's/^_Avoid_: *//' | tr ',' '\n' | grep -v '(' | tr -d ' ' | tr 'A-Z' 'a-z' | sort -u \
        | grep -vxF -f <(printf '%s\n' "$terms")
}
named_with() {
    local term=$1
    shift
    find "$@" -type f 2>/dev/null \
        | awk -v term="$term" '{ name = $0; sub(/.*\//, "", name); name = tolower(name); gsub(/[-_ .]/, "", name); if (index(name, term)) print $0 "\tavoided-word:" term "\tnaming.md\t1" }'
}
for glossary in GLOSSARY.md docs/GLOSSARY.md; do
    [ -f "$glossary" ] || continue
    for term in $(avoided_words "$glossary"); do
        named_with "$term" app resources/views resources/js routes lang
    done
done
for glossary in Modules/*/GLOSSARY.md Modules/*/docs/GLOSSARY.md; do
    module=${glossary%%/docs/GLOSSARY.md}
    module=${module%%/GLOSSARY.md}
    for term in $(avoided_words "$glossary"); do
        named_with "$term" "$module/app" "$module/resources" "$module/routes" "$module/lang"
    done
done

# comments.md: a comment not in English, commented-out code, an empty //, a TODO with no issue, and a comment over 3 lines
COMMENTED=(app routes bootstrap/app.php config Modules/*/app Modules/*/routes)
OUR_JS=(resources/js resources/css Modules/*/resources/assets)
NOT_ENGLISH='(?=\p{L})[^\x00-\x7F]'
check comment-not-english comments.md "^\\s*(//|\\*|/\\*|#)(?!\\[).*$NOT_ENGLISH" '*.php' 0 "${COMMENTED[@]}"
check comment-not-english comments.md "^\\s*(//|\\*|/\\*).*$NOT_ENGLISH" '*.js' 0 "${OUR_JS[@]}"
check comment-not-english comments.md "\\{\\{--(?:(?!--\\}\\}).)*$NOT_ENGLISH" '*.blade.php' 0 "${VIEWS[@]}"
check commented-out-code comments.md '^\s*//\s*(\$\w+.*;|return\b.*;|[\w\\]+(::|->)\w+\(.*\);|\$this->.*;|[\w\\]+::class,?)\s*$' '*.php' 0 "${COMMENTED[@]}"
check empty-comment comments.md '^\s*//\s*$' '*.php' 0 "${COMMENTED[@]}"
check todo-without-issue comments.md '\b(TODO|FIXME)\b(?!\(#\d+\))' '*.php' 0 "${COMMENTED[@]}"
find "${COMMENTED[@]}" "${OUR_JS[@]}" -type f \( -name '*.php' -o -name '*.js' \) 2>/dev/null | while read -r file; do
    awk -v file="$file" '
        function flush() { if (run > 3) long++; run = 0 }
        /^[ \t]*\/\// { run++; next }
        { flush() }
        /^[ \t]*\/\*\*/ { doc = 1; text = 0 }
        doc && /^[ \t]*\*[ \t]+[^@ \t]/ { text++ }
        doc && /\*\// { doc = 0; if (text > 3) long++ }
        END { flush(); if (long) print file "\tlong-comment\tcomments.md\t" long }
    ' "$file"
done

# naming.md: a middleware alias, config file or command name that is not in Laravel's form
check alias-not-dotted naming.md "^\s*'[a-z.]*[-_A-Z][\w.-]*'\s*=>\s*[\\\\\w]+::class" '*.php' 0 bootstrap/app.php
check command-not-kebab naming.md "\\\$signature\s*=\s*'[^ ']*[_A-Z]" '*.php' 0 app/Console Modules/*/app/Console
check route-name-not-kebab naming.md "->name\('[^']*[_A-Z]" '*.php' 0 "${ROUTES[@]}"
for config in config/*_*.php Modules/*/config/*_*.php; do
    printf '%s\tconfig-not-kebab\tnaming.md\t1\n' "$config"
done

# controllers.md
check validates-inline controllers.md '\$request->validate\(|Validator::make\(' '*.php' 0 "${CONTROLLERS[@]}"
check transaction-or-try controllers.md 'DB::(beginTransaction|transaction)\(|\btry\s*\{' '*.php' 0 "${CONTROLLERS[@]}"
check builds-json controllers.md 'response\(\)->json\(' '*.php' 0 "${CONTROLLERS[@]}"
check queries-in-controller controllers.md '\b[A-Z]\w+::(where|query|create|find|findOrFail|all|whereIn|updateOrCreate)\(' '*.php' 0 "${CONTROLLERS[@]}"
check passes-whole-request controllers.md '\$request->(all|input|get)\(' '*.php' 0 "${CONTROLLERS[@]}"

# policies.md
check names-a-permission policies.md "authorize\('[a-z]+-[a-z-]+'" '*.php' 0 "${CONTROLLERS[@]}" app/Livewire Modules/*/app/Livewire
check names-a-role policies.md 'hasRole\(|hasAnyRole\(' '*.php' 0 app/Http app/Policies app/Services app/Livewire Modules/*/app
check deny-with-text policies.md 'Response::deny\(' '*.php' 0 "${POLICIES[@]}"

# errors.md
check abort-with-text errors.md "abort(_if|_unless)?\([^)]*,\s*['\"]" '*.php' 0 "${APP[@]}"

# logging.md: a message that is not fixed, and an exception logged as text
check log-message-not-fixed logging.md "Log::\w+\(\s*('[^']*'\s*\.|\"[^\"]*\\$)" '*.php' 0 "${APP[@]}" "${ROUTES[@]}"
check exception-as-text logging.md 'getTraceAsString\(|=>\s*\$\w+->getMessage\(\)' '*.php' 0 "${APP[@]}"

# form-requests.md
check authorize-not-true form-requests.md 'function authorize\(\)[^{]*\{\s*return (?!true;)' '*.php' 1 "${REQUESTS[@]}"
check closure-in-rules form-requests.md 'function \(\$attr\w*|fn \(\$attr\w*' '*.php' 0 "${REQUESTS[@]}"
check locale-loop form-requests.md 'getSupportedLocales|foreach \(\[.ar.,\s*.en.\]' '*.php' 0 "${REQUESTS[@]}"

# services.md
check service-knows-http services.md '\bauth\(\)|\bAuth::|\brequest\(\)|\bsession\(\)' '*.php' 0 "${SERVICES[@]}"
check static-service services.md 'public static function' '*.php' 0 "${SERVICES[@]}"
for client in $(grep -rlP 'Http::' "${APP[@]}" 2>/dev/null); do
    grep -q 'timeout(' "$client" || printf '%s\thttp-without-timeout\tservices.md\t1\n' "$client"
done

# config.md
check env-outside-config config.md '\benv\(' '*.php' 0 "${APP[@]}" "${ROUTES[@]}" "${VIEWS[@]}"

# models.md
check casts-property models.md 'protected \$casts\b' '*.php' 0 "${MODELS[@]}"
check old-scope models.md 'function scope[A-Z]' '*.php' 0 "${MODELS[@]}"
check guarded-empty models.md '\$guarded\s*=\s*\[\]' '*.php' 0 "${MODELS[@]}"
check events-in-model models.md 'function booted\(|static::(creating|created|updating|updated|saving|saved|deleting|deleted)\(' '*.php' 0 "${MODELS[@]}"
check untyped-relation models.md 'function \w+\(\)\s*\{\s*return \$this->(belongsTo|hasMany|hasOne|belongsToMany|morph\w+)\(' '*.php' 1 "${MODELS[@]}"

# enums.md
check upper-case-cases enums.md 'case [A-Z][A-Z0-9_]+\s*=' '*.php' 0 "${ENUMS[@]}"
check get-label enums.md 'function getLabel\(' '*.php' 0 "${ENUMS[@]}"
for enum in $(grep -rlP '^enum \w+' "${ENUMS[@]}" 2>/dev/null); do
    grep -q 'HasLabel' "$enum" || printf '%s\tno-has-label\tenums.md\t1\n' "$enum"
done

# texts.md
check text-in-php texts.md "['\"][^'\"]*$NOT_ENGLISH" '*.php' 0 "${APP[@]}" routes config
check text-in-view texts.md ">[^<{@]*$NOT_ENGLISH" '*.blade.php' 0 "${VIEWS[@]}"
check text-in-js texts.md "['\"\`][^'\"\`]*$NOT_ENGLISH" '*.js' 0 "${OUR_JS[@]}"

# blade.md
check php-in-view blade.md '@php' '*.blade.php' 0 "${VIEWS[@]}"
check inline-script blade.md '<script(?![^>]*\bsrc=)[^>]*>' '*.blade.php' 0 "${VIEWS[@]}"
check inline-style-or-event blade.md 'style="|\bon(click|change|submit|input|keyup)="' '*.blade.php' 0 "${VIEWS[@]}"
check raw-output blade.md '\{!!' '*.blade.php' 0 "${VIEWS[@]}"
check query-in-view blade.md '\b[A-Z]\w+::(where|query|find|all|count)\(' '*.blade.php' 0 "${VIEWS[@]}"
check asset-with-hand-written-version blade.md 'asset\([^)]*\)\s*\}\}\s*\?v' '*.blade.php' 0 "${VIEWS[@]}"
find "${OUR_JS[@]}" -type f \( -name '*.js' -o -name '*.css' \) 2>/dev/null | grep -P '/[^/]*[A-Z_][^/]*\.(js|css)$' | grep -v '\.min\.' \
    | while read -r file; do printf '%s\tasset-name-not-kebab\tblade.md\t1\n' "$file"; done

# routes.md
check route-closure routes.md 'Route::\w+\([^;]*function\s*\(' '*.php' 0 "${ROUTES[@]}"
check can-middleware routes.md 'can:' '*.php' 0 "${ROUTES[@]}"

# cache.md
check cache-forever-or-tags cache.md 'rememberForever\(|Cache::(tags|forever)\(' '*.php' 0 "${APP[@]}"

# excel.md
check export-from-collection excel.md 'implements[^{]*FromCollection' '*.php' 0 app/Exports Modules/*/app/Exports
check writes-in-import excel.md '\b[A-Z]\w+::(create|insert|updateOrCreate|firstOrCreate)\(|new [A-Z]\w+\(\s*\[' '*.php' 0 app/Imports Modules/*/app/Imports
for import in $(grep -rlP 'implements[^{]*To(Model|Collection|Array)' app/Imports Modules/*/app/Imports 2>/dev/null); do
    grep -q 'WithValidation' "$import" || printf '%s\timport-without-validation\texcel.md\t1\n' "$import"
done

# notifications.md
check not-queued notifications.md 'class \w+ extends (Mailable|Notification)\b(?![^{]*ShouldQueue)' '*.php' 0 app/Mail app/Notifications Modules/*/app

# jobs.md: a queued job that does not state $tries, $backoff and $timeout, or has no failed()
for job in $(grep -rlP 'implements[^{]*ShouldQueue' app/Jobs Modules/*/app/Jobs 2>/dev/null); do
    missing=0
    for part in '\$tries' '\$backoff' '\$timeout' 'function failed('; do grep -q "$part" "$job" || missing=$((missing + 1)); done
    if [ $missing -gt 0 ]; then printf '%s\tno-retries\tjobs.md\t%s\n' "$job" "$missing"; fi
done

# The project's own checks, written with the same check function (see CHECKS.md)
if [ -f docs/agents/refactor-checks.sh ]; then
    source docs/agents/refactor-checks.sh
fi
