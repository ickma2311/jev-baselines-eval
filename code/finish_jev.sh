#!/bin/zsh
# Loop until all 300 Jev rows are valid: wait for any running run_b0.py, drop error rows, rerun.
cd "$(dirname "$0")/.."
while true; do
  while pgrep -f run_b0.py >/dev/null; do sleep 30; done
  n=$(python3 - <<'PY'
import json
rows=[json.loads(l) for l in open('pilot/results_b0.jsonl')]
keep=[r for r in rows if not (r['method']=='jev' and r.get('error'))]
open('pilot/results_b0.jsonl','w').write(''.join(json.dumps(r)+'\n' for r in keep))
print(sum(1 for r in keep if r['method']=='jev'))
PY
)
  echo "$(date) valid jev rows: $n"
  [ "$n" -ge 300 ] && { echo "$(date) ALL DONE"; break; }
  python3 pilot/run_b0.py >> pilot/run_b0.log 2>&1
done
