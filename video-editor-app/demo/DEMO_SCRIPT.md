1. Start backend stack
   - `docker compose up --build`
2. Start frontend
   - `cd frontend && npm install && EXPO_PUBLIC_API_BASE_URL=http://localhost:8000 npm run start`
3. Open the Editor screen
4. Pick a sample video (use `base_video.mp4` from assets if needed)
5. Add overlays
   - Text overlay with content "Happy New Year!" at bottom center from 2.5s to 6s
   - Image overlay using `overlay_image.png` at top-left from 1s to 4s
   - Video clip overlay using `overlay_clip.mp4` at top-right from 3s to 8s
6. Preview timeline and playback; confirm overlays appear at times
7. Submit to backend; note the `job_id` response
8. Observe progress percent in the UI while polling status
9. When done, open the result URL and download the rendered mp4
10. Play the rendered video
11. Share the screen recording and rendered video via a public drive link and email to `arush@buttercut.ai`
