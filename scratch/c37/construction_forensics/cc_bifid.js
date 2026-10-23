// Executes the VERBATIM CyberChef run() bodies of BifidCipherEncode/Decode + genPolybiusSquare + Array.prototype.unique
// (extracted from gchq/CyberChef master, src dir passed as argv[2]). Reads JSON jobs from argv[3]; writes JSON results.
const fs = require('fs');
const src = process.argv[2];
function extract(text, sig) {
  const i = text.indexOf(sig); if (i < 0) throw new Error('sig ' + sig);
  let j = text.indexOf('{', i), depth = 0, k = j;
  for (; k < text.length; k++) { if (text[k] === '{') depth++; else if (text[k] === '}') { depth--; if (depth === 0) break; } }
  return text.slice(j + 1, k);
}
const utils = fs.readFileSync(src + '/Utils.mjs', 'utf8');
eval('Array.prototype.unique = function() {' + extract(utils, 'Array.prototype.unique = function()') + '}');
class OperationError extends Error {}
const ciphers = fs.readFileSync(src + '/Ciphers.mjs', 'utf8');
const genPolybiusSquare = new Function('keyword', extract(ciphers, 'export function genPolybiusSquare'));
const mk = (f) => new Function('genPolybiusSquare', 'OperationError', 'return function(input, args){' + extract(fs.readFileSync(src + '/' + f, 'utf8'), 'run(input, args)') + '}')(genPolybiusSquare, OperationError);
const dec = mk('BifidCipherDecode.mjs'), enc = mk('BifidCipherEncode.mjs');
const jobs = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const out = jobs.map(j => {
  try {
    const sq = genPolybiusSquare(j.key.toUpperCase().replace('J', 'I')).map(r => r.join('')).join('');
    return { ...j, square: sq, out: (j.op === 'dec' ? dec : enc)(j.input, [j.key]) };
  } catch (e) { return { ...j, error: String(e.message) }; }
});
process.stdout.write(JSON.stringify(out));
