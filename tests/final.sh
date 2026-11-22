#!/bin/bash
cd /tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t
: > final.log
for t in t40 t41 t42 t43 t37 t38 t39 real_check prod_smoke; do
  echo "== $t" >> final.log
  curl -s 127.0.0.1:8780/__ctl/reset >/dev/null
  timeout 300 python3 -I $t.py 2>&1 | tail -3 | cut -c1-200 >> final.log
done
echo FINI >> final.log
