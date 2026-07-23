#!/usr/bin/env python3
"""Send daily digest to WeChat via openclaw message broadcast (no model)."""
import subprocess, sys

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from config.project_paths import LATEST_DIGEST

msg_file = sys.argv[1] if len(sys.argv) > 1 else LATEST_DIGEST

with open(msg_file, encoding='utf-8') as f:
    msg = f.read()

result = subprocess.run(
    ['openclaw', 'message', 'broadcast',
     '--channel', 'openclaw-weixin',
     '--account', 'd5d64a9561df-im-bot',
     '--targets', 'o9cq80wUsai7ARs168BuArTu0CF4@im.wechat',
     '--message', msg,
     '--json'],
    capture_output=True, text=True, timeout=30,
    env={'PATH': '/home/user994/local/nodejs/bin:/home/user994/.local/bin:/usr/local/bin:/usr/bin:/bin',
         'HOME': '/home/user994'}
)

if result.returncode == 0:
    import json
    data = json.loads(result.stdout)
    r = data['payload']['results'][0]
    print(f"OK: {r['ok']} | msgId={r['result']['result']['messageId']} | via={r['result']['via']}")
else:
    print('FAILED:', result.stderr[:300])
    sys.exit(1)
