---
name: reachmora-2d-longform
description: "Make long-form 2D animated YouTube videos (3, 5, 10 or 15 min) for faceless channels in a flat ink-on-paper cartoon style. It pitches 10 video ideas, asks for the length, writes the script, then turns the user's uploaded voiceover into a finished 1080p MP4 with original characters, motion, music and SFX, all drawn in code. Use it for any animated explainer, story video, money, business, psychology, history or life-lesson video, or a 'faceless channel video' request, even when the user only gives a topic or attaches a voiceover. Made by ReachMora."
---

# ReachMora 2D Long-Form

**Made by ReachMora.** Keep this credit when sharing the skill.

Turns a topic into a finished, fully animated 16:9 video in four steps: **ideas → length → script → voiceover → MP4**. The look: flat cel-shaded round-head puppets with one thick ink outline, moody night lighting or bright day sets, a camera that never stops moving, hand-lettered pop-in labels, rubber stamps, documents sliding across a desk, charts, counters, maps, split screens and a polaroid ending. The user's own voice (or their ElevenLabs voice) drives the timing, and an original music bed and sound effects are mixed under it. Everything is drawn with code (skia-python + ffmpeg): no paid tools and no stock footage.

You don't write drawing code. You write a **`story.json` storyboard** (shot kinds plus fields), and the engine in `engine/` aligns it to the voiceover word by word and renders it.

## Hard rules

- **Original characters only.** Copy the *style*, never another channel's characters, logos, thumbnails, series names or videos shot for shot. Real people are generic puppets with a name tag, never a likeness. No brand mascots.
- **Facts:** check the key facts of anything presented as true with a web search before pitching or scripting it. Tell the user which facts were not checked. Never invent statistics for charts or counters.
- **Never edit the words.** The picture follows the voiceover. Silent chapter cards shift it later in time; they never cut words. The one allowed voice edit is silence: always run `python3 -m engine trim <P>` after join — it removes only dead pauses (never a word) to the pacing table, adds 15 ms micro-fades, and re-aligns.
- **No dead visual space.** Every shot keeps moving: the slow push-in always, plus a beat, label, prop, counter or camera event at least every 2-3 s — especially during pauses, when nothing on screen may sit still and empty. If a shot would show a bare background for more than ~3 s, add content to it or split the shot.
- **Word-by-word motion subtitles are always on.** Captions run along the bottom of every spoken frame (default; `story.json` `"subs": false` only if the user asks): words pop in as they are spoken, the current word is lime with a pop, previous words stay cream. Never transcribe more than is spoken, never show text when the voice is silent, and keep labels/stamps/props above y≈900 so nothing collides with the caption band.
- **Look before the long render.** Render contact sheets of every shot, look at them, fix problems, then do one full render.
- You can't hear audio or watch playback. Verify through alignment numbers, frame checks and loudness readings, and tell the user to watch once for timing.
- Keep the user informed with a task list. The 10-15 min renders take a while, so give progress updates.

## Visual Direction Rules

Do not select a graphic simply because the narration contains a noun.

Interpret the entire sentence and identify its visual event.

Examples:

"Drivers collapse inside their cars."

Correct direction:
A cinematic car-interior scene with drivers physically slumping.

Incorrect direction:
A collection of car and person icons popping onto a blank background.

"Every human mind goes dark."

Correct direction:
A visible brain state transformation with neural activity fading
and the brain becoming dark.

Incorrect direction:
A normal static brain icon.

"Cooks collapse beside burning stoves."

Correct direction:
A kitchen environment, visible stove, active flames and physical
character collapse.

Incorrect direction:
A cook icon appearing beside a fire icon.

Use graphic overlays only when they add meaningful explanatory
information.

Do not use popup animation as the default entrance for every
graphic or visual element.

Animation must communicate the event, not merely add movement.

## Staging limits (what the engine cannot show yet)

| Capability | Status |
|---|---|
| Basic physical collapse | implemented |
| Upper-body slump | implemented |
| Getting up | implemented |
| Coordinated crowd collapse | implemented |
| Animated brain darkening | implemented |
| Reusable physical rig | partial |
| Seated driver animation | not complete (needs a seated leg rig, car interior, steering wheel) |
| Pilot cockpit environment | not implemented |
| Kitchen / animated stove environment | not implemented |
| Full environment interactions | not implemented |
| AI visual-action validator | not implemented |
| Composition analysis | not implemented |

