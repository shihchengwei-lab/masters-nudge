const path = require('path');
const { Linter } = require('eslint');
const rule = require(path.join(process.argv[2], 'lib/rules/no-dupe-disjunctions.ts')).default;
const linter = new Linter();
linter.defineRule('probe', rule);
const code = '/(?<=a|a[ab])/';
const messages = linter.verify(code, {parserOptions: {ecmaVersion: 2020}, rules: {probe: 'error'}});
const column = code.indexOf('[ab]') + 2;
const passed = messages.some(m => m.column === column && m.endColumn === column + 1 &&
    m.message.startsWith('Unexpected useless element. All paths of')) &&
    !messages.some(m => m.column === code.indexOf('a[ab]') + 1 && m.endColumn > column + 1);
const exponentialCode = '/(?:a+|[ab])+$/';
const exponentialOptions = {report: 'all', reportExponentialBacktracking: 'certain'};
const exponentialMessages = linter.verify(exponentialCode, {
    parserOptions: {ecmaVersion: 2020}, rules: {probe: ['error', exponentialOptions]},
});
console.log('PROBE_RESULT ' + JSON.stringify({code, messages, passed,
    exponential: {code: exponentialCode, options: exponentialOptions, messages: exponentialMessages,
        warningPreserved: exponentialMessages.some(m => /exponential backtracking/i.test(m.message))}}));
