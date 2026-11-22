/* Framework-free components. Lesson content and scene state belong to the course. */
const Studio = (() => {
  const labels = {
    en: { course:"Course", lessons:"lessons", progress:"Progress", language:"Language", dark:"Switch to dark theme", light:"Switch to light theme", reached:"Reached recap", learn:"Learn", practice:"Practice", lab:"Design Lab", sheets:"Cheatsheets", search:"Search lessons & concepts…", replay:"Replay", pause:"Pause", resume:"Resume", inLesson:"In this lesson", goals:"You'll learn", notes:"Notes", expand:"Expand diagram", menu:"Course index" },
    ar: { course:"المقرر", lessons:"دروس", progress:"التقدّم", language:"اللغة", dark:"التبديل إلى الوضع الداكن", light:"التبديل إلى الوضع الفاتح", reached:"وصلت للخلاصة", learn:"تعلّم", practice:"تدريب", lab:"مختبر التصميم", sheets:"ملخصات", search:"ابحث في الدروس والمفاهيم…", replay:"إعادة", pause:"إيقاف مؤقت", resume:"استئناف", inLesson:"في هذا الدرس", goals:"ستتعلّم", notes:"ملاحظات", expand:"تكبير الرسم", menu:"الفهرس" }
  };
  const folders = ["#d3ae78","#3a9c53","#825dcb","#dc8051","#3389bf","#319b90","#ce5477","#909d48","#69798e"];
  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function icon(kind, color = "currentColor") {
    const shapes = {
      folder:'<path d="M2 4h7l2 2h10v13H2z" fill="currentColor"/><path d="M2 8h19" stroke="var(--paper)" opacity=".6"/>',
      file:'<path d="M5 2h9l5 5v14H5z M14 2v6h5" fill="none" stroke="currentColor" stroke-width="1.4"/>',
      done:'<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor"/><path d="m7 12 3 3 7-7" fill="none" stroke="currentColor" stroke-width="1.5"/>'
    };
    const svg = document.createElementNS("http://www.w3.org/2000/svg","svg");
    svg.setAttribute("viewBox","0 0 24 24"); svg.setAttribute("class","tree-icon "+kind);
    svg.setAttribute("aria-hidden","true"); svg.style.color = color;
    svg.innerHTML = shapes[kind];
    return svg;
  }
  function preferences(host, {key, initialLanguage = "en", onChange}) {
    const storageKey = "visual-studio:"+key+":preferences";
    let saved;
    try { saved = JSON.parse(localStorage.getItem(storageKey)) || {}; } catch { saved = {}; }
    let lang = ["ar","en"].includes(saved.lang) ? saved.lang : initialLanguage === "ar" ? "ar" : "en";
    let theme = saved.theme === "dark" ? "dark" : "light";
    const language = element("select");
    for (const [value, text] of [["ar","العربية"],["en","English"]]) {
      const option = element("option","",text); option.value = value; option.lang = value;
      language.append(option);
    }
    const themeButton = element("button"); themeButton.type = "button";
    host.classList.add("preferences"); host.replaceChildren(language,themeButton);
    function apply() {
      const root = document.documentElement;
      root.lang = lang; root.dir = lang === "ar" ? "rtl" : "ltr"; root.dataset.theme = theme;
      const t = labels[lang]; language.value = lang; language.setAttribute("aria-label",t.language);
      for (const node of document.querySelectorAll("[data-copy]")) {
        if (Object.hasOwn(t,node.dataset.copy)) node.textContent = t[node.dataset.copy];
      }
      for (const action of ["menu","expand","search"]) {
        document.querySelector('[data-action="'+action+'"]')?.setAttribute("aria-label",t[action]);
      }
      themeButton.textContent = theme === "dark" ? "☀" : "☾";
      themeButton.title = theme === "dark" ? t.light : t.dark;
      themeButton.setAttribute("aria-label",themeButton.title);
      onChange({lang,theme});
    }
    function save() {
      try { localStorage.setItem(storageKey,JSON.stringify({lang,theme})); } catch { /* The live controls still work. */ }
      apply();
    }
    language.onchange = () => { lang = language.value; save(); };
    themeButton.onclick = () => { theme = theme === "dark" ? "light" : "dark"; save(); };
    apply();
  }
  function tree(host, {chapters, active, completed = new Set(), lang, onNavigate}) {
    const t = labels[lang];
    const previous = new Map(Array.from(host.querySelectorAll(".chapter"), group => [group.dataset.id,group.open]));
    const newLesson = active !== host.dataset.active;
    const progressOpen = host.querySelector(".tree-progress")?.open || false;
    const scrollTop = host.querySelector(".tree-list")?.scrollTop || 0;
    const count = group => group.lessons.filter(lesson => completed.has(lesson.id)).length;
    const all = chapters.flatMap(group => group.lessons);
    const number = n => n.toLocaleString(lang);
    const fraction = (a,b) => { const value = element("bdi","",number(a)+" / "+number(b)); value.dir="ltr"; return value; };
    const head = element("div","tree-head");
    let lessonCount = number(all.length)+" "+(all.length === 1 ? "lesson" : "lessons");
    if (lang === "ar") {
      const form = new Intl.PluralRules("ar").select(all.length);
      lessonCount = form === "one" ? "درس واحد" : form === "two" ? "درسان" : number(all.length)+(form === "few" ? " دروس" : " درسًا");
    }
    head.append(icon("folder"),element("span","",t.course),element("small","",lessonCount));
    const close = element("button","tool tree-toggle","×");
    close.type="button"; close.dataset.action="close-menu";
    close.setAttribute("aria-label",lang==="ar" ? "إغلاق الفهرس" : "Close course index");
    head.append(close);
    const list = element("nav","tree-list"); list.setAttribute("aria-label",t.course);
    for (const [i,group] of chapters.entries()) {
      const details = element("details","chapter"); details.dataset.id = group.id;
      const containsActive = group.lessons.some(lesson => lesson.id === active);
      details.open = (newLesson && containsActive) || (previous.get(group.id) ?? containsActive);
      const summary = element("summary"); const badge = element("small"); badge.append(fraction(count(group),group.lessons.length));
      const numberTag = element("bdi","",String(i+1).padStart(2,"0")+"."); numberTag.dir="ltr";
      summary.append(element("span","chevron"),icon("folder",folders[i%folders.length]),numberTag,element("span","",group.title[lang]),badge);
      const entries = element("ul");
      for (const lesson of group.lessons) {
        const row = element("li"); const link = element("a","lesson-link"); link.href = lesson.href;
        if (lesson.id === active) link.setAttribute("aria-current","page");
        const done = completed.has(lesson.id);
        if (done) link.setAttribute("aria-label",lesson.title[lang]+", "+t.reached);
        link.append(icon(done ? "done" : "file"),element("span","",lesson.title[lang]));
        if (onNavigate) link.addEventListener("click", event => {
          if (event.button || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
          event.preventDefault(); onNavigate(lesson);
        });
        row.append(link); entries.append(row);
      }
      details.append(summary,entries); list.append(details);
    }
    const progress = element("details","tree-progress"); progress.open = progressOpen;
    const summary = element("summary","",t.progress);
    summary.append(fraction(all.filter(lesson=>completed.has(lesson.id)).length,all.length),element("span","chevron"));
    const breakdown = element("ul");
    for (const group of chapters) {
      const line = element("li","",group.title[lang]+" "); line.append(fraction(count(group),group.lessons.length)); breakdown.append(line);
    }
    progress.append(summary,breakdown); host.classList.add("course-tree"); host.dataset.active = active;
    host.replaceChildren(head,list,progress); list.scrollTop = scrollTop;
  }
  function timeline(host,{steps,index,lang,onStep}) {
    const track = element("ol","step-track");
    steps.forEach((s,i) => {
      const item = element("li"); const button = element("button"); button.type="button";
      if (i === index) button.setAttribute("aria-current","step");
      if (i < index) item.classList.add("past");
      button.append(element("span","dot",(i+1).toLocaleString(lang)),element("span","",s.label[lang]));
      button.onclick = () => { onStep(i); host.querySelector('[aria-current="step"]')?.focus({preventScroll:true}); };
      item.append(button); track.append(item);
    });
    host.replaceChildren(track);
    const selected = track.querySelector('[aria-current="step"]');
    if (selected && track.scrollWidth > track.clientWidth) {
      const r = selected.getBoundingClientRect(), box = track.getBoundingClientRect();
      if (r.left < box.left || r.right > box.right) track.scrollBy({left:r.left+r.width/2-box.left-box.width/2});
    }
  }
  function guide({lang, index, steps, goals = [], onBack, onNext, nextTitle, previousAvailable}) {
    const current = steps[index];
    const slot = name => document.querySelector('[data-slot="'+name+'"]');
    const n = value => value.toLocaleString(lang);
    const position = lang === "ar" ? "الخطوة "+n(index+1)+" من "+n(steps.length) : "Step "+n(index+1)+" of "+n(steps.length);
    slot("position").textContent = position;
    slot("guide-position").textContent = position;
    slot("step-role").textContent = current.role[lang];
    slot("step-title").textContent = current.title[lang];
    slot("explanation").replaceChildren(...current.paragraphs.map(p => element("p","",p[lang])));
    const callout = slot("callout");
    callout.hidden = !current.callout;
    callout.replaceChildren();
    if (current.callout) {
      callout.dataset.kind = current.callout.kind;
      callout.append(element("strong","",current.callout.title[lang]),element("p","",current.callout.body[lang]));
    }
    const changes = slot("changes");
    changes.replaceChildren();
    if (current.changes?.length) {
      const items = element(current.changesOrdered ? "ol" : "ul");
      for (const change of current.changes) {
        const item = element("li");
        item.append(element("bdi","",change[lang]));
        items.append(item);
      }
      if (!current.changesOrdered) changes.append(element("strong","",lang === "ar" ? "ما الذي تغيّر" : "What changed"));
      changes.append(items);
    }
    const notes = callout.closest(".step-notes");
    if (notes) notes.hidden = callout.hidden && !changes.childElementCount;
    const outcomeList = slot("goal-list");
    const outcomes = outcomeList.closest(".outcomes");
    if (outcomes) outcomes.hidden = goals.length === 0;
    outcomeList.replaceChildren(...goals.map(goal => {
      const item = element("li");
      const checked = index >= goal.at;
      const mark = element("span","goal-mark",checked ? "✓" : "");
      mark.setAttribute("aria-hidden","true");
      const status = lang === "ar" ? (checked ? "تم تناوله" : "قادم") : (checked ? "Covered" : "Upcoming");
      item.append(mark,element("span","sr-only",status+" "),element("span","",goal.title[lang]));
      return item;
    }));
    const back = document.querySelector('[data-action="back"]'), next = document.querySelector('[data-action="next"]');
    back.textContent = lang === "ar" ? "→ رجوع" : "← Back"; back.disabled = !previousAvailable; back.onclick = onBack;
    next.textContent = nextTitle[lang]; next.onclick = onNext;
  }
  function controls({onSearch,onReplay,onPause,onMove}) {
    const action = name => document.querySelector('[data-action="'+name+'"]');
    const stage = document.querySelector(".stage"), drawer = document.querySelector("#course-tree");
    const menu = action("menu"), expand = action("expand"), pause = action("pause");
    const scrim = element("button","drawer-scrim"); scrim.type="button"; scrim.tabIndex=-1; scrim.hidden=true;
    const compact = matchMedia("(max-width:1000px)");
    drawer?.after(scrim);
    if (menu) menu.hidden = !drawer;
    let paused = false;
    function isOverlayOpen() {
      return compact.matches && drawer?.hasAttribute("data-open");
    }
    function syncIndex() {
      if (!drawer || !menu) return;
      const open = compact.matches ? isOverlayOpen() : !drawer.hasAttribute("data-collapsed");
      menu.setAttribute("aria-expanded",String(open));
      scrim.hidden = !isOverlayOpen();
    }
    function closeDrawer(restore=true) {
      if (!drawer) return;
      drawer.removeAttribute("data-open");
      syncIndex();
      if (restore) menu?.focus();
    }
    function closeStage() {
      stage.classList.remove("expanded-stage"); expand.setAttribute("aria-expanded","false"); expand.focus();
    }
    function refresh() {
      const lang=document.documentElement.lang, t=labels[lang];
      pause.querySelector("span").textContent = paused ? t.resume : t.pause;
      pause.querySelector("b").textContent = paused ? "▷" : "Ⅱ";
      pause.setAttribute("aria-pressed",String(paused));
      const close = lang === "ar" ? "إغلاق" : "Close";
      scrim.setAttribute("aria-label",close);
      expand.setAttribute("aria-label",stage.classList.contains("expanded-stage") ? close : t.expand);
    }
    if (drawer && menu) {
      function collapseIndex() {
        drawer.setAttribute("data-collapsed","");
        syncIndex();
        menu.focus();
      }
      menu.onclick = () => {
        if (compact.matches) {
          if (isOverlayOpen()) return closeDrawer();
          drawer.setAttribute("data-open","");
          syncIndex();
          drawer.querySelector('[data-action="close-menu"]')?.focus();
        } else if (drawer.hasAttribute("data-collapsed")) {
          drawer.removeAttribute("data-collapsed");
          syncIndex();
        } else {
          collapseIndex();
        }
      };
      scrim.onclick = () => closeDrawer();
      drawer.addEventListener("click", e => {
        if (e.target.closest('[data-action="close-menu"]')) {
          if (compact.matches) closeDrawer();
          else collapseIndex();
        } else if (isOverlayOpen() && e.target.closest("a") && !e.ctrlKey && !e.metaKey && !e.shiftKey && !e.altKey) {
          closeDrawer();
        }
      });
      compact.addEventListener("change", () => {
        const focusInIndex = drawer.contains(document.activeElement);
        closeDrawer(focusInIndex && (compact.matches || drawer.hasAttribute("data-collapsed")));
      });
      syncIndex();
    }
    expand.onclick = () => {
      if (stage.classList.contains("expanded-stage")) closeStage();
      else { stage.classList.add("expanded-stage"); expand.setAttribute("aria-expanded","true"); }
      refresh();
    };
    action("search").onclick = onSearch; action("replay").onclick = onReplay;
    pause.onclick = () => { paused=!paused; onPause(paused); refresh(); };
    document.addEventListener("keydown", e => {
      if (e.defaultPrevented) return;
      const overlay=isOverlayOpen() ? drawer : stage.classList.contains("expanded-stage") ? stage : null;
      if (overlay && e.key==="Escape") {
        e.preventDefault(); if (overlay===drawer) closeDrawer(); else closeStage(); refresh(); return;
      }
      if (overlay && e.key==="Tab") {
        const focusable=[...overlay.querySelectorAll("a[href],button:not(:disabled),summary,input,select,[tabindex='0']")].filter(node=>node.getClientRects().length);
        if (focusable.length && document.activeElement===(e.shiftKey?focusable[0]:focusable.at(-1))) {
          e.preventDefault(); (e.shiftKey?focusable.at(-1):focusable[0]).focus();
        }
        return;
      }
      if (isOverlayOpen() || document.querySelector("dialog[open]")) return;
      if ((e.ctrlKey||e.metaKey) && e.key.toLowerCase()==="k") { e.preventDefault(); onSearch(); return; }
      if (e.ctrlKey||e.metaKey||e.altKey||e.target.closest("input,select,textarea,[contenteditable=true]")) return;
      if (e.key.toLowerCase()==="r") { e.preventDefault(); onReplay(); }
      if (e.code==="Space" && !e.target.closest("button,a,summary")) { e.preventDefault(); pause.click(); }
      if (e.key==="ArrowLeft"||e.key==="ArrowRight") {
        e.preventDefault(); const next=document.documentElement.dir==="rtl"?"ArrowLeft":"ArrowRight"; onMove(e.key===next?1:-1);
      }
    });
    return {refresh,closeDrawer};
  }
  function codeBlock(source, language) {
    const block = element("pre", "code-block");
    const code = element("code", "", source);
    block.dir = "ltr";
    block.append(code);
    if (language && globalThis.hljs?.getLanguage(language)) {
      code.classList.add("language-" + language);
      globalThis.hljs.highlightElement(code);
    }
    return block;
  }
  function sceneX(distanceFromStart, width, minX = 0) {
    const rtl = document.documentElement.dir === "rtl";
    return minX + (rtl ? width - distanceFromStart : distanceFromStart);
  }
  return {preferences,tree,timeline,guide,controls,codeBlock,sceneX};
})();
