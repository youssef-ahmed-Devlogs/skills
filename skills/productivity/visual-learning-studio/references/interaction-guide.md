# Choose the learner's experiment

Start with the question a learner should answer by looking at the stage. Pick the representation that makes the discriminating evidence easy to see.

| Learning question | Stage and learner action | Observable evidence |
| --- | --- | --- |
| Where did this item go? | Trace a single item through a flow. Step, rewind or pause. | The same labeled item changes location. Completed legs stay visible and totals update. |
| Why did the program produce that value? | Synchronize a short code listing, highlighted operation and memory/table view. Change an input and step again. | The changed value appears at the line that caused it. The explanation points to that value. |
| Which model fits these observations? | Keep one data set and switch hypotheses, or reveal observations one by one. | Indicate the exact observations each hypothesis explains or fails to explain. |
| What does this quantity control? | Manipulate a parameter on the object or beside it. Keep other inputs constant. | The drawing and a labeled measurement update together. Show units and a baseline. |
| Which choice fits this constraint? | Place alternatives against the same brief, horizon and scale. Let the learner choose, then change one constraint. | Highlight the benefit and cost that actually change the decision. |
| How do I judge a crafted work? | Compare two versions of the same sentence, image, rhythm or layout. Isolate a feature. | Mark the phrase, visual region or beat that supports the interpretation. Allow reasoned alternatives when warranted. |
| How do the pieces work together? | Build an artifact from earlier lessons. Apply a new use case, input or fault and let the learner revise it. | Show which requirement passes, which breaks and what revision changes the outcome. |

## Two worked adaptations

**Git branching.** A collaborator adds a commit on a feature branch. Begin with two branch labels pointing at the same commit. Ask which label will move, then let the learner commit on the active branch. Animate the new commit and move only that label. Switching branches moves HEAD while preserving both histories. For transfer, place the learner on the other branch and ask them to predict the next graph before revealing it. Compute labels and the readout from the graph and current branch.

**Rhythm.** The learner needs to distinguish tempo from note density. Keep a four-beat grid and place one event per beat at 60 BPM. Let them subdivide each beat into two equal events. The new onsets are 0.5 seconds apart and the bar still lasts 4 seconds. Reset the pattern and change tempo to 120 BPM. The bar now lasts 2 seconds. For transfer, display a new timeline and ask which change preserved the bar duration. Use a visible playhead and optional user-started audio so the experiment also works silently.

## Useful implementation boundary

Separate authored lessons (stable IDs, stages, captions, concept anchors, prerequisites) from a small state model (lesson, step, learner input and playback). Derive all views of an experiment from the same model. Choose playback that matches the concept: a playhead for time, discrete snapshots for comparisons, direct manipulation for spatial judgment. A local, dependency-free page can be appropriate for a small lesson. Reuse the project's routing and components for a course.

An effective test names an input and an expected observation. For the rhythm lesson, changing the subdivision at fixed tempo must leave bar duration unchanged. Test the same invariant after Back, Replay and a direct jump. For an interpretive lesson, check that the highlighted evidence belongs to the selected version and the feedback permits the readings the evidence supports.
