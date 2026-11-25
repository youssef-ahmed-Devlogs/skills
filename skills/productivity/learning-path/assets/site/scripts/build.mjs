import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { course, sections } from "../course.mjs";
import { courseLanguages, validateCourse } from "./validate.mjs";

const OUT_DIR = fileURLToPath(new URL("../", import.meta.url));
validateCourse(course, sections);
const languages = courseLanguages(course);
const firstLanguage = languages[0];

function translations(render) {
  return Object.fromEntries(languages.map(lang => [lang, render(lang)]));
}

function valueIn(value, lang) {
  return typeof value === "string" ? value : value[lang];
}

function variants(render, tag = "span", attrs = "") {
  return languages.map(lang => `<${tag} data-lang="${lang}"${attrs}>${render(lang)}</${tag}>`).join("");
}

function label(value, tag, attrs) {
  return variants(lang => formatProse(valueIn(value, lang), lang === "ar"), tag, attrs);
}

// Arguments may contain escaped, formatted HTML.
function wording(en, ar, tag, attrs) {
  return variants(lang => lang === "ar" ? ar : en, tag, attrs);
}


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
  return `<span class="${cls}">${wording(levelMeta.en, levelMeta.ar)}</span>`;
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

function actorDescription(actor) {
  return [actor.description].flat().map(item => label(item)).join(" / ");
}

function renderSequenceDiagram(lesson, caseIdx, lang) {
  const c = lesson.cases[caseIdx];
  const markerId = `arr-${lesson.id}-${caseIdx}-${lang}`;
  const actors = lesson.actors.map((a) => ({
    name: valueIn(a.name, lang),
    sub: valueIn(Array.isArray(a.description) ? a.description[caseIdx] : a.description, lang)
  }));

  const xs = [104, 310, 516];
  const boxW = 172;
  const boxH = 48;
  const obs = c.observations.map((o) => o[lang]);
  const outcomeBoxClass = caseIdx === 0 ? "d-state-green" : "d-state-red";

  let curY = 78;
  const parts = [];

  const n1 = renderNoteBox(xs[0], curY, obs[0] || c.name[lang], "d-note-box", "d-note-text");
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
    <div class="diagram-wrap" dir="ltr" data-lang="${lang}">
      <svg direction="${lang === "ar" ? "rtl" : "ltr"}" viewBox="0 0 620 ${totalH}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${esc(lesson.title[lang])} — ${esc(c.name[lang])}">
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
    title: wording("Roadmap", "خريطة المسار"),
    items: [{ href: "index.html", num: "00", title: wording("Curriculum Overview", "نظرة عامة على المنهج") }]
  },
  ...resolvedSections.map(sec => ({
    badge: renderLevelBadge(sec.levelMeta, "lvl-badge-xs"),
    title: label(sec.title),
    items: sec.lessons.map(lesson => ({
      href: `${lesson.id}.html`,
      num: String(++navCounter).padStart(2, "0"),
      title: label(lesson.title)
    }))
  }))
];

const milestones = allLessons.filter(lesson => lesson.milestone);
const searchIndexData = translations(lang => {
  const overview = lang === "ar"
    ? `${course.title.ar} · عدد الفصول: ${resolvedSections.length}، عدد الدروس: ${counts.all}`
    : `${course.title.en} · ${resolvedSections.length} sections, ${counts.all} lessons`;
  const rows = [{ page: "index.html", hash: "", title: overview, group: lang === "ar" ? "خريطة المسار" : "Roadmap" }];
  for (const lesson of allLessons) {
    const page = lesson.id + ".html";
    const group = lesson.section.title[lang];
    const title = lesson.title[lang];
    rows.push({ page, group, hash: "", title: `[${lesson.levelMeta[lang]}] ${title} (${lesson.term[lang]})` });
    lesson.cases.forEach((item, index) => {
      const caseLabel = lang === "ar" ? "الحالة" : "Case";
      rows.push({ page, group, hash: "#case-" + (index + 1), title: `${title} · ${caseLabel} ${index + 1}: ${item.name[lang]}` });
    });
  }
  return rows;
});

const languageMenu = languages.length === 2 ? `
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
  </div>` : "";

const interfaceText = {
  en: {
    navigation: "Toggle navigation", theme: "Change theme preference",
    copy: "Copy code", filter: "Filter by level",
    search: `Search all ${counts.all} lessons...`, empty: "No matching lessons found."
  },
  ar: {
    navigation: "القائمة", theme: "تغيير المظهر",
    copy: "نسخ الكود", filter: "تصفية حسب المستوى",
    search: `ابحث في الدروس (${counts.all})...`, empty: "لا توجد نتائج مطابقة."
  }
};

