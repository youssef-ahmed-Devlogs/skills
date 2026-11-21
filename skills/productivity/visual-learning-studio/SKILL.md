---
name: visual-learning-studio
disable-model-invocation: true
description: Build a runnable visual learning website or interactive lesson for a technical or nontechnical subject. Use for requests to turn a topic into a step-through course, a hands-on learning path, or a teaching experience inspired by Designed to Scale. Also applies to Arabic requests for a كورس بصري تفاعلي or مسار تعليمي تفاعلي.
---

# Visual Learning Studio

Build a working learning experience in Arabic and English. Use the requested language for the first visit. Every lesson and course uses the supplied Designed to Scale shell, light and dark palettes, top language and theme controls, and bundled fonts. For a plan request, deliver a curriculum and a worked lesson storyboard. For a course, deliver the full learning path and a final application.

## Interview first, then ask for approval

For every new learning path or standalone lesson, begin with an interview in the user's language. Keep the interview and proposal in chat. Until the user explicitly approves the specific proposal, wait before creating or changing any files, including notes, outlines, mockups, starter code and previews.

1. Ask one focused question and wait for the answer. Start with the learner's real goal or the most important gap in what they have already told you. If the initial brief is detailed, confirm the specific starting point with them. Carry answers forward between turns.
2. Establish what the learner can already do unaided, what they have tried, and exactly where they get stuck. Ask for a concrete example. If the boundary is unclear, offer one small prediction or task in chat and discuss their reasoning before choosing the starting lesson. Accept a clear account of starting from zero. For a course made for others, ask the requester about the intended audience and confirm any unknowns with them. A topic name or a level label alone never establishes prerequisites. Compare that evidence with the skills used by the requested tasks. When a prerequisite is missing, pause here for the learner's choice as described below. If it is simply unmentioned, ask before treating it as a gap.
3. Ask about the time available, desired depth, type of practice and constraints that affect this course. Let earlier answers determine the next question. A recommendation can help choose the scope or format. The learner supplies the evidence of their ability.
4. Present two things in chat: what you understood (goal, evidence of current skills, gaps and constraints), and the proposed path (starting point, ordered lesson titles, what the learner will do or demonstrate in each, and the final application). Explain briefly why the order fits this learner. For one lesson, propose its steps and practice instead.
5. End the proposal by asking whether to build this exact version or change it. Stop and wait. An explicit yes to the current proposal authorizes the build. A diagnostic answer, an earlier request to build, silence, or a request for revisions does not. For revisions, present the updated proposal and ask again. For a plan-only request, finish with the agreed plan in chat.

### When a prerequisite is missing

Interrupt the interview before proposing lessons. Name the specific missing skill and give one example of where the learner will need it. Distinguish an essential dependency for their goal from useful background. Offer the following three choices together in the learner's language, using their actual topics. Ask which route they want, then end the turn and wait.

1. **Switch the goal.** Make the prerequisite the subject of this course. The originally requested subject can be a separate course later.
2. **Keep the goal and add a short introduction.** Put only the missing foundations in a small opening module inside the requested course. Name the specific skills this module would cover and the first target lesson that uses them.
3. **Start the requested subject directly.** Explain the practical trade-off once. If they choose this route, start the outline with the target subject and honor their choice throughout.

For example, when a TypeScript learner says JavaScript functions and objects are new to them, explain that a lesson on typing function parameters assumes they can already follow what the function does. Offer a JavaScript course first, a short module on the JavaScript used in their TypeScript exercises, or TypeScript from lesson one. Choose only after hearing their preference.

Carry the selected route into the interview summary and ordered lesson proposal. Choosing a route settles the scope. Building still requires separate explicit approval of the actual proposal.

## Design the path

1. Use the confirmed starting point and approved goal. Choose a situation the learner will revisit. Work backwards from the final task to the prerequisites the interview showed they need.
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