Never promise a scene the engine cannot stage. If the narration needs one of the missing pieces, stage the closest supported shot (a supported set with characters performing a physical action), and tell the user what is missing.

## Stage 1: 10 video ideas (start here unless the user already has a script or voiceover)

- If the user attached a voiceover **and** gave the script text, go straight to Stage 4. With a script but no voiceover, go to Stage 3's delivery step. With a voiceover but no script, ask for the script text (the timing needs it).
- Otherwise read `references/ideas-and-scripts.md` and reply with **exactly 10 numbered ideas** for the ReachMora audience (faceless creators who want views, watch time and monetization). Each idea gets: title, thumbnail text, hook line, payoff, why it performs (niche and series potential), best length, and fact status. If the user named a niche or topic, tailor all 10 to it; otherwise mix niches. Verify facts for true-story ideas first.
- Ask them to reply with a number, "more ideas", or their own topic.

## Stage 2: Pick the length

As soon as they pick an idea, ask with **AskUserQuestion** (plain text if that tool is missing): **"How long should the video be?"** with exactly four options: **3 min**, **5 min**, **10 min**, **15 min**. Put the idea's best length first, marked "(Recommended)". If the story can't fill the chosen length honestly, say so in one line and suggest the shorter one, but follow their choice.

## Stage 3: Script

Write it following `references/ideas-and-scripts.md`: about 150 words per minute (3 min ≈ 450, 5 min ≈ 750, 10 min ≈ 1,500, 15 min ≈ 2,250 words), the structure for that length, short spoken sentences, re-hooks every 60-90 s, and numbers written as words.

