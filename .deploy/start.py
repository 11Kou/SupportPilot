import os
from pathlib import Path
import subprocess
import time
import urllib.request

root = Path(__file__).resolve().parent.parent
os.chdir(root)
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
try:
    with opener.open('http://127.0.0.1:8000/openapi.json', timeout=3) as response:
        if b'SupportPilot' in response.read():
            print('SupportPilot is already running.')
            raise SystemExit(0)
except OSError:
    pass

(root / 'log').mkdir(exist_ok=True)
(root / 'data').mkdir(exist_ok=True)
env = os.environ.copy()
env['PATH'] = str(Path.home() / '.local/bin') + os.pathsep + env.get('PATH', '')
for name in ('NO_PROXY', 'no_proxy'):
    existing = env.get(name, '')
    env[name] = ','.join(filter(None, [existing, 'localhost,127.0.0.1,::1']))
with (root / 'log/dev.log').open('a') as log:
    process = subprocess.Popen(
        ['bash', './scripts/dev.sh'], cwd=root, env=env,
        stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
        start_new_session=True,
    )
(root / 'data/local-dev.pid').write_text(str(process.pid) + '\n')
print(f'SupportPilot startup launched (PID {process.pid}).')
deadline = time.monotonic() + 90
while time.monotonic() < deadline:
    if process.poll() is not None:
        raise SystemExit(f'Startup failed; see {root / "log/dev.log"}')
    try:
        with opener.open('http://127.0.0.1:8000/openapi.json', timeout=1) as response:
            if b'SupportPilot' in response.read():
                print('SupportPilot is ready: http://127.0.0.1:8000')
                break
    except OSError:
        pass
    time.sleep(1)
else:
    raise SystemExit(f'Startup timed out; see {root / "log/dev.log"}')
