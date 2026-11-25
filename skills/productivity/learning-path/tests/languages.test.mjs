import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { cpSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { course, sections } from "../assets/site/course.mjs";
import { validateCourse } from "../assets/site/scripts/validate.mjs";

const template = new URL("../assets/site/", import.meta.url);

function courseData(language) {
  const data = { course: { ...course, language }, sections };
  return JSON.parse(JSON.stringify(data, (key, value) => {
    if (language === "en" && key === "ar") return undefined;
    if (language === "ar" && key === "en") return undefined;
    return value;
  }));
}

for (const mode of ["en", "ar", "both"]) {
  test(`build a course with only the fields needed for ${mode}`, t => {
    const dir = mkdtempSync(join(tmpdir(), "learning-path-"));
    t.after(() => rmSync(dir, { recursive: true, force: true }));
    cpSync(template, dir, { recursive: true });
    const data = courseData(mode);
    writeFileSync(join(dir, "course.mjs"),
      `export const course = ${JSON.stringify(data.course)};\nexport const sections = ${JSON.stringify(data.sections)};\n`);
    execFileSync(process.execPath, ["scripts/build.mjs"], { cwd: dir });
    const app = readFileSync(join(dir, "assets/app.js"), "utf8");
    execFileSync(process.execPath, ["--check", "assets/app.js"], { cwd: dir });
    assert.equal(app.includes('id="lang-menu-wrap"'), mode === "both");
    const lesson = sections[0].lessons[0];
    const first = mode === "ar" ? "ar" : "en";
    for (const page of ["index", lesson.id]) {
      const html = readFileSync(join(dir, page + ".html"), "utf8");
      assert.ok(html.includes(`<html lang="${first}" dir="${first === "ar" ? "rtl" : "ltr"}"`));
      for (const lang of ["en", "ar"]) {
        const selected = mode === "both" || lang === mode;
        assert.equal(html.includes(`data-lang="${lang}"`), selected);
        assert.equal(app.includes(lesson.title[lang]), selected);
        if (page === lesson.id) {
          assert.equal(html.includes(lesson.cases[0].observations[1][lang]), selected);
          assert.equal(html.includes(`arr-${lesson.id}-0-${lang}`), selected);
        }
      }
    }
  });
}

test("require each selected language and accept older bilingual data", () => {
  const legacy = courseData("both");
  delete legacy.course.language;
  legacy.sections[0].lessons[0].actors[0].name = "Log";
  validateCourse(legacy.course, legacy.sections);
  for (const lang of ["en", "ar"]) {
    const data = courseData(lang);
    delete data.sections[0].lessons[0].quiz.reason[lang];
    assert.throws(() => validateCourse(data.course, data.sections), /quiz.reason/);
  }
  assert.throws(() => validateCourse({ ...course, language: "other" }, sections), /course.language/);
});