const appJsContent = `/* ==========================================================================
   Learning Path — Shared Interactive Shell
   Junior -> Mid -> Senior Badges · Light/Dark
   ========================================================================== */

(function () {
  "use strict";

  const escapeHtml = ${esc.toString()};
  const languages = ${JSON.stringify(languages)};
  const ui = ${JSON.stringify(translations(lang => interfaceText[lang]))};
  const brandHtml = ${JSON.stringify(label(course.brand))};
  const journeyHtml = ${JSON.stringify(label(course.journey))};
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
    const saved = localStorage.getItem(STORAGE_LOCALE);
    return languages.includes(saved) ? saved : languages[0];
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
    document.querySelectorAll("[data-theme-choice]").forEach((item) => {
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
    if (languages.length > 1) localStorage.setItem(STORAGE_LOCALE, locale);
    document.title = document.querySelector("title").dataset[locale];

    document.querySelectorAll("[data-set-locale]").forEach((btn) => {
      btn.setAttribute("data-active", btn.dataset.setLocale === locale ? "true" : "false");
    });

    document.querySelectorAll("[data-ui-label]").forEach(element => {
      element.setAttribute("aria-label", ui[locale][element.dataset.uiLabel]);
    });
    document.querySelectorAll(".code-copy-btn").forEach(btn => { btn.title = ui[locale].copy; });
    const searchInput = document.getElementById("search-modal-input");
    if (searchInput) searchInput.placeholder = ui[locale].search;
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
            <button class="mobile-menu-btn" id="mobile-menu-btn" data-ui-label="navigation">
              \${ICONS.menu}
            </button>
            <a href="index.html" class="brand-logo">
              \${brandHtml}
              <span class="brand-chevrons">&gt;&gt;</span>
            </a>
            <span class="version-badge">
              \${journeyHtml}
            </span>
          </div>

          <button class="search-trigger" id="search-trigger-btn" type="button">
            <span class="search-trigger-left">
              \${ICONS.search}
              ${wording(`Search ${counts.all} lessons...`, `ابحث في ${counts.all} درساً...`)}
            </span>
            <span class="search-kbd">Ctrl K</span>
          </button>

          <div class="navbar-right">
            ${languageMenu}
            <div class="theme-menu-wrap" id="theme-menu-wrap">
              <button
                type="button"
                class="icon-btn"
                id="theme-toggle-btn"
                data-ui-label="theme"
                aria-haspopup="menu"
                aria-expanded="false"
              >
                \${ICONS.system}
              </button>
              <div class="theme-menu" id="theme-menu" role="menu">
                <button type="button" class="theme-menu-item" role="menuitem" data-theme-choice="system">
                  <span class="theme-menu-item-left">
                    \${ICONS.system}
                    ${wording("System", "النظام")}
                  </span>
                  <span class="theme-menu-check">\${ICONS.check}</span>
                </button>
                <button type="button" class="theme-menu-item" role="menuitem" data-theme-choice="light">
                  <span class="theme-menu-item-left">
                    \${ICONS.sun}
                    ${wording("Light", "نهاري")}
                  </span>
                  <span class="theme-menu-check">\${ICONS.check}</span>
                </button>
                <button type="button" class="theme-menu-item" role="menuitem" data-theme-choice="dark">
                  <span class="theme-menu-item-left">
                    \${ICONS.moon}
                    ${wording("Dark", "ليلي")}
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
      const itemsHtml = group.items
        .map((item) => {
          const isActive = item.href === current ? " active" : "";
          const numSpan = item.num === "00" ? "" : \`<span class="sidebar-num">\${item.num}</span>\`;
          return \`
            <li>
              <a class="sidebar-link\${isActive}" href="\${item.href}">
                \${numSpan}
                \${item.title}
              </a>
            </li>
          \`;
        })
        .join("");

      return \`
        <div class="sidebar-group">
          <div class="sidebar-group-head">
            <h4 class="sidebar-group-title">
              \${group.title}
            </h4>
            \${group.badge || ""}
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
        const labelHtml = languages.map(lang => {
          const element = h.querySelector('[data-lang="' + lang + '"]');
          return \`<span data-lang="\${lang}">\${escapeHtml(element.textContent)}</span>\`;
        }).join("");
        return \`<li><a class="\${cls}" href="#\${h.id}" data-toc-target="\${h.id}">\${labelHtml}</a></li>\`;
      })
      .join("");

    tocMount.innerHTML = \`
      <div class="toc-title">
        \${ICONS.toc}
        ${wording("On this page", "في هذه الصفحة")}
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
      btn.title = ui[getSavedLocale()].copy;
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
          copyPageBtn.innerHTML = \`\${ICONS.check}${wording("Copied", "تم النسخ")}\`;
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

    const matches = SEARCH_INDEX[locale].filter((item, index) => {
      if (!q) return item.hash === "";
      return languages.some(lang => {
        const row = SEARCH_INDEX[lang][index];
        return row.title.toLowerCase().includes(q) || row.group.toLowerCase().includes(q);
      });
    }).slice(0, 14);

    if (!matches.length) {
      container.innerHTML = \`<div class="search-empty">\${ui[locale].empty}</div>\`;
      return;
    }

    container.innerHTML = matches
      .map((m) => {
        const { title, group } = m;
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
function pageShell({ title, bodyHtml }) {
  return `<!DOCTYPE html>
