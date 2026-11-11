"""Check installed lockfile packages against the completed SCA inventory."""
import json
import pathlib
import sys
import urllib.parse

out = pathlib.Path(sys.argv[1])
issues = []
lock = json.loads(pathlib.Path('package-lock.json').read_text())
expected = set()
optional_absent = []
for path, entry in lock['packages'].items():
    if not path:
        continue
    manifest = pathlib.Path(path) / 'package.json'
    if not manifest.is_file():
        if entry.get('optional'):
            optional_absent.append(path)
        else:
            issues.append('Required locked package not installed: ' + path)
        continue
    package = json.loads(manifest.read_text())
    expected.add((package['name'], package['version']))
observed = set()
try:
    report = json.loads((out / 'dependency-check-report.json').read_text())
    def inventory(dependencies):
        for dependency in dependencies:
            yield dependency
            yield from inventory(dependency.get('relatedDependencies', []))
    for dep in inventory(report.get('dependencies', [])):
        if dep.get('name') and dep.get('version'):
            observed.add((dep['name'], dep['version']))
        for package in dep.get('packages', []) + dep.get('packageIds', []):
            identifier = package.get('id', '')
            if identifier.startswith('pkg:npm/'):
                value = urllib.parse.unquote(identifier[8:].split('?')[0])
                name, _, version = value.rpartition('@')
                observed.add((name, version))
    missing = sorted(expected - observed)
    if missing:
        issues.append('Installed name/version pairs missing from SCA: ' + str(len(missing)))
    log = (out / 'dc-console.log').read_text()
    for analyzer in ('Node Package Analyzer', 'Node Audit Analyzer'):
        if 'Finished ' + analyzer not in log:
            issues.append('Analyzer completion missing: ' + analyzer)
    if (out / 'dc-exit-code.txt').read_text().strip() not in ('0', '15'):
        issues.append('Dependency-Check infrastructure/analysis failure')
except (OSError, ValueError, KeyError) as exc:
    missing = sorted(expected)
    issues.append(str(exc))
if not expected:
    issues.append('No installed locked dependencies')
result = dict(passed=not issues, issues=issues, lockfile_entries=len(lock['packages'])-1,
              installed_unique_name_versions=len(expected), observed_unique_name_versions=len(observed),
              missing_name_versions=missing, optional_not_installed=optional_absent)
(out / 'sca-coverage.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
sys.exit(bool(issues))
