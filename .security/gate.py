"""Fail closed: report integrity and severity gate; no exceptions configured."""
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])
problems = []
def read(name):
    try:
        return json.loads((p / name).read_text())
    except Exception as e:
        problems.append(f'{name}: {e}')
        return {}
coverage = read('sca-coverage.json')
if not coverage.get('passed'):
    problems.append('SCA coverage incomplete: ' + str(coverage.get('issues', [])))
s = read('semgrep.json')
if not s.get('paths', {}).get('scanned') or s.get('errors'):
    problems.append('SAST missing scanned files or has errors')
for r in s.get('results', []):
    if r['extra']['severity'].upper() in ('ERROR', 'HIGH', 'CRITICAL'):
        problems.append('SAST: ' + r['check_id'] + ':' + r['path'])
b = read('sbom.cyclonedx.json')
if b.get('bomFormat') != 'CycloneDX' or not b.get('components'):
    problems.append('SBOM invalid or empty')
d = read('dependency-check-report.json')
if not d.get('dependencies') or d.get('scanInfo', {}).get('analysisExceptions'):
    problems.append('SCA missing dependencies or analysis exceptions')
if not d.get('scanInfo', {}).get('dataSource'):
    problems.append('SCA data sources unavailable')
for dep in d.get('dependencies', []):
    for v in dep.get('vulnerabilities', []):
        scores = [float(x[k]) for x in (v.get('cvssv2', {}), v.get('cvssv3', {}), v.get('cvssv4', {})) for k in ('score','baseScore') if k in x]
        if not scores:
            problems.append('SCA unscored vulnerability: ' + v['name'])
        elif max(scores) >= 7:
            problems.append('SCA: ' + dep['fileName'] + ' ' + v['name'] + ' ' + str(max(scores)))
print(json.dumps({'passed': not problems, 'problems': problems}, indent=2))
sys.exit(bool(problems))
