# Build from the shared course shell

The supplied files are production inputs. Bring them into every generated course. Use the same shell even when the topic has no technical vocabulary. A framework port must keep its reading order, components, proportions, colors and behavior.

| File | How to use it |
| --- | --- |
| [lesson-shell.html](../assets/lesson-shell.html) | Insert the fragment in the page body. Fill each content slot from real lesson data. Wire every action. |
| [studio.css](../assets/studio.css) | Load once. Use its named colors in cards, controls, SVGs, canvas and overlays. Layout follows document direction. |
| [studio.js](../assets/studio.js) | Load as a classic script before the course script. Use the preference controls, folder tree and timeline. |
| [Highlight.js 11.11.1](../assets/highlight/highlight.min.js) | For courses with code, load the bundled classic script before rendering any snippets. Include its adjacent LICENSE. Embed it locally in single-file builds. |
| [fonts](../assets/fonts/) | Keep the relative paths or embed the fonts used in a single-file HTML build. Ship the corresponding license and attribution files with the output. Code blocks must load the bundled Nerd Font offline. |

## Bind the shell

Use `host.replaceChildren(Studio.codeBlock(snippet.source, snippet.language))` when rendering source, including after a step, input or language change. For example, pass `"javascript"` for a Node.js example even when the lesson text is Arabic. For a grammar outside the common bundle, include its matching Highlight.js language module locally before rendering. Plain output and logs can use `"plaintext"`. In a framework or static build, generate equivalent highlighted tokens with the same palette. Verify that the code element's text exactly matches the formatted source and the code surface, plain text and syntax colors keep the dark-editor palette when the page switches themes. Long lines scroll inside the block.

Keep the shared type sizes and weights when porting the shell or adding views. Use bold 1rem text for lesson objectives, step explanations and outcomes. Use bold .875rem text for breadcrumbs, timeline labels, legend keys and short labels. Use the same text hierarchy in custom views. Let translations wrap. Mark code blocks with `<pre><code>` or `.code-block`; make syntax tokens inherit the code family. At handoff, check these roles on a narrow screen in both languages and themes. Check a real code block with the network disconnected and confirm the bundled face loads and long lines scroll inside the block.

Keep one stable ID per chapter, lesson, step and concept across both languages. A localized title has the shape `{ar, en}`. Chapters contain `{id, title, lessons}`. Each lesson has `{id, title, href}` with a real first-step URL. Each step has a localized `label`, teaching role, explanation, visible change, scene state and any relevant outcome IDs. Use the actual course router and a single experiment model. Keep language and theme outside that model.

```js
const slot = name => document.querySelector('[data-slot="' + name + '"]');
Studio.preferences(slot('preferences'), {
  key: course.id,
  initialLanguage: course.startLanguage,
  onChange({lang, theme}) {
    renderLessonAndControls({lang, theme, state});
    Studio.tree(document.querySelector('#course-tree'), {
      chapters: course.chapters, active: state.lesson.id,
      completed: state.reachedRecap, lang, onNavigate: openLesson
    });
    Studio.timeline(slot('timeline'), {
      steps: state.lesson.steps, index: state.step, lang, onStep: openStep
    });
  }
});
```

Inside the lesson renderer, call `Studio.guide({lang, index, steps, goals, onBack, onNext, nextTitle, previousAvailable})`. Each step provides localized `role`, `title`, `label` and a list of localized `paragraphs`. An optional `callout` holds a kind (idea, tip or warning), localized title and body. Optional `changes` are localized strings. Set `changesOrdered: true` for a sequence the learner must trace in order. Each goal has a localized title and a zero-based `at` step. Supply the localized next destination, including the following lesson at a chapter boundary.

The functions beginning with `render` and `open`, the course and the state above are supplied by the generated site. Render the tree, timeline and guide on route and progress changes too. Mount preferences once into its stable host. Localize the document title, navigation, menu and search results, keyboard hints, empty states, diagrams, chart labels, practice feedback, progress text and glossary explanations. Support search aliases from both languages and route matches to the exact step. Set localized accessible names on icon-only buttons. Load fonts before measuring canvas labels, and redraw on language or theme changes.

Mount `const controls = Studio.controls({onSearch, onReplay, onPause, onMove})` once, before preferences. Supply the course search dialog, scene restart, playback state setter and a bounded step navigator. Call `controls.refresh()` after language or scene changes. The helper owns the menu drawer, focus return, expanded view and keyboard shortcuts. Set real hrefs and active state on the four mode links and home. Connect those links to the course's populated views.

## Match the two reference screens

