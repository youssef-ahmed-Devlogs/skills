# Finding the candidates

Run `scan.sh` of this skill's folder from the project root. `npx skills` puts the skill in `.agents/skills/laravel-refactor-issues`, and links it for Claude Code in `.claude/skills/laravel-refactor-issues`:

```bash
bash .agents/skills/laravel-refactor-issues/scan.sh > "$TMPDIR/refactor-scan.tsv"
```

Each line is one file and one check that hit it: `<path> <TAB> <check> <TAB> <convention file> <TAB> <hits>`. A file's number of breaks, for the order of step 5, is its number of lines in the output: the checks it hits, not the raw hits.

A hit is only a candidate. Step 6 reads the file and confirms it against the convention named on the line. A name that starts with `project/` is one of the project's own rules; the others are in `.claude/rules/laravel`.

## What no search can see

These conventions need reading, so step 6 checks them in every file of the batch:

- `controllers.md`: an action method without its `#[Authorize]` attribute; a controller with methods beyond the seven resource ones; logic, files or mail in a controller; a Service not taken in the constructor.
- `policies.md`: a model with no Policy; a Policy that names a role.
- `livewire.md`: a Livewire action that writes without `$this->authorize()`; an id the browser must not change, without `#[Locked]`; fields and rules outside a Form Object; a query the view reads outside a `#[Computed]` method.
- `services.md`: a CRUD Service whose method names are not `list`, `create`, `update`, `delete`; a write to several tables outside `DB::transaction()`; a refusal returned as `true` or `false` instead of thrown; a mail or notification sent by the Service instead of an event.
- `models.md`: missing `$fillable` fields; an Enum field not cast to its Enum.
- `enums.md`: a case compared with a string; the same condition on cases repeated outside the Enum.
- `jobs.md`: a job that holds logic instead of calling a Service, or that is not safe to run twice; a job dispatched inside a transaction without `afterCommit()`.
- `cache.md`: a key written as a string where it is read or cleared; a cache cleared from an observer; a cache with no lifetime.
- `form-requests.md`: a request not named `Store<Name>Request` or `Update<Name>Request`; a plain `exists` on a model that belongs to an owner, such as a team.
- `routes.md`: a CRUD controller registered with single routes; a nested route without `->scopeBindings()`.
- `excel.md`: an export whose query is not from a Service; a big export or import that is not queued.
- `errors.md`: an error page or an error JSON answer built outside `withExceptions` and the error classes.
- `folders.md`: a view or Livewire view outside its area folder; a big lang file that holds many features; a feature's setup in `AppServiceProvider`.
- `api-resources.md`, `naming.md`, `notifications.md`: the shapes and names they ask for.
- `naming.md`: a class, method, column, route or lang key named with a word its glossary says to avoid. The search sees file names only.
- `comments.md`: a comment that says what the code does instead of why.
- `logging.md`: a line at the wrong level; a secret or a whole request in a log line.
- A text a person sees, written in English in the code: the search sees only other scripts, such as Arabic.

## The project's own checks

A project adds its own checks in two files, so the skill stays the same in every project:

- `docs/agents/refactor-checks.sh`: searches that `scan.sh` runs after its own, with the same `check` function, such as `check role-written-outside project/roles.md '->(assignRole|syncRoles)\(' '*.php' 0 app`.
- `docs/agents/refactor-checks.md`: what only reading can see, one line per rule, in the shape of the list above.

## Keeping the search current

When a rule of `.claude/rules/laravel` that this scan covers is added or changed, add or change its check in `scan.sh`, in this skill's own repository, in the same pull request, with a line on the convention file it serves. When only reading can see it, add its line to the list above instead. A project's own rule gets its check in the project's two files above.
