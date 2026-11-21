#!/bin/bash
# lance un serveur local le temps des tests (il s'arrête avec le script), puis la série demandée
cd /tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t
python3 -I serve.py 8765 > /dev/null 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null' EXIT
for i in $(seq 1 60); do curl -s -o /dev/null http://127.0.0.1:8765/carnet-thailande-/ && break; sleep 0.2; done
./run_all.sh "$@"
