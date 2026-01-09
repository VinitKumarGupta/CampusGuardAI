#!/bin/bash

FRAMES_FOLDER="cv_engine/media/output/frames"
VIOLATIONS_FOLDER="cv_engine/media/output/violations"
VEHICLE_LOGS="cv_engine/media/output/vehicle_log.json"

echo "Clearing output folders..."

rm -rf "$FRAMES_FOLDER" "$VIOLATIONS_FOLDER"
rm -f "$VEHICLE_LOGS"

mkdir -p "$FRAMES_FOLDER" "$VIOLATIONS_FOLDER"

echo "Done."
