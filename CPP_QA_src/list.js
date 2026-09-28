// Dev helper: node CPP_QA_src/list.js 3 4  -> question numbers and titles of those sections
const fs = require('fs');
const s = fs.readFileSync(__dirname + '/../500_CPP_Interview_Questions_Reference.html', 'utf8');
const Q = eval(s.match(/<script id="qdata">([\s\S]*?)<\/script>/)[1] + ';QUESTIONS');
for (const sec of process.argv.slice(2).map(Number)) {
  const qs = Q.filter(q => q.section === sec);
  console.log(`== ${sec}. ${qs[0].sectionTitle} (${qs.length})`);
  for (const q of qs) console.log(q.num + ' ' + q.question.slice(0, 100));
}
