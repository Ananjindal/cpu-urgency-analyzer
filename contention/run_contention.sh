#!/bin/bash

CORES=${1:-4}
DURATION=${2:-30}

echo "======================================"
echo "       CPU CONTENTION TEST"
echo "======================================"
echo "CPU workers : $CORES"
echo "Duration    : $DURATION seconds"
echo

stress-ng \
    --cpu "$CORES" \
    --timeout "${DURATION}s" \
    --metrics-brief
