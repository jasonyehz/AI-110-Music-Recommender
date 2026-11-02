# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

All work below was done with Claude Code (Claude Sonnet 5.5) in one session. The prompts are the challenge instructions pasted into the chat. The verification notes list the checks that were run and what they showed. Add your own notes where you checked or changed something yourself.

---

## Agentic Workflow (SF8)

**What task did you give the agent?**

Challenge 1 (advanced song features), plus the related changes for Challenges 2, 3, and 4 in the same pass. The agent was to add 5 new song attributes to `data/songs.csv` and make `src/recommender.py` score them. The agent also had to keep the existing behavior working.

**Prompts used:**

> Introduce 5 or more complex attributes to your dataset that are not currently present in the baseline data, such as Song Popularity (0-100), Release Decade, or Detailed Mood Tags (e.g., "nostalgic," "aggressive," "euphoric"). Update both data/songs.csv and the scoring logic in src/recommender.py so scoring accounts for the new attributes.

> Build two or more different ranking strategies (e.g., "Genre-First," "Mood-First," or "Energy-Focused") so a user can switch between modes in main.py.

> Implement a "Diversity Penalty" that prevents the recommender from suggesting too many songs from the same artist or genre in the top results.

> Improve the readability of your terminal output by providing a formatted table or summary... the table must include the "reasons" for each score.

**What did the agent generate or change?**

- `data/songs.csv`: added 5 columns to all 18 songs.
  - `popularity` (0-100)
  - `release_decade` (1960 to 2020)
  - `mood_tags` (several tags per song, separated by `|`)
  - `instrumentalness` (0-1)
  - `language` (english, instrumental, spanish, korean)
- `src/recommender.py`:
  - `load_songs` parses the new columns (ints, floats, and a tag list).
  - `Song` and `UserProfile` gained the new fields with defaults, so the original tests still work.
  - `score_song` scores each new attribute only when the user gave a preference for it. Popularity, decade, and instrumentalness use the same closeness rule as energy. Mood tags score by the share of wanted tags the song has. Language is an exact match.
  - `ScoringMode`, `SCORING_MODES`, and the `mode` and `diversity` options (Challenges 2 and 3).
- `src/main.py`: new command line options, two new profiles that use the advanced attributes, and an ASCII table (Challenge 4).
- `tests/test_recommender.py`: 6 new tests.

**What did you verify or fix manually?**

- **Old results unchanged:** I reran the pop profile in the default mode with no advanced preferences. The scores still match the earlier README output (4.38, 3.46, 2.29, ...), so the new code did not change the original behavior.
- **Tests:** `pytest` passed (8 tests). One of my new tests failed on the first run, and the test was wrong, not the code. The diversity penalty (1.5 total) is not big enough to push a strong match (a song with a genre match and a close energy) below a weak one. I changed the test data so the penalty can matter, and it passed.
- **Advanced profiles:** the "Instrumental study music" profile puts the instrumental lofi songs on top, and the "Nostalgic 90s country fan" profile shows the decade and tag points in the reasons.
- **Things to review yourself:** the new attribute values are made up. The weights for the new attributes (0.5 to 1.0) are a first guess and have not been tuned.

---

## Design Pattern (SF10)

**Which design pattern did you use?**

A simple **Strategy pattern**. Each ranking style is a `ScoringMode` object that holds the point values for each feature. `score_song` takes a mode and reads the weights from it, so the scoring code is the same for every mode.

**How did AI help you brainstorm or implement it?**

I asked for a design that keeps the code modular. Claude suggested making each strategy a small frozen data object, not a separate class or function per mode. All the modes score features the same way and only the weights differ, so data is simpler than subclasses. A new mode is then one new dictionary entry. The three modes are:

- `genre-first` (the original weights: genre 2.0, mood 1.0, energy 1.5)
- `mood-first` (mood 2.0, genre 1.0, more weight on mood tags)
- `energy-focused` (energy 3.0, genre 1.0, mood 1.0)

I did not prototype the second mode on its own branch, as the challenge suggested. I worked on `main` and kept the original `genre-first` weights as the default, so the earlier results stayed the same.

**How does the pattern appear in your final code?**

- `ScoringMode` and `SCORING_MODES` in `src/recommender.py` define the strategies.
- `get_mode` looks one up by name (and raises a clear error for an unknown name).
- `score_song` and `recommend_songs` take a `mode` argument, and `main.py` exposes it as `--mode`.

Check on the "pop fan wants calm" profile: `genre-first` ranks the two pop songs first. `mood-first` and `energy-focused` put the calm, chill songs first. The mode changes the ranking as intended.

---

## Diversity Penalty (Challenge 3)

**Prompt used:** the Challenge 3 text above, with the rule: if a song's artist is already in the top results, subtract points from its score.

**What was built:** `recommend_songs(..., diversity=True)` picks songs one at a time. After each pick, every remaining song loses 1.0 point for each picked song by the same artist and 0.5 points for each picked song in the same genre. The penalty shows up in the reasons, for example `diversity penalty: artist LoRoom already picked (-1.0)`.

**Check:** for the Chill Lofi profile, Focus Flow (by LoRoom, the same artist as the #1 song) drops from #3 to #4 and Spacewalk Thoughts moves up. The penalty is a nudge. A very strong match can still stay in the list.

---

## Visual Summary Table (Challenge 4)

**Prompt used:** the Challenge 4 text above.

**What was built:** `format_table` in `src/main.py` prints a bordered ASCII table with the rank, title, artist, score, and reasons. Long reasons wrap onto extra lines inside the table. I used plain Python and not `tabulate`, so there is nothing new to install.