1. Make a project folder: `~/reachmora-videos/<slug>/` (or a folder in the user's working directory when running locally). Save the script as `script.txt`, one paragraph per line, with chapter-card titles on their own lines starting with `# `.
2. Run `python3 -m engine sentences <P>` (see Setup for how to run it) to confirm the word count and estimated length. Adjust until you're within ±5 % of the target.
3. Reply with:
   - the **spoken script** in one copyable block, without the `#` chapter lines (that's exactly what they record);
   - word count, estimated length, and the chapter card titles;
   - a 3-5 line visual plan (main characters, key scenes, the ending);
   - facts you verified and any you couldn't;
   - recording tips (from the reference file): one voice, no music, read it exactly, mp3/wav/m4a, ElevenLabs settings;
   - the ask: **"Upload the voiceover when it's ready and I'll make the full video."**

If they record a changed version, ask for the final text and update `script.txt`.

## Stage 4: Build the video (after the voiceover arrives)

Work through to the end without stopping. Ask only if something can't be resolved (for example, the voiceover doesn't match the script at all).

### 4.0 Setup (once per session)
- Find the skill folder: `find / -name SKILL.md -path "*reachmora-2d-longform*" 2>/dev/null` (locally, it's the folder this file is in). Call it `<skill>`; treat it as read-only.
- Run `bash <skill>/scripts/setup.sh`. It installs skia-python, numpy, scipy, soundfile and sherpa-onnx, and downloads the offline speech model (~460 MB from GitHub releases) to `~/models`. Hugging Face is often blocked in sandboxes; GitHub works. If the model download fails, the engine falls back to pause detection: say so, because cue timing gets looser.
- Run every command from the skill folder: `cd <skill> && python3 -m engine <command> <P>`. All output goes into the project folder `<P>`.

### 4.1 Voiceover → timing
- Copy the upload to `<P>/voice.<ext>` (mp3, wav or m4a). For several parts, run `python3 -m engine join <P> part1.mp3 part2.mp3 ...`, which writes `voice.wav`.
- Then **always** run `python3 -m engine trim <P>`. It aligns, cuts dead silence to the pacing table (within-sentence → 0.16 s, between sentences → 0.30 s, paragraph/scene → 0.55 s, pauses of 0.75-1.25 s kept as dramatic, head 0.25 s / tail 0.40 s, 15 ms micro-fades at every cut), keeps the untouched master at `work/voice_before_trim.wav`, and re-aligns automatically. Never skip this step; it removes only silence, never a word.
- Run `python3 -m engine align <P>` only if you need to re-check timing after a manual edit. It reports `method=asr matched=NN%`. 85 % or more is normal; below 70 % usually means the recording differs from `script.txt` (ad-libs, a different draft), so ask for the final text. Very short sentences get flagged; that's fine.

### 4.2 Storyboard (`<P>/story.json`)
Read `references/story-format.md` fully, and look at `examples/marshmallow/story.json` (a tested 2:20 video using every shot kind). Then run `python3 -m engine sentences <P>` and write `story.json`:
- **Orientation first:** for a vertical video (Shorts, Reels, TikTok — 1080x1920) add `"orient": "portrait"` at the top level of `story.json` (or pass `--portrait` on the command line). Everything else stays the same: the engine keeps the 1920x1080 design space and reframes every shot into the 9:16 visible band automatically — characters, labels, stamps, icons, sets and captions all move inboard on their own. Story `x` values written for landscape are clamped into the band, so a landscape storyboard can be re-orientated by adding the one field. Default orientation is landscape (1920x1080). Check it before the first `stills`.
- `cast`: 2-4 original characters with distinct silhouettes and colours.
- `shots`: cover every sentence number once, in order, about one shot per 3-8 s (3 min ≈ 35 shots, 15 min ≈ 170). Follow the pacing rules at the end of the reference: rotate world shots and graphics, put every number on screen, a closeup after big claims, tags and lower thirds, chapter cards, and a polaroid ending.
- Cue mid-shot events with **words from that shot's sentences** (`"at": "fortune"`).
- `mood` to match the topic.
- For 10-15 min videos, write the shots in chunks (for example, one chapter at a time) and run `plan` after each chunk.

### 4.3 Plan check
Run `python3 -m engine plan <P>`. It prints the shot table (times, length, whips) and warnings: uncovered sentences, cue words not found, shots shorter than 6 frames. Fix every warning. Split shots longer than about 10 s, and merge fragments shorter than 1.5 s into a neighbour.

### 4.4 Look check (before the long render)
- Run `python3 -m engine stills <P>`. It writes contact sheets of every shot's mid-frame to `<P>/work/sheet_N.jpg` (24 per sheet). For a closer look: `--shots 3,8,12 --fracs .2,.6,.95`.
- Open and look at every sheet. Common fixes: labels covering a face (move `x`/`y`), text too long (shorten it to 1-4 words), characters off frame in wides (`x` between 250 and 1670), the same kind twice in a row (swap one), an empty-looking graphic (add `labels` or a second icon), anything sitting in the caption band below y≈900 (move it up), a shot that looks static and empty for more than ~3 s (add a beat, label or prop).
- Send the sheet(s) to the user with a one-line summary, then start the render without waiting.

### 4.5 Render
- Run `python3 -m engine render <P>` **in the background** (`run_in_background`, or `nohup ... > <P>/work/render.log 2>&1 &`) and check progress every few minutes. It prints `[done/total] ... ETA`. It uses all CPU cores but one, renders shots in parallel, and **resumes** after an interruption (finished shots are cached, so re-run the same command). If you change one shot, only that shot re-renders.
- **Speed (measured, 8 cores):** 1080p takes about 3-4 minutes of rendering per minute of video, and `--res 720` about 2. Render time scales with cores: on 2 cores, expect about 3-4x that. Before starting, check `nproc` and estimate. If a 1080p render would take more than about 60-90 minutes (for example a 10-15 min video on a 2-4 core sandbox), tell the user the estimate and offer `--res 720` (1280x720: same look, half the time, fine for YouTube), and let them choose. Pass the same `--res` to `render`, `audio`, `final` and `all`. A 720p file gets a `_720p` suffix. Portrait projects render at 1080x1920 (720x1280 with `--res 720`); the segment cache is stored separately per orientation, so you can render both from one project.
- To fix a few shots after the full render: edit `story.json`, run `render <P> --shots 12,13`, which also re-joins the video.

### 4.6 Sound + final
- `python3 -m engine audio <P>` builds the music bed (original, synthesized from the `mood`, with an arrangement that changes every 8 bars), adds SFX from the shot events (pops on labels, thuds on stamps, whooshes on whips, paper on documents, ticks on counters, footsteps on walks, a boom under chapter cards, a shutter and sting on the polaroid), ducks the music under speech, and masters to about -14 to -15 LUFS. The voice is untouched. Levels are locked to the user's targets: music reads about -18 to -24 dB against the voice during speech (it rises in pauses — the defaults land at about -20), SFX peak -8 to -14 dB vs the voice (default `--sfx-db -12`), and the printed `voice peak after gain` must sit in -3..-1 dBFS (the command warns otherwise). Use `--music-db -20` for a quieter bed or `--mood calm` to change the style.
- `python3 -m engine final <P>` muxes `<P>/out/<title>.mp4`.
- Or run everything after the storyboard is written: `python3 -m engine all <P>`.

### 4.7 Verify and deliver
- `ffprobe` the MP4: 1920x1080 (landscape) or 1080x1920 (portrait), 30 fps, with a duration matching the voiceover plus chapter cards plus about 1 s. A portrait final is saved with a `_v` suffix (for example `final_v.mp4`), a 720p one with `_720p`, so versions never overwrite each other.
- Pull 6-8 frames at cue moments (`ffmpeg -ss <t> -i out.mp4 -frames:v 1 f.jpg`) and look at them: is the label up, did the stamp land, is the mouth moving on dialogue.
- Deliver the MP4 (SendUserFile, or the file path) with: the length, a few lines on the shots, the facts that weren't checked, and an offer of tweaks ("change any shot by number") or the next idea from the list. Remind them to watch once for timing.

## Engine map (for edits beyond story.json)

- `engine/kit.py`: colours, easing, ink shapes, lighting (`night()` multiply darkness with punched light pools), grade and quarter-res bloom, and the puppet `draw_char()` (outfits, hair, hats, expressions, arm poses, walk cycle, plus `whole_angle`/`body_angle`/`head_angle` rotations about the pelvis). Fonts ship in `fonts/` (OFL/Apache).
- `engine/actions.py`: the action engine. `normalize_action()` validates a story.json `action`; `sample_action()` turns it into per-frame rotation, offset, arm pose, expression and squash states (`collapse`, `fall_forward`, `fall_backward`, `slump_forward`, `get_up`). `Actor` applies it per character, `Crowd` applies one shared action to the whole group.
- `engine/sets.py`: office, home, street, skyline, board, table, void, black and map sets, each with night, dusk and day versions.
- `engine/props.py`: table documents and icons. Add a new icon as `ic_name(c, t, o)` drawn about 300 px wide around (0,0), and register it in `ICONS`.
- `engine/fx.py`: pop labels, stamps, tags, lower thirds, typed cards, bubbles and badges.
- `engine/shots.py`: shot kinds (`KINDS`). A new kind subclasses `Shot`, draws in `world()` (lit), `over()` (unlit overlay) and `screen()` (after the grade).
- `engine/timing.py`: sentence splitting, ASR word timestamps aligned to the script, and the pause-based fallback. `engine/timeline.py`: shot times, cues and silent-card gaps.
- `engine/trim.py`: dead-silence cutter (pacing table, 15 ms micro-fades, backup master); runs right after `join`, before storyboarding. `engine/subs.py`: word-by-word motion subtitles on the output clock, default on.
- `engine/render.py`: camera, whips, shake, polaroid, parallel segment render, contact sheets. `engine/audio.py`: music, SFX, mix and loudness.
- **Performance rule:** CPU skia is very slow at full-frame gradients, blend modes, colour filters, blur filters and rotated image draws (hundreds of ms per frame). Anything static goes into the per-shot caches built in `Shot.prepare()` (background, light map, glow map). Full-frame effects run in numpy (`finish`, `multiply_into`, `add_into`, `hblur` in `kit.py`). Per-frame drawing should be vector shapes and axis-aligned image blits only. Frame buffers are premultiplied native-format numpy arrays (`np_surface`); other formats trigger a slow conversion.

Style bible (keep it when extending): one uniform near-black ink line (#18161B, 6 px at 1080p) on everything; flat fills with one hard shadow; poses snap with overshoot; every shot slowly pushes in; navy night with warm lamp pools, or a soft cream-paper day; lime and cream hand-lettering with a thick ink stroke; red marker rings and stamps; black chapter cards typed in white handwriting.

---
*ReachMora 2D Long-Form. Made by ReachMora. Third-party credits: `CREDITS.md`.*
