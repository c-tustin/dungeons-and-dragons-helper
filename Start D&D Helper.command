#!/bin/bash
# Double-click to launch D&D Helper in your browser.
cd "$(dirname "$0")/app" || exit 1
PORT=8765
URL="http://localhost:$PORT"
if curl -s -o /dev/null "$URL"; then
  open "$URL"; exit 0
fi
( sleep 1; open "$URL" ) &
echo "D&D Helper is running at $URL"
echo "Keep this window open while you play. Close it (or press Ctrl+C) to stop."
python3 -m http.server "$PORT" --bind 127.0.0.1