<html lang="${firstLanguage}" dir="${firstLanguage === "ar" ? "rtl" : "ltr"}" data-locale="${firstLanguage}" data-theme="light">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title ${languages.map(lang => `data-${lang}="${esc(title[lang])} · ${esc(course.brand[lang])}"`).join(" ")}>${esc(title[firstLanguage])} · ${esc(course.brand[firstLanguage])}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?${languages.includes("ar") ? "family=Cairo:wght@400;500;600;700&" : ""}family=Geist+Mono:wght@400;500;600&family=Instrument+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="assets/styles.css?v=14" />
  <script src="assets/app.js?v=14"></script>
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
                  ${label(l.title)}
                </span>
              </div>
              ${renderLevelBadge(l.levelMeta, "lvl-badge-xs")}
            </div>
            <div class="lesson-tile-desc">
              ${label(l.question)}
            </div>
          </a>
        `;
      })
      .join("");

    return `
      <section class="chapter-section" data-level="${sec.level}">
        <h2 id="section-${sec.id}" style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
          <span>
            ${wording(`${sIdx + 1}. ${esc(sec.title.en)}`, `${sIdx + 1}. ${formatArLabel(sec.title.ar)}`)}
          </span>
          ${renderLevelBadge(sec.levelMeta)}
        </h2>
        <p style="margin-bottom:12px;">
          ${label(sec.summary)}
        </p>
        <div class="chapter-card">
          <div class="chapter-card-head">
            ${renderLevelBadge(sec.levelMeta)}
            <span class="lesson-step-pill">${wording(`${sec.lessons.length} lessons`, `عدد الدروس: ${sec.lessons.length}`)}</span>
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
        ${wording("Career Transition Roadmap", "مسار التحول المهني")}
      </div>
      ${renderLevelBadge(LEVEL_META.junior)}
      ${renderLevelBadge(LEVEL_META.mid)}
      ${renderLevelBadge(LEVEL_META.senior)}
    </div>
    <div class="page-title-row">
      <h1 class="page-title">
        ${label(course.title)}
      </h1>
      <button type="button" class="copy-page-btn" id="copy-page-btn">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
        ${wording("Copy page", "نسخ الصفحة")}
      </button>
    </div>
    <p class="page-lead">
      ${label(course.intro)}
    </p>
  </div>

  <article class="prose">
    <div class="callout callout-laravel">
      <div class="callout-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
      </div>
      <div class="callout-body">
        ${label(course.study, "p")}
      </div>
    </div>

    <h2 id="practice-project">${label(course.project.title)}</h2>
    ${label(course.project.intro, "p")}
    <details><summary>${label(course.project.setupTitle)}</summary>
      ${label(course.project.setup, "p")}
      <div class="code-block"><pre dir="ltr"><code>${esc(course.project.commands)}</code></pre></div>
    </details>
    <ul>${milestones.map(({ id, level }) => `
      <li><a href="${id}.html#milestone">${wording(`${LEVEL_META[level].en} project checkpoint`, `تسليم مرحلة ${LEVEL_META[level].ar}`)}</a></li>`).join("")}</ul>
    <div class="track-filters" role="group" data-ui-label="filter" aria-label="${interfaceText[firstLanguage].filter}">
      <button type="button" class="track-filter-btn active" data-track-filter="all">
        ${wording(`All lessons (${counts.all})`, `كل الدروس (${counts.all})`)}
      </button>
      <button type="button" class="track-filter-btn" data-track-filter="junior">
        ${wording(`Junior (${counts.junior})`, `جينيور (${counts.junior})`)}
      </button>
      <button type="button" class="track-filter-btn" data-track-filter="mid">
        ${wording(`Mid-Level (${counts.mid})`, `ميد ليفل (${counts.mid})`)}
      </button>
      <button type="button" class="track-filter-btn" data-track-filter="senior">
        ${wording(`Senior (${counts.senior})`, `سينيور (${counts.senior})`)}
      </button>
    </div>

    ${sectionsHtml}
  </article>

  <nav class="pagination">
    <span></span>
    <a class="page-nav-link next" href="${allLessons[0].id}.html">
      ${wording(`Start Lesson 01: ${esc(allLessons[0].title.en)}`, `ابدأ الدرس 01: ${formatArLabel(allLessons[0].title.ar)}`)}
      <span>&rsaquo;</span>
    </a>
  </nav>
