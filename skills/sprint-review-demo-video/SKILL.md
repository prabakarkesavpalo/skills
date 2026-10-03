---
name: sprint-review-demo-video
description: Record a small, downloadable narrated sprint-review demo video with Playwright, macOS say and ffmpeg. Use when asked for a demo video of finished work, a sprint review recording, or a showcase artifact that is not high resolution.
---

# Sprint-review demo video

Target: 854x480, 15 fps, crf 28, mp4. A 5 minute video is about 3 to 4 MB.

1. Slides: simple HTML title and summary slides rendered to images, plus live app steps.
2. Drive the app with Playwright (`channel: 'chrome'`, `recordVideo: { dir, size: { width: 854, height: 480 } }`). Harden each step: click first, verify the value, set 8 s timeouts.
3. Narration: macOS `say -o file.aiff` per scene. Get durations with `ffprobe`, not by parsing headers (WAV parsing gave NaN).
4. Mux with ffmpeg. Use `-filter_complex "$(cat filter.txt)"`; `-filter_complex_script` was not supported by the installed build.
5. Keep the script in the repo (`docs/demo/demo.mjs`, `mux.sh`) so the video can be regenerated.
6. Check the output: duration, size, a few frames.

Delivery: a file sender may not work from every session. Put the mp4 in the repo or a shared doc, and say where.
