#!/bin/bash
cd /tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t
./run_srv.sh t4 t5 t6 t7 t8 t9 t10 t11 t12 t13 t14 t15 t16 t18 t19 t20 t22 t26 t27 t28 t29 t30 t31 t32 t33 t35 t36
cp summary.log summary_series.log
./final.sh
echo CHAINFINI > chain.done