- **Top bar.** On desktop use a compact 54 px masthead with the topic mark, Learn / Practice / Design Lab / Cheatsheets, course search with Ctrl/Cmd+K, language and sun/moon controls. For full courses implement all four destinations. Practice accepts predictions with explanatory feedback. The lab lets the learner change an input and see the effect. Cheatsheets gives a compact, printable bilingual reference and links back to relevant steps. Use the project's own name and actual author credits where available.
- **Curriculum.** Use the supplied tree. Its heading shows a folder, Course and the actual lesson count. Chapters have disclosure chevrons, two-digit numbers, colored folder icons and completed/total. Children have thin elbow connectors and page icons with a folded corner. Open the active chapter on entry. Use a rounded sage row with a hard shadow on the active file, checked icons on completed files, and the expandable progress summary anchored at the foot. Derive counts from data. The progress box follows the scrolling rows even in a short window.
- **Center.** Put the chapter/lesson breadcrumb, compact title, and the time, level and step-count badges above the stage. Use a faint isometric grid, outlined topic-specific objects, attached labels, purposeful movement and readable legend marks. For an abstract subject use a legible source text, score or table inside the same stage. Keep the stage visually dominant. In the light theme use warm paper and dark ink, in the dark theme warm charcoal and ivory. Keep matched entity colors meaningful in both.
- **Inside the stage.** Place the relevant state readouts at the top leading edge, Replay and Pause/Resume opposite, and short symbol keys in the legend when needed. Keep code and actual output together. Put instructions, trace interpretations and timing caveats in the guide. Make Replay restart the current transition, Pause hold playback, and Resume continue it. A stepwise scene can replay a discrete reveal. Use an equivalent still state for reduced motion. Distinguish a condition by shape, text or symbol as well as color. Reserve the measurement strip for values the lesson actually changes or explains.
- **Below the stage.** Show “In this lesson”, current/total count and connected numbered circles with short labels. Enable direct jumps and keyboard step navigation. Highlight completed positions, current position and upcoming steps distinctly. Keep the current node in view when the rail scrolls.
- **Guide column.** Place the step counter and role badge above a short heading, one or two paragraphs, and a contextual tip, warning or key idea when applicable. Show a concise “What changed” list on state transitions. Anchor Back and the named Next destination at the foot, followed by shortcut hints. Place the lesson question in the guide when it adds to the step title. Group optional observations, assumptions and feedback in the single labeled Notes section under the explanation. Use `callout` for a tip or warning and `changes` for observations about the current state. Refresh these on step or input changes. Use a bordered native disclosure labeled ملاحظات or Notes, initially open. Keep essential instructions above it. Preserve the open or closed state when updating its contents. Leave both fields empty to hide the box. A separate “You'll learn” card appears only for distinct lesson goals and checks them off when their steps are reached. Use realistic reading time and derive counts from course data.
- **Small screens.** Turn the tree into an accessible drawer with a close action and focus return. Keep language, theme and search reachable. Put the guide and its controls before the stage, offer expanded scene view, and provide room for sticky controls plus the device safe area. The last line of feedback and the next control must be readable without overlapping. Mirror the interface in Arabic. Keep commands, paths, hashes, formulas and directional axes isolated in their natural direction.

## Course index

Keep the index at the reading end with its toggle in the top bar and a close button inside. Open it by default on desktop. Closing it removes its column and gap and widens the guide and notes by that amount. Keep the scene and timeline at their current width. Preserve the selected lesson, step, chapter expansion and progress when toggling. On smaller screens the index starts closed and opens as a drawer from the reading end.

Check both toggle buttons on desktop in each language. Compare the widths of the guide and stage before and after collapse. Check that the toggle exposes the current state, closing returns focus to the toggle, and the compact drawer closes on Escape or lesson selection. Resize across the breakpoint with the drawer open, and verify the desktop layout and toggle agree.

## Acceptance at handoff

Read a step in order from the guide. Check that its question, instruction and feedback each appear once and all remaining scene labels identify an object, value, symbol or control. Fold and unfold Notes with the keyboard. Switch to a step without notes and confirm the notes panel disappears. Inspect the same substantive step in English and Arabic, each in light and dark, on desktop and phone. Check the computed font and a loaded font face for Arabic prose and a diagram label. Resize with the drawer open. Check focus return, long translations, overflow, font files in an offline build, graphic contrast and the guide's last line above the bottom controls. Compare the desktop geometry with the supplied layout. At desktop width check the actual panel positions: Arabic has the guide on the right, scene in the middle and tree on the left. English has the guide on the left, scene in the middle and tree on the right. On tablet the guide stays at reading start and the tree opens from the opposite edge. On phones the guide precedes the scene. Exercise Learn, Practice, Design Lab and Cheatsheets after switching languages in place. For each mode, apply the same rule to its primary prompt, experiment or reference content and its secondary navigation. Preserve the intrinsic direction of code and axes.

Switch language and theme mid-experiment, then reload. Confirm route, selected input where retained by the course, progress and saved preferences behave as intended. Run the same transition by Next, Back, direct link and Replay. Pause mid-transition and verify readouts agree with the displayed scene. Follow a search result in each language, switch to practice, make a wrong prediction, retry, then follow the reference link back to the lesson.

### Arabic terminology review for programming courses

Use the course glossary as the source of the canonical English spelling for each programming term. Use that spelling in both versions. Explain a term in Egyptian Arabic at its first use and in the Arabic glossary definition. Keep terms such as `call stack`, `callback`, `event loop`, and `Promise` in English. For example, write “الـ call stack بيتابع الدوال اللي شغّالة دلوقتي.” Use the same name throughout the course.

Review all Arabic content before handoff, including chapter and lesson names, steps, notes, diagram labels, practice prompts and feedback, lab controls, cheat sheets, glossary entries, and search results. Search the authored data for translated or transliterated versions of terms in the glossary and replace them with their canonical names. Verify that the English term is searchable while the site is in Arabic. In RTL prose, isolate mixed-direction names where needed with `<bdi dir="ltr" lang="en">` or an equivalent in the renderer. Check a phrase with a multiword term and nearby punctuation on a narrow screen.
