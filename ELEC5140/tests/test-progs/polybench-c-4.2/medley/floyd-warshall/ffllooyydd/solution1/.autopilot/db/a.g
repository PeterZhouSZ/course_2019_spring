#!/bin/sh
lli=${LLVMINTERP-lli}
exec $lli \
    /media/lty/SSD/Experiment-tmp/final1027/tests/test-progs/polybench-c-4.2/medley/floyd-warshall/ffllooyydd/solution1/.autopilot/db/a.g.bc ${1+"$@"}
