---
name: visual-learning-studio
disable-model-invocation: true
description: Build a runnable visual learning website or interactive lesson for a technical or nontechnical subject. Use for requests to turn a topic into a step-through course, a hands-on learning path, or a teaching experience inspired by Designed to Scale. Also applies to Arabic requests for a كورس بصري تفاعلي or مسار تعليمي تفاعلي.
---

# Visual Learning Studio

Build a working learning experience in Arabic and English. Use the requested language for the first visit. Every lesson and course uses the supplied Designed to Scale shell, light and dark palettes, top language and theme controls, and bundled fonts. For a plan request, deliver a curriculum and a worked lesson storyboard. For a course, deliver the full learning path and a final application.

## Design the path

1. Define what a learner will be able to **do** at the end. Infer the starting level from the request, or use an approachable beginner entry. Choose a concrete situation the learner will revisit. Sketch the final task first and work backwards to its prerequisites.
2. Give each lesson a question, the prior idea it uses, an observable outcome, and a new case where the learner must apply it. Group lessons where the learner's task changes, for example from reading a model, to changing it, to diagnosing a surprising result. Put the minimum vocabulary beside its first use.
3. Connect lessons by consequence. The last step resolves the opening question and introduces a limit or question that motivates the next lesson. A final case should combine earlier decisions under a new constraint. Fit the number of lessons and steps to the topic and requested scope.

Ground the examples in the learner's reason for studying. Give each short lesson one practical win and identify the evidence that would show it. Check domain claims against primary material and link a relevant source near the recap. Introduce one new difficulty at a time. After a worked example, hide the result and let the learner predict from memory, inspect the evidence and try again. In a later lesson bring that decision back with a changed case. Use Practice to mix up related decisions that learners tend to confuse. Build a bilingual glossary and a compact reference sheet from terms and decisions actually taught.

## Build each lesson around evidence

Storyboard the hard part before styling the course. For each meaningful transition record **what stays fixed, what changes, what the learner sees, and what they can infer**. Choose a representation using [the interaction guide](references/interaction-guide.md) when the subject, controls or form of evidence are unclear.

- Open in a concrete situation with a visible initial state. Establish a baseline the learner can remember. Walk through a mechanism in small causal steps with stable positions and labels. Introduce a complication or counterexample, then let the learner resolve it using the model.
- Give the learner something consequential to do. They might replay a transition, choose an input, move a component, compare interpretations, or predict which outcome a change will produce. Pick the smallest gesture that exposes the lesson's idea. A step button can be enough when the sequence itself is the subject.
- Couple the diagram, annotations, measurements and explanation to the same state. Name the changed object and show the old and new value, relation or interpretation. Use real units, explicit assumptions and calculated values where appropriate. For qualitative subjects, show the evidence in the work itself.
- Include a transfer check when it serves the outcome. Give an unfamiliar example, invite a choice, and explain it using visible evidence. Provide a way to revise or replay. Keep lesson navigation available. Track arrival at the recap separately from demonstrated skill whenever both are shown.

## Make the workspace

Start each build by reading [the shell integration guide](references/course-shell.md). Copy its HTML fragment, CSS, JavaScript and licensed fonts into the output, or port the components faithfully to the user's framework. Reuse them across all topics. Use [the visual study](references/reference-study-ar.md) for examples of how the original teaches. Write original content and diagrams.

- Open in a usable lesson. On desktop put the colored folder tree, central lesson stage and separate guide column on one row. Use the supplied file icons, connectors, counters and current-row treatment for every course. A standalone lesson can omit the tree. Retain the same materials, bilingual controls, scene, timeline and guide.
- On narrow screens, move the tree into a drawer and keep the stage, active step and next/back controls reachable. Give dense scenes an expanded view. Keep interactive labels readable without horizontal page scrolling. Use keyboard-operable controls, visible focus, and a reduced-motion or discrete-state equivalent. Explain the state in text as well as color.
- Every multi-lesson course has Learn, Practice, Design Lab and Cheatsheets in the top bar. Implement a working activity for each using the same lesson data. Provide durable step URLs, local resume and concept search. For a single lesson, keep its prediction, experiment and recap accessible within the lesson.
- Every output offers exactly العربية and English. Translate all learner-facing content and accessible labels. Apply IBM Plex Sans Arabic to all Arabic UI and diagram text and JetBrains Mono to the English UI and code. Both top-bar switches work on small screens and preserve the current lesson, step, inputs and progress.

## Verify through the learner's route

Run the site. Enter from the normal starting screen and finish a lesson. Change a meaningful input or case, observe the predicted consequence and compare it to the explanation. Move backwards, replay and jump directly to a later step. A given step and input must reconstruct the same scene and readouts regardless of the path used to reach them. Check a new case against the lesson objective.

For courses, traverse chapter boundaries, test all four modes and confirm every curriculum entry opens substantive content. Test the language × theme × viewport matrix and the interaction checks in the integration guide. Report what ran and any remaining limits.
