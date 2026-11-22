---
name: visual-learning-studio
disable-model-invocation: true
description: Build a runnable visual learning website or interactive lesson for a technical or nontechnical subject. Use for requests to turn a topic into a step-through course, a hands-on learning path, or a teaching experience inspired by Designed to Scale. Also applies to Arabic requests for a كورس بصري تفاعلي or مسار تعليمي تفاعلي.
---

# Visual Learning Studio

Build a working learning experience in Arabic and English. Use the requested language for the first visit. Every lesson and course uses the supplied Designed to Scale shell, light and dark palettes, top language and theme controls, and bundled fonts. For a plan request, deliver a curriculum and a worked lesson storyboard. For a course, deliver the full learning path and a final application.

## Interview first, then ask for approval

For every new learning path or standalone lesson, begin with an interview in the user's language. Keep the interview and proposal in chat. Until the user explicitly approves the specific proposal, wait before creating or changing any files, including notes, outlines, mockups, starter code and previews.

1. Explain briefly that chat is for planning and the teaching will happen in the interactive site. For any subject, choose one unresolved decision about the path, such as where to start, which foundations to include, or what kind of practice fits the goal. Use what the learner has already said to write one short, everyday question whose answer would change that decision. Ask about an experience they can report or a preference they can express without knowing the new subject. For example, prior programming experience might change a JavaScript introduction, while access to a camera might change a photography lab. These examples illustrate how to choose a question. Generate the wording and follow-up from this learner's context. When the next answer would make no difference to the plan, present the proposal.
2. Accept the learner's own account, including “no”, “a little” and “I'm not sure”. Ask about a prerequisite only if its answer would change the path. If a real gap emerges, offer the three routes below and wait for their choice. For a course made for others, ask about the audience. Keep quizzes, predictions, code traces, worked examples and explanations of the target concept inside the approved website. Never use a chat exercise to verify someone's level.
3. Clarify the goal or constraints only when they affect the proposal. Offer familiar choices such as interview prep, a work project or general curiosity. As soon as the starting point and goal are clear enough, propose the path. Avoid making the learner design their own curriculum or sit through a fixed questionnaire.
4. Summarize what the learner told you and show the proposed lessons in order, beginning with the orientation described below. Say briefly what each lesson will cover and where practice fits. For a single lesson, show its steps. If the learner says a topic needs an introduction, revise the outline in chat and reserve the introduction itself for the site.
5. Ask whether to build this exact proposal or change it, then stop. Build only after explicit approval of the current proposal. After revisions, ask again. For a plan-only request, finish with the agreed plan in chat.

### When a prerequisite is missing

Interrupt the interview before proposing lessons. Name the specific missing skill and give one example of where the learner will need it. Distinguish an essential dependency for their goal from useful background. Offer the following three choices together in the learner's language, using their actual topics. Ask which route they want, then end the turn and wait.

1. **Switch the goal.** Make the prerequisite the subject of this course. The originally requested subject can be a separate course later.
2. **Keep the goal and add a short introduction.** Put only the missing foundations in a small opening module inside the requested course. Name the specific skills this module would cover and the first target lesson that uses them.
3. **Start the requested subject directly.** Explain the practical trade-off once. If they choose this route, start the outline with the target subject and honor their choice throughout.

For example, when a TypeScript learner says JavaScript functions and objects are new to them, explain that a lesson on typing function parameters assumes they can already follow what the function does. Offer a JavaScript course first, a short module on the JavaScript used in their TypeScript exercises, or TypeScript from lesson one. Choose only after hearing their preference.

Carry the selected route into the interview summary and ordered lesson proposal. Choosing a route settles the scope. Building still requires separate explicit approval of the actual proposal.

## Design the path

Make lesson one in both the proposal and the built course an introduction to the chosen subject. Name the subject in its title. Explain in plain language what it is, what people needed before it existed, how it arose, and what people use it for today. Use a verified historical detail when it explains the purpose. Adjust the depth to the interview. If the learner skipped prerequisites, introduce the chosen subject directly. In a course with an agreed prerequisite module, first orient the learner to the target and explain where that module fits.

For a beginner JavaScript path, open with “What is JavaScript, and why did the web need it?” A visual can show what changes when a page responds to a click. Save declaring a variable for a later lesson. A reader should be able to explain what the subject is and why someone would use it before the first coding task.