`;

fs.writeFileSync(
  path.join(OUT_DIR, "index.html"),
  pageShell({ title: course.title, bodyHtml: indexBody }),
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
          ${wording(`<strong>From the previous concept:</strong> ${formatProse(bridge.en)}`, `<strong>ربط مع الدرس السابق:</strong> ${formatProse(bridge.ar, true)}`, "p")}
        </div>
      </div>
    `
    : "";

  const baselineBridgeHtml = baselineBridge
    ? `
      <div class="callout callout-laravel">
        <div class="callout-icon">${BRIDGE_ICON}</div>
        <div class="callout-body">
          ${wording(`<strong>${esc(course.bridgeLabel.en)}</strong> ${formatProse(baselineBridge.en)}`, `<strong>${formatArLabel(course.bridgeLabel.ar)}</strong> ${formatProse(baselineBridge.ar, true)}`, "p")}
        </div>
      </div>
    `
    : "";

  const casesHtml = lesson.cases
    .map((c, cIdx) => {
      const badgeClass = cIdx === 0 ? "badge-ok" : "badge-warn";
      const fileName = c.file;
      return `
        <h3 id="case-${cIdx + 1}">
          ${wording(`Case ${cIdx + 1}: ${esc(c.name.en)}`, `الحالة ${cIdx + 1}: ${formatArLabel(c.name.ar)}`)}
        </h3>

        ${languages.map(lang => renderSequenceDiagram(lesson, cIdx, lang)).join("")}

        <div class="code-block has-header" dir="ltr">
          <div class="code-block-header">
            <span>${esc(fileName)} · ${label(c.name)}</span>
            <span class="${badgeClass}">${wording(`Case ${cIdx + 1}`, `الحالة ${cIdx + 1}`)}</span>
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
            <strong>${label(actor.name)}</strong><br/>
            <span style="font-size:0.78rem;color:var(--text-subtle)">${actorDescription(actor)}</span>
          </td>
          <td>
            ${label(obs0)}
          </td>
          <td>
            ${label(obs1)}
          </td>
        </tr>
      `;
    })
    .join("");

  const actorsParamsHtml = lesson.actors
    .map((actor) => {
      return `
        <div class="param-item">
          <div class="param-header">
            <span class="param-name">${label(actor.name)}</span>
            <span class="type-pill">${label(actor.kind)}</span>
          </div>
          <p class="param-desc">${actorDescription(actor)}</p>
        </div>
      `;
    })
    .join("");

  const quizChoicesHtml = lesson.quiz.choices
    .map(
      (chItem, chI) => `
        <button type="button" class="quiz-option">
          <span class="sidebar-num">${String.fromCharCode(65 + chI)}</span>
          ${label(chItem)}
        </button>
      `
    )
    .join("");



  const prevLinkHtml = prev
    ? `
      <a class="page-nav-link prev" href="${prev.id}.html">
        <span>&lsaquo;</span>
        ${label(prev.title)}
      </a>
    `
    : `
      <a class="page-nav-link prev" href="index.html">
        <span>&lsaquo;</span>
        ${wording("Curriculum Overview", "نظرة عامة على المنهج")}
      </a>
    `;

  const nextLinkHtml = next
    ? `
      <a class="page-nav-link next" href="${next.id}.html">
        ${label(next.title)}
        <span>&rsaquo;</span>
      </a>
    `
    : `<span></span>`;

  const bodyHtml = `
    <div class="page-header">
      <div class="page-eyebrow-row">
        <div class="page-eyebrow">
          ${label(sec.title)}
        </div>
        ${renderLevelBadge(lesson.levelMeta)}
        <span class="lesson-step-pill">${lessonNum} / ${allLessons.length}</span>
      </div>

      <div class="page-title-row">
        <h1 class="page-title">
          ${label(lesson.title)}
        </h1>
        <button type="button" class="copy-page-btn" id="copy-page-btn">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
          ${wording("Copy page", "نسخ الصفحة")}
        </button>
      </div>

      <p class="page-lead">
        ${label(lesson.question)}
      </p>
    </div>

    <article class="prose">
      ${baselineBridgeHtml}
      ${bridgeHtml}

      <h2 id="overview">
        ${wording("How It Works", "كيف تعمل الآلية")}
      </h2>

      ${label(lesson.intro, "p")}

      <div class="callout callout-warning">
        <div class="callout-icon">${WARN_ICON}</div>
        <div class="callout-body">
          ${label(lesson.mechanism, "p")}
        </div>
      </div>

      <h2 id="trace-diagrams">
        ${wording("Execution Diagrams &amp; Code", "المخططات التوضيحية والكود")}
      </h2>

      ${wording("Compare the two execution scenarios below. Predict the result of each case, then check which change explains the observations.", "قارن بين حالتي التنفيذ التاليتين. توقّع نتيجة كل حالة ثم حدّد التغيير اللي يفسّر الملاحظات.", "p")}

      ${casesHtml}

      <h2 id="comparison-matrix">
        ${wording("Side-by-Side Comparison", "مقارنة تفصيلية بين الحالتين")}
      </h2>

      <div class="table-wrap">
        <table class="doc-table">
          <thead>
            <tr>
              <th>
                ${wording("Stage / Actor", "المرحلة / المكوّن")}
              </th>
              <th><code>${label(lesson.cases[0].name)}</code></th>
              <th><code>${label(lesson.cases[1].name)}</code></th>
            </tr>
          </thead>
          <tbody>
            ${tableRowsHtml}
          </tbody>
        </table>
      </div>


      <h2 id="key-concepts">
        ${wording("Key Concept &amp; Components", "المفهوم الأساسي والمكوّنات")}
      </h2>

      <div class="param-list">
        <div class="param-item">
          <div class="param-header">
            <span class="param-name">${label(lesson.term)}</span>
            <span class="type-pill">${wording("core term", "مصطلح أساسي")}</span>
          </div>
          ${label(lesson.definition, "p", " class=\"param-desc\"")}
        </div>
        ${actorsParamsHtml}
      </div>

      <h2 id="practical-lab">
        ${wording(`Apply it in ${esc(course.project.name)}`, `تطبيق الدرس في ${formatArLabel(course.project.name)}`)}
      </h2>

      <p>${wording("Start in ", "ابدأ من ")}<code dir="ltr">${esc(task.file)}</code></p>
      ${label(task, "p")}
      ${milestone ? `
        <h2 id="milestone">
          ${wording(`${lesson.levelMeta.en} project checkpoint`, `تسليم مرحلة ${lesson.levelMeta.ar}`)}
        </h2>
        ${label(milestone, "p")}
      ` : ""}

      <h2 id="concept-check">
        ${wording("Concept Check", "اختبر فهمك")}
      </h2>

      <div class="quiz-card" data-answer="${lesson.quiz.answer}">
        <p class="quiz-question">
          ${label(lesson.quiz.question)}
        </p>
        <div class="quiz-options">
          ${quizChoicesHtml}
        </div>
        <div class="quiz-feedback">
          ${wording(`<strong>Explanation:</strong> ${formatProse(lesson.quiz.reason.en)}`, `<strong>التوضيح:</strong> ${formatProse(lesson.quiz.reason.ar, true)}`, "p", " style=\"margin:0\"")}
        </div>
      </div>

      ${
        lesson.source
          ? `
        <p style="font-size:0.875rem;color:var(--text-muted);margin-top:20px;">
          ${wording("Official Reference:", "المرجع الرسمي:")}
          <a class="doc-link" href="${esc(lesson.source[1])}" target="_blank" rel="noopener noreferrer">${label(lesson.source[0])} &nearr;</a>
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
    pageShell({ title: lesson.title, bodyHtml }),
    "utf8"
  );
});

console.log(`Built index.html + ${allLessons.length} lesson HTML pages + assets/app.js in ${OUT_DIR}`);
