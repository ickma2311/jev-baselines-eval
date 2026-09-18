#!/bin/zsh
# Loop until all 300 Jev rows are valid: wait for any running run_b0.py, drop error rows, rerun.
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
RES="$(ls results_b0.jsonl ../results/results_b0.jsonl 2>/dev/null | head -1)"
while true; do
  while pgrep -f run_b0.py >/dev/null; do sleep 30; done
  n=$(RES="$RES" python3 - <<'PY'
import json
import os
RES=os.environ["RES"]
rows=[json.loads(l) for l in open(RES)]
keep=[r for r in rows if not (r['method']=='jev' and r.get('error'))]
open(RES,'w').write(''.join(json.dumps(r)+'\n' for r in keep))
print(sum(1 for r in keep if r['method']=='jev'))
PY
)
  echo "$(date) valid jev rows: $n"
  [ "$n" -ge 300 ] && { echo "$(date) ALL DONE"; break; }
  python3 "$HERE/run_b0.py" >> pilot/run_b0.log 2>&1
done