1. Use the confirmed starting point and approved goal. Choose a situation the learner will revisit. Work backwards from the final task to the prerequisites the interview showed they need.
2. Give each lesson a question, the prior idea it uses, an observable outcome, and a new case where the learner must apply it. Group lessons where the learner's task changes, for example from reading a model, to changing it, to diagnosing a surprising result. Put the minimum vocabulary beside its first use.
3. Connect lessons by consequence. The last step resolves the opening question and introduces a limit or question that motivates the next lesson. A final case should combine earlier decisions under a new constraint. Fit the number of lessons and steps to the topic and requested scope.

Ground the examples in the learner's reason for studying. Give each short lesson one practical win and identify the evidence that would show it. Check domain claims against primary material and link a relevant source near the recap. Introduce one new difficulty at a time. After a worked example, hide the result and let the learner predict from memory, inspect the evidence and try again. In a later lesson bring that decision back with a changed case. Use Practice to mix up related decisions that learners tend to confuse. Build a bilingual glossary and a compact reference sheet from terms and decisions actually taught.

## Build each lesson around evidence

Storyboard the hard part before styling the course. For each meaningful transition record **what stays fixed, what changes, what the learner sees, and what they can infer**. Choose a representation using [the interaction guide](references/interaction-guide.md) when the subject, controls or form of evidence are unclear.

- In a standalone lesson or a later lesson that introduces a concept, first name it, explain its purpose and connect it to what the learner already understands. Then show a concrete situation, walk through the mechanism and invite the learner to try it. Cover the subject's broader history in its opening lesson.
- Give the learner something consequential to do. They might replay a transition, choose an input, move a component, compare interpretations, or predict which outcome a change will produce. Pick the smallest gesture that exposes the lesson's idea. A step button can be enough when the sequence itself is the subject.
- Couple the diagram, annotations, measurements and explanation to the same state. Name the changed object and show the old and new value, relation or interpretation. Use real units, explicit assumptions and calculated values where appropriate. For qualitative subjects, show the evidence in the work itself.
- Include a transfer check when it serves the outcome. Give an unfamiliar example, invite a choice, and explain it using visible evidence. Provide a way to revise or replay. Keep lesson navigation available. Track arrival at the recap separately from demonstrated skill whenever both are shown.

## Make the workspace

Start each build by reading [the shell integration guide](references/course-shell.md). Copy its HTML fragment, CSS, JavaScript and licensed fonts into the output, or port the components faithfully to the user's framework. Reuse them across all topics. Use [the visual study](references/reference-study-ar.md) for examples of how the original teaches. Write original content and diagrams.

- Open in a usable lesson. Use reading order across Learn, Practice, Design Lab and Cheatsheets. Put the primary explanation or task and its controls at the reading start, the related scene or work area in the middle, and any lesson index or auxiliary navigation at the far end. On desktop the guide is on the right in Arabic and on the left in English. On phones stack the task before its work area and use a drawer for the index. Keep DOM and keyboard order aligned with the reading sequence. Use the supplied file icons, connectors, counters and current-row treatment for every course. A standalone lesson can omit the tree. Retain the same materials, bilingual controls, scene, timeline and guide.
- On narrow screens, move the tree into a drawer and keep the stage, active step and next/back controls reachable. Give dense scenes an expanded view. Keep interactive labels readable without horizontal page scrolling. Use keyboard-operable controls, visible focus, and a reduced-motion or discrete-state equivalent. Explain the state in text as well as color.
- Every multi-lesson course has Learn, Practice, Design Lab and Cheatsheets in the top bar. Implement a working activity for each using the same lesson data. Provide durable step URLs, local resume and concept search. For a single lesson, keep its prediction, experiment and recap accessible within the lesson.
- Every output offers exactly العربية and English. Translate all learner-facing content and accessible labels. Use IBM Plex Sans Arabic for Arabic UI and diagrams, JetBrains Mono for English UI, and the bundled JetBrainsMono Nerd Font Mono for code blocks in both languages. Keep lesson explanations, objectives, captions and step labels bold and readable in every mode. Both top-bar switches work on small screens and preserve the current lesson, step, inputs and progress.

## Verify through the learner's route

Run the site. Enter from the normal starting screen and finish a lesson. Change a meaningful input or case, observe the predicted consequence and compare it to the explanation. Move backwards, replay and jump directly to a later step. A given step and input must reconstruct the same scene and readouts regardless of the path used to reach them. Check a new case against the lesson objective.

For courses, traverse chapter boundaries, test all four modes and confirm every curriculum entry opens substantive content. Test the language × theme × viewport matrix and the interaction checks in the integration guide. Report what ran and any remaining limits.
