#!/bin/bash
# régression complète : chaque test a son journal ; résumé dans summary.log
cd /tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t
: > summary.log
for t in "$@"; do
  s=$(date +%s)
  timeout 420 python3 -I $t.py > log_$t.txt 2>&1
  rc=$?
  e=$(( $(date +%s) - s ))
  echo "$t rc=$rc ${e}s :: $(tail -n 2 log_$t.txt | tr '\n' ' ' | cut -c1-220)" >> summary.log
done
echo FINI >> summary.log
