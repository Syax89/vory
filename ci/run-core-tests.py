"""Execute real Swift tests; require behavioral failures on the pinned old sources."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess

revision = os.environ['REVISION']
assert revision in {'base', 'candidate'}
root = Path(__file__).resolve().parents[1]
command = ['swift', 'test', '--package-path', 'Packages/VoryCore', '--filter', 'ChatRegistryTests|AwayRefreshTests']
result = subprocess.run(command, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
log = result.stdout
(root / 'core-tests.log').write_text(log)
print(log)
assert 'Build complete!' in log, 'A build failure is not behavioral regression-red'
if revision == 'base':
    assert result.returncode != 0, 'Old production unexpectedly passed the regression tests'
    for test in ['anEmptyRuntimeIDMatchesNoChat', 'theReturnWithNothingArrivingStillReadsTheListsOnce']:
        assert re.search(r'✘ Test ' + test + r'\(\) failed', log), f'Missing intended failure: {test}'
else:
    assert result.returncode == 0, 'Candidate regression tests failed'
    assert re.search(r'Test run with \d+ tests in \d+ suites passed', log)
files = ['Packages/VoryCore/Sources/VoryCore/Runtime/ChatRegistry.swift', 'Packages/VoryCore/Sources/VoryCore/Runtime/GatewayRuntime.swift', 'VoryTests/AwayRefreshTests.swift', 'VoryTests/HermesRemoteTests.swift']
receipt = json.dumps({'revision': revision, 'test_exit': result.returncode, 'sha256': {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in files}}, indent=2)
(root / 'core-results.json').write_text(receipt)
print(receipt)
