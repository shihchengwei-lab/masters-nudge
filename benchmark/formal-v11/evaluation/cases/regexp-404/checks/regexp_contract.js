const path = require('path');
const { Linter } = require('eslint');
const rule = require(path.join(process.argv[2], 'lib/rules/no-dupe-disjunctions.ts')).default;
const linter = new Linter();
linter.defineRule('probe', rule);
const codes = ['/a[ab]+|b+a|[ab]{2}/'];
const results = codes.map(code => {
  try {
    const messages = linter.verify(code, {parserOptions:{ecmaVersion:2020},rules:{probe:'error'}});
    let passed;
    if (code === codes[0]) {
      const column = code.indexOf('[ab]{2}') + 2;
      passed = messages.some(m => m.column === column && m.endColumn === column + 1 && m.message.startsWith('Unexpected useless element. All paths of'));
    }
    return {code,messages,passed};
  } catch (error) { return {code,error:String(error),passed:false}; }
});
console.log('PROBE_RESULT ' + JSON.stringify(results));
