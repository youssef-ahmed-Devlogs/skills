function check(condition, field, expected) {
  if (!condition) throw new Error(`${field} requires ${expected}`);
}

function text(value, field) {
  check(typeof value === "string" && value.trim(), field, "non-empty text");
}

function pair(value, field) {
  for (const lang of ["en", "ar"]) text(value?.[lang], `${field}.${lang}`);
}

function slug(value, field, seen) {
  check(typeof value === "string" && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value), field, "a lowercase URL slug");
  check(!seen.has(value), field, `a unique ID (${value} is already used)`);
  seen.add(value);
}

export function validateCourse(course, sections) {
  for (const key of ["brand", "journey", "title", "intro", "study", "bridgeLabel"]) pair(course[key], key);
  for (const key of ["title", "intro", "setupTitle", "setup"]) pair(course.project?.[key], "project." + key);
  for (const key of ["name", "commands"]) text(course.project[key], "project." + key);

  check(Array.isArray(sections) && sections.length, "sections", "at least one section");
  const levels = ["junior", "mid", "senior"];
  const sectionIds = new Set();
  const lessonIds = new Set(["index"]);
  let lastLevel = 0;
  for (const section of sections) {
    slug(section.id, "section.id", sectionIds);
    check(levels.includes(section.level), section.id, "a valid section level");
    for (const key of ["title", "summary"]) pair(section[key], section.id + "." + key);
    check(Array.isArray(section.lessons) && section.lessons.length, section.id, "lessons");
    for (const lesson of section.lessons) {
      const id = lesson.id;
      slug(id, "lesson.id", lessonIds);
      const rank = levels.indexOf(lesson.level ?? section.level);
      check(rank >= lastLevel, id, "Junior → Mid-Level → Senior order");
      lastLevel = rank;
      for (const key of ["title", "question", "intro", "mechanism", "term", "definition", "bridge", "practical"]) {
        pair(lesson[key], id + "." + key);
      }
      if (lessonIds.size > 2) pair(lesson.previous, id + ".previous");
      if (lesson.milestone) pair(lesson.milestone, id + ".milestone");
      text(lesson.practical.file, id + ".practical.file");
      check(Array.isArray(lesson.actors) && lesson.actors.length === 3, id, "three actors");
      for (const actor of lesson.actors) {
        text(actor.name, id + ".actor.name");
        text(actor.kind, id + ".actor.kind");
        if (Array.isArray(actor.description)) {
          check(actor.description.length === 2, id, "one actor description per case");
          actor.description.forEach(item => text(item, id + ".actor.description"));
        } else text(actor.description, id + ".actor.description");
      }
      check(Array.isArray(lesson.cases) && lesson.cases.length === 2, id, "two cases");
      for (const item of lesson.cases) {
        pair(item.name, id + ".case.name");
        text(item.file, id + ".case.file");
        text(item.code, id + ".case.code");
        check(Array.isArray(item.observations) && item.observations.length === 3, id, "one observation per actor");
        item.observations.forEach(observation => pair(observation, id + ".observation"));
      }
      const quiz = lesson.quiz;
      pair(quiz?.question, id + ".quiz.question");
      pair(quiz.reason, id + ".quiz.reason");
      check(Array.isArray(quiz.choices) && quiz.choices.length >= 2, id, "at least two quiz choices");
      quiz.choices.forEach(choice => pair(choice, id + ".quiz.choice"));
      check(Number.isInteger(quiz.answer) && quiz.answer >= 0 && quiz.answer < quiz.choices.length, id, "a zero-based answer index");
      text(lesson.source?.[0], id + ".source label");
      check(/^https?:\/\//.test(lesson.source?.[1]), id, "an official source URL");
    }
  }
}
