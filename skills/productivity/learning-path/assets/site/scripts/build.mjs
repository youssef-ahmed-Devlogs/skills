import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { course, sections } from "../course.mjs";
import { validateCourse } from "./validate.mjs";

const OUT_DIR = fileURLToPath(new URL("../", import.meta.url));
validateCourse(course, sections);

const LEVEL_META = {
  junior: { key: "junior", cls: "lvl-junior", en: "Junior", ar: "جينيور" },
  mid: { key: "mid", cls: "lvl-mid", en: "Mid-Level", ar: "ميد ليفل" },
  senior: { key: "senior", cls: "lvl-senior", en: "Senior", ar: "سينيور" }
};

const resolvedSections = sections.map((section) => ({
  ...section,
  levelMeta: LEVEL_META[section.level],
  lessons: section.lessons.map((lesson) => {
    const level = lesson.level ?? section.level;
    return { ...lesson, level, levelMeta: LEVEL_META[level], section };
  })
}));

const allLessons = resolvedSections.flatMap((s) => s.lessons);
const counts = {
  all: allLessons.length,
  junior: allLessons.filter((l) => l.level === "junior").length,
  mid: allLessons.filter((l) => l.level === "mid").length,
  senior: allLessons.filter((l) => l.level === "senior").length
};

console.log(
  `Loaded ${resolvedSections.length} sections and ${allLessons.length} lessons (Junior: ${counts.junior}, Mid: ${counts.mid}, Senior: ${counts.senior}).`
);

