const bi = (en, ar) => ({ en, ar });

export const course = {
  brand: bi("Python Mastery", "إتقان Python"),
  journey: bi("Spreadsheets → Python", "من الجداول إلى Python"),
  title: bi("Build a reading planner with Python", "ابنِ مخطط قراءة باستخدام Python"),
  intro: bi("Turn a reading log into a shortlist that fits your available time.", "حوّل سجلّ القراءة لقائمة تساعدك تختار قراءة تناسب وقتك."),
  study: bi("Think of sorting a spreadsheet column. Predict both outputs, run each file, then implement the same decision in your planner.", "افتكر لما بترتّب عمود في جدول. توقّع النتيجتين، شغّل كل ملف، وبعدها طبّق نفس القرار في مخطط القراءة."),
  bridgeLabel: bi("Spreadsheet → Python", "من الجداول إلى Python"),
  keywords: ["True", "False", "def"],
  project: {
    name: "reading-planner",
    title: bi("Your reading planner", "مشروع مخطط القراءة"),
    intro: bi("Create a local reading-planner folder. The first exercise adds the view that recommends the shortest reading session.", "أنشئ مجلد محلي باسم reading-planner. في أول تمرين هتبني العرض اللي بيرشّح أقصر جلسة قراءة."),
    setupTitle: bi("Run a planner exercise", "تشغيل تمرين المخطط"),
    setup: bi("Use a Python 3 interpreter. Save either case as planner.py in the project folder, then run these commands there.", "استخدم Python 3. احفظ كود أي حالة باسم planner.py في مجلد المشروع وشغّل الأوامر دي من جواه."),
    commands: "python3 --version\npython3 planner.py"
  }
};

const input = bi("Supply 25, 10 and 40 minutes.", "ابدأ بالمدد 25 و10 و40 دقيقة.");
const lesson = {
  id: "sort-duration",
  title: bi("Which reading session comes first?", "أي جلسة قراءة هتظهر الأول؟"),
  question: bi("How can the planner show the shortest session first and keep the original log?", "إزاي تعرض أقصر جلسة الأول وتحتفظ بترتيب السجل الأصلي؟"),
  bridge: bi("Sorting a spreadsheet view puts the smallest cell at the top. In Python, use the first element of the sorted result to make a recommendation.", "لما بترتّب عرض عمود تصاعديًا، أصغر قيمة بتظهر فوق. في Python تقدر تختار أول عنصر من النتيجة عشان ترشّح جلسة."),
  intro: bi("A list groups several values in one order. Here each number is the duration of a reading session in minutes. Sorting makes the shortest session easy to find.", "القائمة بتجمع قيم بترتيب معيّن. كل رقم عندنا مدة جلسة قراءة بالدقايق. ترتيب الأرقام بيسهّل اختيار أقصر جلسة."),
  mechanism: bi("Python’s `sorted()` returns a new list. Setting `reverse=True` places the largest number first. Save the code as `planner.py` and run `python3 planner.py`.", "الدالة `sorted()` بترجع قائمة جديدة. لو استخدمت `reverse=True` هيظهر أكبر رقم الأول. احفظ الكود في `planner.py` وشغّل `python3 planner.py`."),
  actors: [
    { name: "Log", kind: "input", description: "Session lengths" },
    { name: "Sorter", kind: "operation", description: "Order the values" },
    { name: "Planner", kind: "output", description: "Show first session" }
  ],
  cases: [
    {
      name: bi("Shortest first", "الأقصر الأول"), file: "planner.py",
      code: "minutes = [25, 10, 40]\nordered = sorted(minutes, reverse=False)\nprint(ordered[0], minutes)",
      observations: [input, bi("Arrange low to high.", "رتّب من الأصغر للأكبر."), bi("Recommend 10 minutes.", "رشّح جلسة 10 دقايق.")]
    },
    {
      name: bi("Longest first", "الأطول الأول"), file: "planner.py",
      code: "minutes = [25, 10, 40]\nordered = sorted(minutes, reverse=True)\nprint(ordered[0], minutes)",
      observations: [input, bi("Arrange high to low.", "رتّب من الأكبر للأصغر."), bi("Recommend 40 minutes.", "رشّح جلسة 40 دقيقة.")]
    }
  ],
  term: bi("Sort direction", "اتجاه الترتيب"),
  definition: bi("The direction determines which end of the range appears first in the result.", "الاتجاه بيحدّد أي طرف من القيم هيظهر الأول في النتيجة."),
  practical: {
    file: "planner.py",
    ...bi("Create this file. Print the shortest session and the original log. Try [15, 5, 20]. Check that the first value printed is 5 and that the log still starts with 15.", "أنشئ الملف واطبع أقصر جلسة والسجل الأصلي. جرّب [15, 5, 20]. اتأكد إن أول قيمة مطبوعة 5 وإن السجل لسه بيبدأ بـ15.")
  },
  milestone: bi("Demonstrate that the planner recommends the shortest session even when the input order changes.", "غيّر ترتيب الجلسات واعرض إن المخطط لسه بيرشّح أقصر واحدة."),
  quiz: {
    question: bi("For [8, 30, 12], which number does case 2 print first?", "مع [8, 30, 12]، أي رقم هتطبعه الحالة التانية الأول؟"),
    choices: [bi("8", "8"), bi("30", "30"), bi("12", "12")], answer: 1,
    reason: bi("Descending order puts 30 first. The original list still starts with 8.", "الترتيب التنازلي بيحط 30 الأول. القائمة الأصلية لسه بتبدأ بـ8.")
  },
  source: ["Python Sorting Techniques", "https://docs.python.org/3/howto/sorting.html#ascending-and-descending"]
};

export const sections = [{
  id: "reading-sessions", level: "junior",
  title: bi("Ordering a reading log", "ترتيب سجل القراءة"),
  summary: bi("Use session length to select the next reading.", "استخدم مدة الجلسة عشان تختار القراءة الجاية."),
  lessons: [lesson]
}];