// ---------------------------------------------------------------------------
// 3. Escaping, Bidi Isolation & Prose Formatting
// ---------------------------------------------------------------------------
function esc(str = "") {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
function fixArabicBidi(html) {
  // Split on HTML tags and HTML entities so neither is ever modified
  const parts = html.split(/(<[^>]+>|&[a-zA-Z0-9#]+;)/g);
  // Match multi-word English technical phrases (including --flags, numbers, slashes) as one LTR run
  const enRun = /(?:--)?[A-Za-z][A-Za-z0-9_.:\-/()]*?(?:(?:\s+(?:&amp;|&|\+|\/|\->|&rarr;)?\s*|\s+)(?:--)?[A-Za-z0-9][A-Za-z0-9_.:\-/()]*)*(?![A-Za-z0-9])/g;
  // Wait: handle '&amp;' inside split cleanly by running over segments outside tags:
  let out = "";
  let inCode = false;
  for (let i = 0; i < parts.length; i++) {
    const seg = parts[i];
    if (!seg) continue;
    if (seg.startsWith("<")) {
      if (/^<code\b/i.test(seg)) inCode = true;
      else if (/^<\/code>/i.test(seg)) inCode = false;
      out += seg;
    } else if (/^&[a-zA-Z0-9#]+;$/.test(seg)) {
      out += seg;
    } else if (inCode) {
      out += seg;
    } else {
      out += seg.replace(
        /(?:--)?[A-Za-z][A-Za-z0-9_.:\-/+]*(?:\s+(?:--)?[A-Za-z0-9][A-Za-z0-9_.:\-/+]*)*(?=\s|$|[،.؟!)\]:؛,])/g,
        (m) => `<bdi dir="ltr">${m}</bdi>`
      );
    }
  }
  // Merge adjacent <bdi dir="ltr">A</bdi> &amp; <bdi dir="ltr">B</bdi> into one LTR span
  return out.replace(
    /<bdi dir="ltr">([^<]+)<\/bdi>(\s*(?:&amp;|&rarr;|\/|\+)\s*)<bdi dir="ltr">([^<]+)<\/bdi>/g,
    '<bdi dir="ltr">$1$2$3</bdi>'
  );
}


function formatProse(text, isArabic = false) {
  const html = esc(text).replace(/`([^`]+)`/g, "<code>$1</code>");
  return isArabic ? fixArabicBidi(html) : html;
}

function formatArLabel(text) {
  return fixArabicBidi(esc(text));
}

function renderLevelBadge(levelMeta, extraCls = "") {
  const cls = `lvl-badge ${levelMeta.cls}${extraCls ? " " + extraCls : ""}`;
  return `<span class="${cls}"><span data-lang="en">${levelMeta.en}</span><span data-lang="ar">${levelMeta.ar}</span></span>`;
}

// ---------------------------------------------------------------------------
// 4. Syntax Highlighter (JS / TS / SQL)
// ---------------------------------------------------------------------------
const KEYWORDS = new Set([
  "import", "from", "export", "const", "let", "var", "function", "async",
  "await", "return", "if", "else", "for", "while", "try", "catch", "finally",
  "throw", "new", "typeof", "of", "in", "true", "false", "null", "undefined",
  "type", "interface", "as", "never", "unknown", "number", "string", "boolean",
  "SELECT", "FROM", "WHERE", "ORDER", "BY", "LIMIT", "UPDATE", "SET", "AND",
  "INSERT", "INTO", "BEGIN", "COMMIT", "ROLLBACK", "VALUES", "ALTER", "TABLE",
  "ADD", "COLUMN", "DROP", "RENAME", "TO", "CREATE", "INDEX", "CONCURRENTLY",
  ...(course.keywords ?? []),
  "FOR", "SKIP", "LOCKED", "RETURNING", "TEXT", "NULL", "PRIMARY", "KEY"
]);

const TYPES = new Set([
  "Promise", "Error", "Map", "Array", "Buffer", "StringDecoder", "EventEmitter",
  "AbortController", "AbortSignal", "Worker", "AsyncLocalStorage", "Math",
  "JSON", "Result", "Product", "EditorGuard", "Pool", "Agent", "CircuitBreaker",
  ...(course.types ?? []),
  "MySqlContainer", "Number"
]);

function highlightCode(source) {
  const tokenRe =
    /(\/\/[^\n]*|--[^\n]*|\/\*[\s\S]*?\*\/|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`|@\w+|\b\d+(?:_\d+)*\b|\b[A-Za-z_$][\w$]*\b)/g;

  let out = "";
  let last = 0;
  let m;

  while ((m = tokenRe.exec(source)) !== null) {
    out += esc(source.slice(last, m.index));
    const tok = m[0];
    const nextChar = source[tokenRe.lastIndex] || "";

    if (tok.startsWith("//") || tok.startsWith("--") || tok.startsWith("/*")) {
      out += `<span class="tok-com">${esc(tok)}</span>`;
    } else if (tok.startsWith('"') || tok.startsWith("'") || tok.startsWith("`")) {
      out += `<span class="tok-str">${esc(tok)}</span>`;
    } else if (tok.startsWith("@")) {
      out += `<span class="tok-fn">${esc(tok)}</span>`;
    } else if (/^\d/.test(tok)) {
      out += `<span class="tok-num">${esc(tok)}</span>`;
    } else if (KEYWORDS.has(tok)) {
      out += `<span class="tok-kw">${esc(tok)}</span>`;
    } else if (TYPES.has(tok)) {
      out += `<span class="tok-type">${esc(tok)}</span>`;
    } else if (nextChar === "(") {
      out += `<span class="tok-fn">${esc(tok)}</span>`;
    } else {
      out += esc(tok);
    }

    last = tokenRe.lastIndex;
  }

  out += esc(source.slice(last));
  return out;
}

// ---------------------------------------------------------------------------
// 5. Mermaid-Style Inline SVG Sequence Diagram Generator
// ---------------------------------------------------------------------------
function wrapLabel(text, maxChars = 32) {
  const words = String(text).split(/\s+/);
  const lines = [];
  let line = "";
  for (const w of words) {
    if (!line) line = w;
    else if ((line + " " + w).length <= maxChars) line += " " + w;
    else {
      lines.push(line);
      line = w;
    }
  }
  if (line) lines.push(line);
  return lines.slice(0, 3);
}

function renderNoteBox(cx, y, text, boxClass = "d-note-box", textClass = "d-note-text") {
  const lines = wrapLabel(text, 32);
  const maxLen = Math.max(...lines.map((l) => l.length));
  const w = Math.min(266, Math.max(134, maxLen * 6.9 + 26));
  const h = lines.length === 1 ? 32 : lines.length === 2 ? 46 : 60;
  let x = cx - w / 2;
  if (x < 10) x = 10;
  if (x + w > 610) x = 610 - w;
  const realCx = x + w / 2;

  const tspans =
    lines.length === 1
      ? `<text x="${realCx}" y="${y + h / 2}" class="${textClass}">${esc(lines[0])}</text>`
      : lines
          .map((ln, idx) => `<text x="${realCx}" y="${y + 15 + idx * 16}" class="${textClass}">${esc(ln)}</text>`)
          .join("");

  return {
    svg: `<rect x="${x.toFixed(1)}" y="${y}" width="${w.toFixed(1)}" height="${h}" rx="2.5" class="${boxClass}" />${tspans}`,
    height: h
  };
}

function renderSequenceDiagram(lesson, caseIdx) {
  const c = lesson.cases[caseIdx];
  const markerId = `arr-${lesson.id}-${caseIdx}`;
  const actors = lesson.actors.map((a) => ({
    name: a.name,
    sub: Array.isArray(a.description) ? a.description[caseIdx] : a.description
  }));

  const xs = [104, 310, 516];
  const boxW = 172;
  const boxH = 48;
  const obs = c.observations.map((o) => o.en);
  const outcomeBoxClass = caseIdx === 0 ? "d-state-green" : "d-state-red";

  let curY = 78;
  const parts = [];

  const n1 = renderNoteBox(xs[0], curY, obs[0] || c.name.en, "d-note-box", "d-note-text");
  parts.push(n1.svg);
  curY += n1.height + 24;

  parts.push(
    `<text x="${(xs[0] + xs[1]) / 2}" y="${curY - 8}" class="d-msg-text">${esc(actors[1].sub)}</text>`,
    `<line x1="${xs[0]}" y1="${curY}" x2="${xs[1] - 4}" y2="${curY}" class="d-arrow" marker-end="url(#${markerId})" />`
  );
  curY += 16;

  const n2 = renderNoteBox(xs[1], curY, obs[1] || "", "d-note-box", "d-note-text");
  parts.push(n2.svg);
  curY += n2.height + 24;

  parts.push(
    `<text x="${(xs[1] + xs[2]) / 2}" y="${curY - 8}" class="d-msg-text">${esc(actors[2].sub)}</text>`,
    `<line x1="${xs[1]}" y1="${curY}" x2="${xs[2] - 4}" y2="${curY}" class="d-arrow-dashed" marker-end="url(#${markerId})" />`
  );
  curY += 16;

  const n3 = renderNoteBox(xs[2], curY, obs[2] || "", outcomeBoxClass, "d-actor-text");
  parts.push(n3.svg);
  curY += n3.height + 24;

  const bottomY = curY;
  const totalH = bottomY + boxH + 16;

  const renderActorRects = (y) =>
    actors
      .map((a, i) => {
        const x = xs[i] - boxW / 2;
        return `
          <rect x="${x}" y="${y}" width="${boxW}" height="${boxH}" rx="3" class="d-actor-box" />
          <text x="${xs[i]}" y="${y + 18}" class="d-actor-text" font-weight="600">${esc(a.name)}</text>
          <text x="${xs[i]}" y="${y + 35}" class="d-msg-text" font-size="10.5">${esc(a.sub)}</text>
        `;
      })
      .join("");

  const lifelines = xs
    .map((x) => `<line x1="${x}" y1="${14 + boxH}" x2="${x}" y2="${bottomY}" class="d-lifeline" />`)
    .join("");

  return `
    <div class="diagram-wrap" dir="ltr">
      <svg viewBox="0 0 620 ${totalH}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${esc(lesson.title.en)} — ${esc(c.name.en)}">
        <defs>
          <marker id="${markerId}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
            <path d="M 0 1 L 10 5 L 0 9 z" class="d-arrowhead" />
          </marker>
        </defs>
        ${renderActorRects(14)}
        ${lifelines}
        ${parts.join("\n")}
        ${renderActorRects(bottomY)}
      </svg>
    </div>
  `;
}
let navCounter = 0;
const navGroupsData = [
  {
    level: null,
    title: { en: "Roadmap", ar: "خريطة المسار" },
    items: [
      { href: "index.html", num: "00", level: null, en: "Curriculum Overview", ar: "نظرة عامة على المنهج" }
    ]
  },
  ...resolvedSections.map((sec) => ({
    level: sec.levelMeta,
    title: { en: esc(sec.title.en), ar: formatArLabel(sec.title.ar) },
    items: sec.lessons.map((l) => {
      navCounter += 1;
      return {
        href: `${l.id}.html`,
        num: String(navCounter).padStart(2, "0"),
        level: l.levelMeta,
        en: esc(l.title.en),
        ar: formatArLabel(l.title.ar)
      };
    })
  }))
];

const milestones = allLessons.filter((lesson) => lesson.milestone);

const searchIndexData = [
  {
    page: "index.html",
    hash: "",
    en: `${course.title.en} — ${resolvedSections.length} Sections, ${counts.all} Lessons`,
    ar: `${course.title.ar} — ${resolvedSections.length} فصلاً و ${counts.all} درساً`,
    groupEn: "Roadmap",
    groupAr: "خريطة المسار"
  }
];

resolvedSections.forEach((sec) => {
  sec.lessons.forEach((l) => {
    searchIndexData.push({
      page: `${l.id}.html`,
      hash: "",
      en: `[${l.levelMeta.en}] ${l.title.en} (${l.term.en})`,
      ar: `[${l.levelMeta.ar}] ${l.title.ar} (${l.term.ar})`,
      groupEn: sec.title.en,
      groupAr: sec.title.ar
    });
    l.cases.forEach((c, idx) => {
      searchIndexData.push({
        page: `${l.id}.html`,
        hash: `#case-${idx + 1}`,
        en: `${l.title.en} — Case ${idx + 1}: ${c.name.en}`,
        ar: `${l.title.ar} — الحالة ${idx + 1}: ${c.name.ar}`,
        groupEn: sec.title.en,
        groupAr: sec.title.ar
      });
    });
  });
});

const appJsContent = `/* ==========================================================================
   Learning Path — Shared Interactive Shell
   Junior -> Mid -> Senior Badges · EN/AR · Light/Dark
   ========================================================================== */

(function () {
  "use strict";

  const escapeHtml = ${esc.toString()};
  const brand = ${JSON.stringify({en:esc(course.brand.en),ar:formatArLabel(course.brand.ar),title:esc(course.title.en),journeyEn:esc(course.journey.en),journeyAr:formatArLabel(course.journey.ar)})};
  const NAV_GROUPS = ${JSON.stringify(navGroupsData, null, 2)};

  const SEARCH_INDEX = ${JSON.stringify(searchIndexData, null, 2)};

  const ICONS = {
    search: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>',
    globe: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>',
    system: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="14" x="2" y="3" rx="2"/><line x1="8" x2="16" y1="21" y2="21"/><line x1="12" x2="12" y1="17" y2="21"/></svg>',
    sun: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>',
    moon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>',
    menu: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="18" y2="18"/></svg>',
    copy: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>',
    check: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>',
    toc: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" x2="21" y1="6" y2="6"/><line x1="3" x2="15" y1="12" y2="12"/><line x1="3" x2="18" y1="18" y2="18"/></svg>'
  };

  const STORAGE_THEME = "learning-path-theme-pref";
  const STORAGE_LOCALE = "learning-path-locale";
  const systemDarkQuery = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;

  function getSavedThemePref() {
    const saved = localStorage.getItem(STORAGE_THEME);
    if (saved === "light" || saved === "dark" || saved === "system") return saved;
    return "system";
  }

  function resolveTheme(pref) {
    if (pref === "light" || pref === "dark") return pref;
    return systemDarkQuery && systemDarkQuery.matches ? "dark" : "light";
  }

  function getSavedLocale() {
    return localStorage.getItem(STORAGE_LOCALE) === "ar" ? "ar" : "en";
  }

  function applyThemePref(pref) {
    localStorage.setItem(STORAGE_THEME, pref);
    const resolved = resolveTheme(pref);
    document.documentElement.setAttribute("data-theme", resolved);
    document.documentElement.setAttribute("data-theme-pref", pref);

    const trigger = document.getElementById("theme-toggle-btn");
    if (trigger) {
      trigger.innerHTML = pref === "light" ? ICONS.sun : pref === "dark" ? ICONS.moon : ICONS.system;
    }
    document.querySelectorAll(".theme-menu-item").forEach((item) => {
      item.setAttribute("data-active", item.dataset.themeChoice === pref ? "true" : "false");
    });
  }

  if (systemDarkQuery) {
    systemDarkQuery.addEventListener("change", () => {
      if (getSavedThemePref() === "system") applyThemePref("system");
    });
  }

  function applyLocale(locale) {
    document.documentElement.setAttribute("data-locale", locale);
    document.documentElement.setAttribute("lang", locale);
    document.documentElement.setAttribute("dir", locale === "ar" ? "rtl" : "ltr");
    localStorage.setItem(STORAGE_LOCALE, locale);

    document.querySelectorAll("[data-set-locale]").forEach((btn) => {
      btn.setAttribute("data-active", btn.dataset.setLocale === locale ? "true" : "false");
    });

    const searchInput = document.getElementById("search-modal-input");
    if (searchInput) {
      searchInput.placeholder =
        locale === "ar"
          ? "ابحث في الـ ${counts.all} درساً (Junior -> Senior)..."
          : "Search all ${counts.all} lessons (Junior -> Senior)...";
    }
  }

  applyThemePref(getSavedThemePref());
  applyLocale(getSavedLocale());

  function getCurrentFile() {
    const path = window.location.pathname;
    const file = path.substring(path.lastIndexOf("/") + 1);
    return file || "index.html";
  }

  function renderNavbar() {
    const mount = document.getElementById("site-navbar");
    if (!mount) return;

    mount.innerHTML = \`
      <header class="navbar">
        <div class="navbar-inner">
          <div class="navbar-left">
            <button class="mobile-menu-btn" id="mobile-menu-btn" aria-label="Toggle navigation">
              \${ICONS.menu}
            </button>
            <a href="index.html" class="brand-logo" title="\${brand.title}">
              <span data-lang="en">\${brand.en}</span>
              <span data-lang="ar">\${brand.ar}</span>
              <span class="brand-chevrons">&gt;&gt;</span>
            </a>
            <span class="version-badge" title="Learning Journey">
              <span data-lang="en">\${brand.journeyEn}</span>
              <span data-lang="ar">\${brand.journeyAr}</span>
            </span>
          </div>

          <button class="search-trigger" id="search-trigger-btn" type="button">
            <span class="search-trigger-left">
              \${ICONS.search}
              <span data-lang="en">Search ${counts.all} lessons...</span>
              <span data-lang="ar">ابحث في ${counts.all} درساً...</span>
            </span>
            <span class="search-kbd">Ctrl K</span>
          </button>

          <div class="navbar-right">
            <div class="theme-menu-wrap" id="lang-menu-wrap">
              <button
                type="button"
                class="icon-btn"
                id="lang-toggle-btn"
                aria-label="Change language"
                aria-haspopup="menu"
                aria-expanded="false"
                title="Language"
              >
                \${ICONS.globe}
              </button>
              <div class="theme-menu" id="lang-menu" role="menu">
                <button type="button" class="theme-menu-item" role="menuitem" data-set-locale="en">
                  <span class="theme-menu-item-left">
                    <span class="lang-code-tag">EN</span>
                    <span>English</span>
                  </span>
                  <span class="theme-menu-check">\${ICONS.check}</span>
                </button>
                <button type="button" class="theme-menu-item" role="menuitem" data-set-locale="ar">
                  <span class="theme-menu-item-left">
                    <span class="lang-code-tag">AR</span>
                    <span style="font-family:var(--font-arabic)">العربية</span>
                  </span>
                  <span class="theme-menu-check">\${ICONS.check}</span>
                </button>
              </div>
            </div>

            <div class="theme-menu-wrap" id="theme-menu-wrap">
              <button
                type="button"
                class="icon-btn"
                id="theme-toggle-btn"
                aria-label="Change theme preference"
                aria-haspopup="menu"
                aria-expanded="false"
              >
                \${ICONS.system}
              </button>
              <div class="theme-menu" id="theme-menu" role="menu">
                <button type="button" class="theme-menu-item" role="menuitem" data-theme-choice="system">
                  <span class="theme-menu-item-left">
                    \${ICONS.system}
                    <span data-lang="en">System</span>
                    <span data-lang="ar">النظام</span>
                  </span>
                  <span class="theme-menu-check">\${ICONS.check}</span>
                </button>
                <button type="button" class="theme-menu-item" role="menuitem" data-theme-choice="light">
                  <span class="theme-menu-item-left">
                    \${ICONS.sun}
                    <span data-lang="en">Light</span>
                    <span data-lang="ar">نهاري</span>
                  </span>
                  <span class="theme-menu-check">\${ICONS.check}</span>
                </button>
                <button type="button" class="theme-menu-item" role="menuitem" data-theme-choice="dark">
                  <span class="theme-menu-item-left">
                    \${ICONS.moon}
                    <span data-lang="en">Dark</span>
                    <span data-lang="ar">ليلي</span>
                  </span>
                  <span class="theme-menu-check">\${ICONS.check}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>
    \`;

    const langWrap = document.getElementById("lang-menu-wrap");
    const langBtn = document.getElementById("lang-toggle-btn");
    const langMenu = document.getElementById("lang-menu");
    const themeWrap = document.getElementById("theme-menu-wrap");
    const themeBtn = document.getElementById("theme-toggle-btn");
    const themeMenu = document.getElementById("theme-menu");

    function setMenuOpen(menu, btn, open) {
      if (!menu || !btn) return;
      menu.classList.toggle("open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    }

    if (langBtn && langMenu) {
      langBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        const willOpen = !langMenu.classList.contains("open");
        setMenuOpen(themeMenu, themeBtn, false);
        setMenuOpen(langMenu, langBtn, willOpen);
      });

      langMenu.querySelectorAll("[data-set-locale]").forEach((item) => {
        item.addEventListener("click", () => {
          applyLocale(item.dataset.setLocale);
          setMenuOpen(langMenu, langBtn, false);
        });
      });
    }

    if (themeBtn && themeMenu) {
      themeBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        const willOpen = !themeMenu.classList.contains("open");
        setMenuOpen(langMenu, langBtn, false);
        setMenuOpen(themeMenu, themeBtn, willOpen);
      });

      themeMenu.querySelectorAll(".theme-menu-item").forEach((item) => {
        item.addEventListener("click", () => {
          applyThemePref(item.dataset.themeChoice);
          setMenuOpen(themeMenu, themeBtn, false);
        });
      });
    }

    document.addEventListener("click", (e) => {
      if (langWrap && !langWrap.contains(e.target)) setMenuOpen(langMenu, langBtn, false);
      if (themeWrap && !themeWrap.contains(e.target)) setMenuOpen(themeMenu, themeBtn, false);
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        setMenuOpen(langMenu, langBtn, false);
        setMenuOpen(themeMenu, themeBtn, false);
      }
    });

    const searchBtn = document.getElementById("search-trigger-btn");
    if (searchBtn) searchBtn.addEventListener("click", openSearchModal);

    const menuBtn = document.getElementById("mobile-menu-btn");
    if (menuBtn) menuBtn.addEventListener("click", toggleMobileSidebar);

    applyThemePref(getSavedThemePref());
    applyLocale(getSavedLocale());
  }

  function renderSidebar() {
    const mount = document.getElementById("site-sidebar");
    if (!mount) return;
    const current = getCurrentFile();

    mount.innerHTML = NAV_GROUPS.map((group) => {
      const groupBadge = group.level
        ? \`<span class="lvl-badge \${group.level.cls} lvl-badge-xs"><span data-lang="en">\${group.level.en}</span><span data-lang="ar">\${group.level.ar}</span></span>\`
        : "";

      const itemsHtml = group.items
        .map((item) => {
          const isActive = item.href === current ? " active" : "";
          const numSpan = item.num === "00" ? "" : \`<span class="sidebar-num">\${item.num}</span>\`;
          return \`
            <li>
              <a class="sidebar-link\${isActive}" href="\${item.href}">
                \${numSpan}
                <span data-lang="en">\${item.en}</span>
                <span data-lang="ar">\${item.ar}</span>
              </a>
            </li>
          \`;
        })
        .join("");

      return \`
        <div class="sidebar-group">
          <div class="sidebar-group-head">
            <h4 class="sidebar-group-title">
              <span data-lang="en">\${group.title.en}</span>
              <span data-lang="ar">\${group.title.ar}</span>
            </h4>
            \${groupBadge}
          </div>
          <ul class="sidebar-list">\${itemsHtml}</ul>
        </div>
      \`;
    }).join("");

    const activeLink = mount.querySelector(".sidebar-link.active");
    if (activeLink) {
      activeLink.scrollIntoView({ block: "center", behavior: "instant" });
    }

    let overlay = document.getElementById("sidebar-overlay");
    if (!overlay) {
      overlay = document.createElement("div");
      overlay.id = "sidebar-overlay";
      overlay.className = "sidebar-overlay";
      overlay.addEventListener("click", closeMobileSidebar);
      document.body.appendChild(overlay);
    }
  }

  function toggleMobileSidebar() {
    const sb = document.getElementById("site-sidebar");
    const ov = document.getElementById("sidebar-overlay");
    if (!sb || !ov) return;
    sb.classList.toggle("open");
    ov.classList.toggle("open");
  }

  function closeMobileSidebar() {
    const sb = document.getElementById("site-sidebar");
    const ov = document.getElementById("sidebar-overlay");
    if (sb) sb.classList.remove("open");
    if (ov) ov.classList.remove("open");
  }

  function buildTOC() {
    const tocMount = document.getElementById("site-toc");
    const article = document.querySelector(".prose");
    if (!tocMount || !article) return;

    const headings = Array.from(article.querySelectorAll("h2[id], h3[id]"));
    if (!headings.length) return;

    const itemsHtml = headings
      .map((h) => {
        const cls = h.tagName === "H3" ? "toc-link toc-h3" : "toc-link";
        const enSpan = h.querySelector('[data-lang="en"]');
        const arSpan = h.querySelector('[data-lang="ar"]');
        const labelHtml =
          enSpan && arSpan
            ? \`<span data-lang="en">\${escapeHtml(enSpan.textContent)}</span><span data-lang="ar">\${escapeHtml(arSpan.textContent)}</span>\`
            : escapeHtml(h.textContent);
        return \`<li><a class="\${cls}" href="#\${h.id}" data-toc-target="\${h.id}">\${labelHtml}</a></li>\`;
      })
      .join("");

    tocMount.innerHTML = \`
      <div class="toc-title">
        \${ICONS.toc}
        <span data-lang="en">On this page</span>
        <span data-lang="ar">في هذه الصفحة</span>
      </div>
      <ul class="toc-list">\${itemsHtml}</ul>
    \`;

    const tocLinks = Array.from(tocMount.querySelectorAll(".toc-link"));
    function setActive(id) {
      tocLinks.forEach((link) => {
        link.classList.toggle("active", link.dataset.tocTarget === id);
      });
    }
    if (headings[0]) setActive(headings[0].id);

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible.length > 0) setActive(visible[0].target.id);
      },
      { rootMargin: "-84px 0px -70% 0px", threshold: 0 }
    );
    headings.forEach((h) => observer.observe(h));
  }

  function enhanceCodeBlocks() {
    document.querySelectorAll(".code-block").forEach((block) => {
      if (block.querySelector(".code-copy-btn")) return;
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "code-copy-btn";
      btn.title = "Copy code";
      btn.innerHTML = ICONS.copy;

      btn.addEventListener("click", async () => {
        const codeEl = block.querySelector("pre code");
        if (!codeEl) return;
        try {
          await navigator.clipboard.writeText(codeEl.innerText);
          btn.innerHTML = ICONS.check;
          btn.classList.add("copied");
          setTimeout(() => {
            btn.innerHTML = ICONS.copy;
            btn.classList.remove("copied");
          }, 1600);
        } catch (_) {}
      });
      block.appendChild(btn);
    });

    const copyPageBtn = document.getElementById("copy-page-btn");
    if (copyPageBtn) {
      copyPageBtn.addEventListener("click", async () => {
        const main = document.querySelector(".main-content");
        if (!main) return;
        try {
          await navigator.clipboard.writeText(main.innerText.trim());
          const orig = copyPageBtn.innerHTML;
          copyPageBtn.innerHTML = \`\${ICONS.check}<span data-lang="en">Copied</span><span data-lang="ar">تم النسخ</span>\`;
          setTimeout(() => {
            copyPageBtn.innerHTML = orig;
          }, 1600);
        } catch (_) {}
      });
    }
  }

  function wireQuizzes() {
    document.querySelectorAll(".quiz-card").forEach((card) => {
      const answerIdx = Number(card.dataset.answer);
      const buttons = Array.from(card.querySelectorAll(".quiz-option"));
      const feedback = card.querySelector(".quiz-feedback");

      buttons.forEach((btn, idx) => {
        btn.addEventListener("click", () => {
          buttons.forEach((b) => b.classList.remove("is-correct", "is-wrong"));
          if (idx === answerIdx) {
            btn.classList.add("is-correct");
            if (feedback) {
              feedback.classList.remove("wrong");
              feedback.classList.add("show", "correct");
            }
          } else {
            btn.classList.add("is-wrong");
            if (buttons[answerIdx]) buttons[answerIdx].classList.add("is-correct");
            if (feedback) {
              feedback.classList.remove("correct");
              feedback.classList.add("show", "wrong");
            }
          }
        });
      });
    });
  }

  function wireTrackFilters() {
    const buttons = document.querySelectorAll(".track-filter-btn");
    if (!buttons.length) return;
    const sections = document.querySelectorAll(".chapter-section");

    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const filter = btn.dataset.trackFilter;
        buttons.forEach((b) => b.classList.toggle("active", b === btn));
        sections.forEach((sec) => {
          const tiles = Array.from(sec.querySelectorAll(".lesson-tile"));
          for (const tile of tiles) {
            tile.hidden = filter !== "all" && tile.dataset.lessonLevel !== filter;
            tile.style.display = tile.hidden ? "none" : "";
          }
          const match = tiles.some((tile) => !tile.hidden);
          sec.classList.toggle("hidden-by-filter", !match);
        });
      });
    });
  }

  let searchBackdrop = null;

  function renderSearchModal() {
    if (document.getElementById("search-backdrop")) return;
    searchBackdrop = document.createElement("div");
    searchBackdrop.id = "search-backdrop";
    searchBackdrop.className = "search-backdrop";
    searchBackdrop.innerHTML = \`
      <div class="search-modal" role="dialog" aria-modal="true">
        <div class="search-input-row">
          \${ICONS.search}
          <input type="text" id="search-modal-input" class="search-input" autocomplete="off" />
          <span class="search-kbd">ESC</span>
        </div>
        <div class="search-results" id="search-results"></div>
      </div>
    \`;

    searchBackdrop.addEventListener("click", (e) => {
      if (e.target === searchBackdrop) closeSearchModal();
    });

    document.body.appendChild(searchBackdrop);

    const input = document.getElementById("search-modal-input");
    input.addEventListener("input", () => renderSearchResults(input.value));

    document.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        openSearchModal();
      } else if (e.key === "Escape" && searchBackdrop.classList.contains("open")) {
        closeSearchModal();
      }
    });
  }

  function openSearchModal() {
    if (!searchBackdrop) renderSearchModal();
    searchBackdrop.classList.add("open");
    const input = document.getElementById("search-modal-input");
    applyLocale(getSavedLocale());
    input.value = "";
    renderSearchResults("");
    setTimeout(() => input.focus(), 20);
  }

  function closeSearchModal() {
    if (searchBackdrop) searchBackdrop.classList.remove("open");
  }

  function renderSearchResults(query) {
    const container = document.getElementById("search-results");
    if (!container) return;
    const q = query.trim().toLowerCase();
    const locale = getSavedLocale();

    const matches = SEARCH_INDEX.filter((item) => {
      if (!q) return item.hash === "";
      return (
        item.en.toLowerCase().includes(q) ||
        item.ar.toLowerCase().includes(q) ||
        item.groupEn.toLowerCase().includes(q) ||
        item.groupAr.toLowerCase().includes(q)
      );
    }).slice(0, 14);

    if (!matches.length) {
      container.innerHTML = \`<div class="search-empty">\${
        locale === "ar" ? "لا توجد نتائج مطابقة." : "No matching lessons found."
      }</div>\`;
      return;
    }

    container.innerHTML = matches
      .map((m) => {
        const title = locale === "ar" ? m.ar : m.en;
        const group = locale === "ar" ? m.groupAr : m.groupEn;
        return \`
          <a class="search-result-item" href="\${m.page}\${m.hash}">
            <span class="search-result-title">\${escapeHtml(title)}</span>
            <span class="search-result-meta">\${escapeHtml(group)} &middot; \${m.page}\${m.hash}</span>
          </a>
        \`;
      })
      .join("");

    container.querySelectorAll("a").forEach((a) => a.addEventListener("click", closeSearchModal));
  }

  document.addEventListener("DOMContentLoaded", () => {
    renderNavbar();
    renderSidebar();
    buildTOC();
    enhanceCodeBlocks();
    wireQuizzes();
    wireTrackFilters();
    renderSearchModal();
  });
})();
`;

fs.writeFileSync(path.join(OUT_DIR, "assets/app.js"), appJsContent, "utf8");

// ---------------------------------------------------------------------------
// 7. HTML Shell
// ---------------------------------------------------------------------------
function pageShell({ titleEn, bodyHtml }) {
  return `<!DOCTYPE html>
<html lang="en" data-locale="en" data-theme="light">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${esc(titleEn)} — ${esc(course.brand.en)}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700&family=Geist+Mono:wght@400;500;600&family=Instrument+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="assets/styles.css?v=13" />
  <script src="assets/app.js?v=13"></script>
</head>
<body>
  <div id="site-navbar"></div>

  <div class="docs-shell">
    <aside class="sidebar" id="site-sidebar"></aside>

    <main class="main-content">
      ${bodyHtml}
    </main>

    <aside class="toc" id="site-toc"></aside>
  </div>
</body>
</html>
`;
}

// ---------------------------------------------------------------------------
// 8. Generate index.html (Progressive Roadmap with Junior/Mid/Senior Filters)
// ---------------------------------------------------------------------------
let tileNum = 0;
const sectionsHtml = resolvedSections
  .map((sec, sIdx) => {
    const tiles = sec.lessons
      .map((l) => {
        tileNum += 1;
        const num = String(tileNum).padStart(2, "0");
        return `
          <a class="lesson-tile" data-lesson-level="${l.level}" href="${l.id}.html">
            <div class="lesson-tile-top" style="justify-content:space-between;">
              <div style="display:flex;align-items:baseline;gap:8px;min-width:0;">
                <span class="sidebar-num">${num}</span>
                <span class="lesson-tile-title">
                  <span data-lang="en">${esc(l.title.en)}</span>
                  <span data-lang="ar">${formatArLabel(l.title.ar)}</span>
                </span>
              </div>
              ${renderLevelBadge(l.levelMeta, "lvl-badge-xs")}
            </div>
            <div class="lesson-tile-desc">
              <span data-lang="en">${esc(l.question.en)}</span>
              <span data-lang="ar">${formatArLabel(l.question.ar)}</span>
            </div>
          </a>
        `;
      })
      .join("");

    return `
      <section class="chapter-section" data-level="${sec.level}">
        <h2 id="section-${sec.id}" style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
          <span>
            <span data-lang="en">${sIdx + 1}. ${esc(sec.title.en)}</span>
            <span data-lang="ar">${sIdx + 1}. ${formatArLabel(sec.title.ar)}</span>
          </span>
          ${renderLevelBadge(sec.levelMeta)}
        </h2>
        <p style="margin-bottom:12px;">
          <span data-lang="en">${esc(sec.summary.en)}</span>
          <span data-lang="ar">${formatProse(sec.summary.ar, true)}</span>
        </p>
        <div class="chapter-card">
          <div class="chapter-card-head">
            ${renderLevelBadge(sec.levelMeta)}
            <span class="lesson-step-pill">${sec.lessons.length} lessons</span>
          </div>
          <div class="chapter-lessons-grid">
            ${tiles}
          </div>
        </div>
      </section>
    `;
  })
  .join("\n");

const indexBody = `
  <div class="page-header">
    <div class="page-eyebrow-row">
      <div class="page-eyebrow">
        <span data-lang="en">Career Transition Roadmap</span>
        <span data-lang="ar">مسار التحول المهني</span>
      </div>
      ${renderLevelBadge(LEVEL_META.junior)}
      ${renderLevelBadge(LEVEL_META.mid)}
      ${renderLevelBadge(LEVEL_META.senior)}
    </div>
    <div class="page-title-row">
      <h1 class="page-title">
        <span data-lang="en">${esc(course.title.en)}</span>
        <span data-lang="ar">${formatArLabel(course.title.ar)}</span>
      </h1>
      <button type="button" class="copy-page-btn" id="copy-page-btn">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
        <span data-lang="en">Copy page</span>
        <span data-lang="ar">نسخ الصفحة</span>
      </button>
    </div>
    <p class="page-lead">
      <span data-lang="en">${formatProse(course.intro.en)}</span>
      <span data-lang="ar">${formatProse(course.intro.ar, true)}</span>
    </p>
  </div>

  <article class="prose">
    <div class="callout callout-laravel">
      <div class="callout-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
      </div>
      <div class="callout-body">
        <p data-lang="en">
          ${formatProse(course.study.en)}
        </p>
        <p data-lang="ar">
          ${formatProse(course.study.ar, true)}
        </p>
      </div>
    </div>

    <h2 id="practice-project"><span data-lang="en">${formatProse(course.project.title.en)}</span><span data-lang="ar">${formatProse(course.project.title.ar, true)}</span></h2>
    <p data-lang="en">${formatProse(course.project.intro.en)}</p>
    <p data-lang="ar">${formatProse(course.project.intro.ar, true)}</p>
    <details><summary><span data-lang="en">${esc(course.project.setupTitle.en)}</span><span data-lang="ar">${formatArLabel(course.project.setupTitle.ar)}</span></summary>
      <p data-lang="en">${formatProse(course.project.setup.en)}</p>
      <p data-lang="ar">${formatProse(course.project.setup.ar, true)}</p>
      <div class="code-block"><pre dir="ltr"><code>${esc(course.project.commands)}</code></pre></div>
    </details>
    <ul>${milestones.map(({ id, level }) => `
      <li><a href="${id}.html#milestone"><span data-lang="en">${LEVEL_META[level].en} project checkpoint</span><span data-lang="ar">تسليم مرحلة ${LEVEL_META[level].ar}</span></a></li>`).join("")}</ul>
    <div class="track-filters" role="group" aria-label="Filter by level">
      <button type="button" class="track-filter-btn active" data-track-filter="all">
        <span data-lang="en">All lessons (${counts.all})</span>
        <span data-lang="ar">كل الدروس (${counts.all})</span>
      </button>
      <button type="button" class="track-filter-btn" data-track-filter="junior">
        <span data-lang="en">Junior (${counts.junior})</span>
        <span data-lang="ar">جينيور (${counts.junior})</span>
      </button>
      <button type="button" class="track-filter-btn" data-track-filter="mid">
        <span data-lang="en">Mid-Level (${counts.mid})</span>
        <span data-lang="ar">ميد ليفل (${counts.mid})</span>
      </button>
      <button type="button" class="track-filter-btn" data-track-filter="senior">
        <span data-lang="en">Senior (${counts.senior})</span>
        <span data-lang="ar">سينيور (${counts.senior})</span>
      </button>
    </div>

    ${sectionsHtml}
  </article>

  <nav class="pagination">
    <span></span>
    <a class="page-nav-link next" href="${allLessons[0].id}.html">
      <span data-lang="en">Start Lesson 01: ${esc(allLessons[0].title.en)}</span>
      <span data-lang="ar">ابدأ الدرس 01: ${formatArLabel(allLessons[0].title.ar)}</span>
      <span>&rsaquo;</span>
    </a>
  </nav>
`;

fs.writeFileSync(
  path.join(OUT_DIR, "index.html"),
  pageShell({ titleEn: course.title.en, bodyHtml: indexBody }),
  "utf8"
);

// ---------------------------------------------------------------------------
// 9. Generate the lesson pages
// ---------------------------------------------------------------------------
const WARN_ICON = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>`;
const INFO_ICON = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>`;
const BRIDGE_ICON = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>`;

allLessons.forEach((lesson, idx) => {
  const sec = lesson.section;
  const lessonNum = String(idx + 1).padStart(2, "0");
  const prev = idx > 0 ? allLessons[idx - 1] : null;
  const next = idx < allLessons.length - 1 ? allLessons[idx + 1] : null;
  const bridge = prev && lesson.previous;
  const task = lesson.practical;
  const milestone = lesson.milestone;
  const baselineBridge = lesson.bridge;

  const bridgeHtml = bridge
    ? `
      <div class="callout callout-info">
        <div class="callout-icon">${INFO_ICON}</div>
        <div class="callout-body">
          <p data-lang="en"><strong>From the previous concept:</strong> ${formatProse(bridge.en)}</p>
          <p data-lang="ar"><strong>ربط مع الدرس السابق:</strong> ${formatProse(bridge.ar, true)}</p>
        </div>
      </div>
    `
    : "";

  const baselineBridgeHtml = baselineBridge
    ? `
      <div class="callout callout-laravel">
        <div class="callout-icon">${BRIDGE_ICON}</div>
        <div class="callout-body">
          <p data-lang="en"><strong>${esc(course.bridgeLabel.en)}</strong> ${formatProse(baselineBridge.en)}</p>
          <p data-lang="ar"><strong>${formatArLabel(course.bridgeLabel.ar)}</strong> ${formatProse(baselineBridge.ar, true)}</p>
        </div>
      </div>
    `
    : "";

  const casesHtml = lesson.cases
    .map((c, cIdx) => {
      const badgeClass = cIdx === 0 ? "badge-ok" : "badge-warn";
      const fileName = c.file;
      const fileLabel = `${fileName} — ${c.name.en}`;
      return `
        <h3 id="case-${cIdx + 1}">
          <span data-lang="en">Case ${cIdx + 1}: ${esc(c.name.en)}</span>
          <span data-lang="ar">الحالة ${cIdx + 1}: ${formatArLabel(c.name.ar)}</span>
        </h3>

        ${renderSequenceDiagram(lesson, cIdx)}

        <div class="code-block has-header" dir="ltr">
          <div class="code-block-header">
            <span>${esc(fileLabel)}</span>
            <span class="${badgeClass}">${cIdx === 0 ? "Case 1" : "Case 2"}</span>
          </div>
          <pre><code>${highlightCode(c.code)}</code></pre>
        </div>
      `;
    })
    .join("\n");

  const tableRowsHtml = lesson.actors
    .map((actor, aIdx) => {
      const obs0 = lesson.cases[0]?.observations[aIdx];
      const obs1 = lesson.cases[1]?.observations[aIdx];
      return `
        <tr>
          <td>
            <strong>${esc(actor.name)}</strong><br/>
            <span style="font-size:0.78rem;color:var(--text-subtle)">${esc(
              Array.isArray(actor.description) ? actor.description.join(" / ") : actor.description
            )}</span>
          </td>
          <td>
            <span data-lang="en">${formatProse(obs0?.en || "")}</span>
            <span data-lang="ar">${formatProse(obs0?.ar || "", true)}</span>
          </td>
          <td>
            <span data-lang="en">${formatProse(obs1?.en || "")}</span>
            <span data-lang="ar">${formatProse(obs1?.ar || "", true)}</span>
          </td>
        </tr>
      `;
    })
    .join("");

  const actorsParamsHtml = lesson.actors
    .map((actor) => {
      const desc = Array.isArray(actor.description) ? actor.description.join(" / ") : actor.description;
      return `
        <div class="param-item">
          <div class="param-header">
            <span class="param-name">${esc(actor.name)}</span>
            <span class="type-pill">${esc(actor.kind)}</span>
          </div>
          <p class="param-desc">${esc(desc)}</p>
        </div>
      `;
    })
    .join("");

  const quizChoicesHtml = lesson.quiz.choices
    .map(
      (chItem, chI) => `
        <button type="button" class="quiz-option">
          <span class="sidebar-num">${String.fromCharCode(65 + chI)}</span>
          <span data-lang="en">${formatProse(chItem.en)}</span>
          <span data-lang="ar">${formatProse(chItem.ar, true)}</span>
        </button>
      `
    )
    .join("");



  const prevLinkHtml = prev
    ? `
      <a class="page-nav-link prev" href="${prev.id}.html">
        <span>&lsaquo;</span>
        <span data-lang="en">${esc(prev.title.en)}</span>
        <span data-lang="ar">${formatArLabel(prev.title.ar)}</span>
      </a>
    `
    : `
      <a class="page-nav-link prev" href="index.html">
        <span>&lsaquo;</span>
        <span data-lang="en">Curriculum Overview</span>
        <span data-lang="ar">نظرة عامة على المنهج</span>
      </a>
    `;

  const nextLinkHtml = next
    ? `
      <a class="page-nav-link next" href="${next.id}.html">
        <span data-lang="en">${esc(next.title.en)}</span>
        <span data-lang="ar">${formatArLabel(next.title.ar)}</span>
        <span>&rsaquo;</span>
      </a>
    `
    : `<span></span>`;

  const bodyHtml = `
    <div class="page-header">
      <div class="page-eyebrow-row">
        <div class="page-eyebrow">
          <span data-lang="en">${esc(sec.title.en)}</span>
          <span data-lang="ar">${formatArLabel(sec.title.ar)}</span>
        </div>
        ${renderLevelBadge(lesson.levelMeta)}
        <span class="lesson-step-pill">${lessonNum} / ${allLessons.length}</span>
      </div>

      <div class="page-title-row">
        <h1 class="page-title">
          <span data-lang="en">${esc(lesson.title.en)}</span>
          <span data-lang="ar">${formatArLabel(lesson.title.ar)}</span>
        </h1>
        <button type="button" class="copy-page-btn" id="copy-page-btn">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
          <span data-lang="en">Copy page</span>
          <span data-lang="ar">نسخ الصفحة</span>
        </button>
      </div>

      <p class="page-lead">
        <span data-lang="en">${formatProse(lesson.question.en)}</span>
        <span data-lang="ar">${formatProse(lesson.question.ar, true)}</span>
      </p>
    </div>

    <article class="prose">
      ${baselineBridgeHtml}
      ${bridgeHtml}

      <h2 id="overview">
        <span data-lang="en">How It Works</span>
        <span data-lang="ar">كيف تعمل الآلية</span>
      </h2>

      <p data-lang="en">${formatProse(lesson.intro.en)}</p>
      <p data-lang="ar">${formatProse(lesson.intro.ar, true)}</p>

      <div class="callout callout-warning">
        <div class="callout-icon">${WARN_ICON}</div>
        <div class="callout-body">
          <p data-lang="en">${formatProse(lesson.mechanism.en)}</p>
          <p data-lang="ar">${formatProse(lesson.mechanism.ar, true)}</p>
        </div>
      </div>

      <h2 id="trace-diagrams">
        <span data-lang="en">Execution Diagrams &amp; Code</span>
        <span data-lang="ar">المخططات التوضيحية والكود</span>
      </h2>

      <p data-lang="en">
        Compare the two execution scenarios below. Predict the result of each case, then check which change explains the observations.
      </p>
      <p data-lang="ar">
        قارن بين حالتي التنفيذ التاليتين. توقّع نتيجة كل حالة ثم حدّد التغيير اللي يفسّر الملاحظات.
      </p>

      ${casesHtml}

      <h2 id="comparison-matrix">
        <span data-lang="en">Side-by-Side Comparison</span>
        <span data-lang="ar">مقارنة تفصيلية بين الحالتين</span>
      </h2>

      <div class="table-wrap">
        <table class="doc-table">
          <thead>
            <tr>
              <th>
                <span data-lang="en">Stage / Actor</span>
                <span data-lang="ar">المرحلة / المكوّن</span>
              </th>
              <th><code>${esc(lesson.cases[0]?.name.en || "Case 1")}</code></th>
              <th><code>${esc(lesson.cases[1]?.name.en || "Case 2")}</code></th>
            </tr>
          </thead>
          <tbody>
            ${tableRowsHtml}
          </tbody>
        </table>
      </div>


      <h2 id="key-concepts">
        <span data-lang="en">Key Concept &amp; Components</span>
        <span data-lang="ar">المفهوم الأساسي والمكوّنات</span>
      </h2>

      <div class="param-list">
        <div class="param-item">
          <div class="param-header">
            <span class="param-name">${esc(lesson.term.en)}</span>
            <span class="type-pill">core term</span>
          </div>
          <p class="param-desc" data-lang="en">${formatProse(lesson.definition.en)}</p>
          <p class="param-desc" data-lang="ar">${formatProse(lesson.definition.ar, true)}</p>
        </div>
        ${actorsParamsHtml}
      </div>

      <h2 id="practical-lab">
        <span data-lang="en">Apply it in ${esc(course.project.name)}</span>
        <span data-lang="ar">تطبيق الدرس في ${formatArLabel(course.project.name)}</span>
      </h2>

      <p><span data-lang="en">Start in </span><span data-lang="ar">ابدأ من </span><code dir="ltr">${esc(task.file)}</code></p>
      <p data-lang="en">${formatProse(task.en)}</p>
      <p data-lang="ar">${formatProse(task.ar, true)}</p>
      ${milestone ? `
        <h2 id="milestone">
          <span data-lang="en">${lesson.levelMeta.en} project checkpoint</span>
          <span data-lang="ar">تسليم مرحلة ${lesson.levelMeta.ar}</span>
        </h2>
        <p data-lang="en">${formatProse(milestone.en)}</p>
        <p data-lang="ar">${formatProse(milestone.ar, true)}</p>
      ` : ""}

      <h2 id="concept-check">
        <span data-lang="en">Concept Check</span>
        <span data-lang="ar">اختبر فهمك</span>
      </h2>

      <div class="quiz-card" data-answer="${lesson.quiz.answer}">
        <p class="quiz-question">
          <span data-lang="en">${formatProse(lesson.quiz.question.en)}</span>
          <span data-lang="ar">${formatProse(lesson.quiz.question.ar, true)}</span>
        </p>
        <div class="quiz-options">
          ${quizChoicesHtml}
        </div>
        <div class="quiz-feedback">
          <p data-lang="en" style="margin:0"><strong>Explanation:</strong> ${formatProse(lesson.quiz.reason.en)}</p>
          <p data-lang="ar" style="margin:0"><strong>التوضيح:</strong> ${formatProse(lesson.quiz.reason.ar, true)}</p>
        </div>
      </div>

      ${
        lesson.source
          ? `
        <p style="font-size:0.875rem;color:var(--text-muted);margin-top:20px;">
          <span data-lang="en">Official Reference:</span>
          <span data-lang="ar">المرجع الرسمي:</span>
          <a class="doc-link" href="${esc(lesson.source[1])}" target="_blank" rel="noopener noreferrer">${esc(lesson.source[0])} &nearr;</a>
        </p>
      `
          : ""
      }
    </article>

    <nav class="pagination">
      ${prevLinkHtml}
      ${nextLinkHtml}
    </nav>
  `;

  fs.writeFileSync(
    path.join(OUT_DIR, `${lesson.id}.html`),
    pageShell({ titleEn: lesson.title.en, bodyHtml }),
    "utf8"
  );
});

console.log(`Built index.html + ${allLessons.length} lesson HTML pages + assets/app.js in ${OUT_DIR}`);
