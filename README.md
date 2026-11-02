# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world recommenders like Spotify combine multiple signals in order to determine what is best for a user. Collaborative filtering learns from what millions of listeners play, skip, save. Content-based filtering matches the audio traits of songs, such as energy and mood. They rank songs based on that data and match it with a user's listening history to determine what is the best song to recommend. My version is very simple content-based recommender. It scores each song by how closely each attribute match a user's stated taste. Genre will have the most weight (2pts), then energy (1.5pts), then mood (1 points). It cannot discover patterns across users, but it will determine what is best for each user based on their inputted data.

### Song features

Each song in `data/songs.csv` (18 songs across 15 genres) has `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, and `acousticness`. The scoring rule currently uses `genre`, `mood`, and `energy`. The other numeric features are loaded but not scored yet.

### User profile

A taste profile is a dictionary of target values:

```python
user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
```

Two contrasting profiles are used for testing: `{"genre": "rock", "mood": "intense", "energy": 0.9}` and `{"genre": "lofi", "mood": "chill", "energy": 0.4}`.

### Algorithm recipe

Every song is scored against the profile, the scores are sorted from highest to lowest, and the top `k` songs are returned along with the reasons for each score.

```
score = 2.0 × [genre matches]
      + 1.0 × [mood matches]
      + 1.5 × (1 − |song energy − target energy|)
```

- **Genre match (+2.0):** the song's genre equals the user's favorite genre, otherwise 0. Genre is the broadest statement of taste, so it carries the most weight.
- **Mood match (+1.0):** the song's mood equals the user's favorite mood, otherwise 0. It is a useful tiebreaker, but it overlaps with genre and energy.
- **Energy closeness (0 to +1.5):** a song exactly on target gets the full 1.5, and the score falls off linearly with distance. Being above or below the target is penalized equally, so higher energy is not automatically better.
- **Maximum score:** 4.5.

### Expected biases and limitations

- **Genre may be over-prioritized.** A genre match is worth more than the whole energy range's spread between a perfect and a poor fit, so a pop song with a mediocre energy can outrank a better-fitting song from another genre. Great songs that match the user's mood and energy but not the genre can be buried.
- **Genre matching is all-or-nothing.** Related genres get no credit: metal gets none against rock, and indie pop gets none against pop.
- **Unfamiliar genres degrade the ranking.** If the user's favorite genre isn't in the catalog, scores bunch together and energy alone decides the order.
- **The catalog is tiny and uneven.** Most genres have one song, and lofi (3) and pop (2) are the only repeats, so those users get far better recommendations than everyone else.
- **Ignored features.** `valence`, `danceability`, `acousticness`, and `tempo_bpm` are not used, so songs with similar energy but very different feel (angry metal vs. euphoric EDM) can look alike.
- **No learning.** Without listening history, the system cannot discover patterns across users, so it only reflects what the user states.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output of `python -m src.main` for the default pop/happy profile:

```
Loaded songs: 18

User profile: genre=pop, mood=happy, energy=0.8

Top recommendations:

1. Sunrise City by Neon Echo - Score: 4.47
     - genre match: pop (+2.0)
     - mood match: happy (+1.0)
     - energy 0.82 vs target 0.80 (+1.47)

2. Gym Hero by Max Pulse - Score: 3.30
     - genre match: pop (+2.0)
     - energy 0.93 vs target 0.80 (+1.30)

3. Rooftop Lights by Indigo Parade - Score: 2.44
     - mood match: happy (+1.0)
     - energy 0.76 vs target 0.80 (+1.44)

4. Concrete Crown by Kid Meridian - Score: 1.47
     - energy 0.78 vs target 0.80 (+1.47)

5. Night Drive Loop by Neon Echo - Score: 1.42
     - energy 0.75 vs target 0.80 (+1.42)
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

I ran seven profiles through `python -m src.main`: three typical listeners and four adversarial edge cases meant to trick the scoring rule. The profiles are defined in `src/main.py`. Each block below is the terminal output, followed by what I observed.

### Standard profiles

#### High-Energy Pop

```
User profile: genre=pop, mood=happy, energy=0.9

1. Sunrise City by Neon Echo - Score: 4.38
     - genre match: pop (+2.0)
     - mood match: happy (+1.0)
     - energy 0.82 vs target 0.90 (+1.38)
2. Gym Hero by Max Pulse - Score: 3.46
     - genre match: pop (+2.0)
     - energy 0.93 vs target 0.90 (+1.46)
3. Rooftop Lights by Indigo Parade - Score: 2.29
     - mood match: happy (+1.0)
     - energy 0.76 vs target 0.90 (+1.29)
4. Storm Runner by Voltline - Score: 1.48
     - energy 0.91 vs target 0.90 (+1.48)
5. Neon Overdrive by Pulse Cartel - Score: 1.41
     - energy 0.96 vs target 0.90 (+1.41)
```

**Observation:** Matches intuition. Sunrise City matches all three features; Gym Hero follows on genre and a closer energy.

#### Chill Lofi

```
User profile: genre=lofi, mood=chill, energy=0.4

1. Midnight Coding by LoRoom - Score: 4.47
     - genre match: lofi (+2.0)
     - mood match: chill (+1.0)
     - energy 0.42 vs target 0.40 (+1.47)
2. Library Rain by Paper Lanterns - Score: 4.42
     - genre match: lofi (+2.0)
     - mood match: chill (+1.0)
     - energy 0.35 vs target 0.40 (+1.42)
3. Focus Flow by LoRoom - Score: 3.50
     - genre match: lofi (+2.0)
     - energy 0.40 vs target 0.40 (+1.50)
4. Spacewalk Thoughts by Orbit Bloom - Score: 2.32
     - mood match: chill (+1.0)
     - energy 0.28 vs target 0.40 (+1.32)
5. Coffee Shop Stories by Slow Stereo - Score: 1.46
     - energy 0.37 vs target 0.40 (+1.46)
```

**Observation:** Matches intuition. All three lofi songs lead, and the ambient and jazz songs that follow share the calm feel.

#### Deep Intense Rock

```
User profile: genre=rock, mood=intense, energy=0.95

1. Storm Runner by Voltline - Score: 4.44
     - genre match: rock (+2.0)
     - mood match: intense (+1.0)
     - energy 0.91 vs target 0.95 (+1.44)
2. Gym Hero by Max Pulse - Score: 2.47
     - mood match: intense (+1.0)
     - energy 0.93 vs target 0.95 (+1.47)
3. Neon Overdrive by Pulse Cartel - Score: 1.48
     - energy 0.96 vs target 0.95 (+1.48)
4. Iron Requiem by Black Cathedral - Score: 1.47
     - energy 0.97 vs target 0.95 (+1.47)
5. Sunrise City by Neon Echo - Score: 1.30
     - energy 0.82 vs target 0.95 (+1.30)
```

**Observation:** There is only one rock song, so after Storm Runner the list fills with high-energy songs. Gym Hero (pop) beats Iron Requiem (metal) because its mood is "intense", and metal gets no credit for being close to rock.

### Adversarial profiles

#### Conflicting: melancholy but high energy

```
User profile: genre=folk, mood=melancholy, energy=0.9

1. Grey November by Wren Hollow - Score: 3.60
     - genre match: folk (+2.0)
     - mood match: melancholy (+1.0)
     - energy 0.30 vs target 0.90 (+0.60)
2. Storm Runner by Voltline - Score: 1.48
     - energy 0.91 vs target 0.90 (+1.48)
3. Gym Hero by Max Pulse - Score: 1.46
     - energy 0.93 vs target 0.90 (+1.46)
4. Neon Overdrive by Pulse Cartel - Score: 1.41
     - energy 0.96 vs target 0.90 (+1.41)
5. Iron Requiem by Black Cathedral - Score: 1.40
     - energy 0.97 vs target 0.90 (+1.40)
```

**Observation:** The folk song has energy 0.30 against a target of 0.90, yet it wins by more than double (3.60 vs 1.48). Genre and mood points (3.0) outweigh the largest possible energy penalty, so the top result ignores the energy request entirely.

#### Genre not in catalog (blues/sad)

```
User profile: genre=blues, mood=sad, energy=0.3

1. Grey November by Wren Hollow - Score: 1.50
     - energy 0.30 vs target 0.30 (+1.50)
2. Spacewalk Thoughts by Orbit Bloom - Score: 1.47
     - energy 0.28 vs target 0.30 (+1.47)
3. Library Rain by Paper Lanterns - Score: 1.42
     - energy 0.35 vs target 0.30 (+1.42)
4. Coffee Shop Stories by Slow Stereo - Score: 1.40
     - energy 0.37 vs target 0.30 (+1.40)
5. Moonlit Sonata Remix by Elise Varo - Score: 1.38
     - energy 0.22 vs target 0.30 (+1.38)
```

**Observation:** Nothing matches genre or mood, so energy alone decides. The top 5 scores span only 0.12 (1.38-1.50), which makes the ranking close to arbitrary.

#### Genre vs. vibe: pop fan wants calm

```
User profile: genre=pop, mood=chill, energy=0.3

1. Sunrise City by Neon Echo - Score: 2.72
     - genre match: pop (+2.0)
     - energy 0.82 vs target 0.30 (+0.72)
2. Gym Hero by Max Pulse - Score: 2.55
     - genre match: pop (+2.0)
     - energy 0.93 vs target 0.30 (+0.55)
3. Spacewalk Thoughts by Orbit Bloom - Score: 2.47
     - mood match: chill (+1.0)
     - energy 0.28 vs target 0.30 (+1.47)
4. Library Rain by Paper Lanterns - Score: 2.42
     - mood match: chill (+1.0)
     - energy 0.35 vs target 0.30 (+1.42)
5. Midnight Coding by LoRoom - Score: 2.32
     - mood match: chill (+1.0)
     - energy 0.42 vs target 0.30 (+1.32)
```

**Observation:** The two pop songs (energy 0.82 and 0.93) outrank songs that fit the requested mood and energy almost perfectly. This is the clearest case of genre over-prioritization.

#### Middle of the road: energy 0.5, no matches

```
User profile: genre=k-pop, mood=party, energy=0.5

1. Dusty Porch Light by Hollow Creek - Score: 1.47
     - energy 0.48 vs target 0.50 (+1.47)
2. Island Drift by Salt & Sun - Score: 1.47
     - energy 0.52 vs target 0.50 (+1.47)
3. Velvet Hours by Amara Skye - Score: 1.42
     - energy 0.45 vs target 0.50 (+1.42)
4. Midnight Coding by LoRoom - Score: 1.38
     - energy 0.42 vs target 0.50 (+1.38)
5. Focus Flow by LoRoom - Score: 1.35
     - energy 0.40 vs target 0.50 (+1.35)
```

**Observation:** Scores are nearly identical (1.47, 1.47, 1.42, ...). Dusty Porch Light and Island Drift tie to two decimals, and the order is broken by their position in the CSV.

### Accuracy and surprises

**Does it feel right?** For coherent profiles, yes. For the Chill Lofi profile, the three lofi songs lead and the ambient and jazz songs that follow share the same calm, acoustic feel. The weakest case is Deep Intense Rock: a rock fan would expect Iron Requiem (metal) at #2, but Gym Hero (pop) ranks above it because the system matches the word "intense" and has no sense that metal is close to rock.

**Why does Sunrise City rank first for pop/happy/0.8?** It is the only song that earns all three awards: genre match (+2.0), mood match (+1.0), and energy 0.82 against a target of 0.80 (+1.47). That totals 4.47 out of 4.5. The runner-up, Gym Hero, earns the genre points and a good energy score but misses the mood match, so it scores 3.30.

**Does one song dominate every list?** No. The #1 song changes for most profiles (Sunrise City, Midnight Coding, Storm Runner, Grey November, Dusty Porch Light). Two surprises, though:

- **Gym Hero shows up in 4 of the 7 top-5 lists** (as pop's #2, rock's #2, the conflicting profile's #3, and the pop-wants-calm profile's #2). Its very high energy (0.93) and "intense" mood overlap with many profiles, and it is one of only two pop songs.
- **Grey November is #1 for two different profiles.** For the conflicting profile it wins on genre and mood alone. For the blues/sad profile it wins by chance, because its energy is exactly 0.30.

The genre weight is the main driver of surprising results. A genre match is worth more than the full range of energy fit, so a genre-matching song can beat a much better overall fit.

### Weight-shift experiment

I doubled the energy weight (1.5 to 3.0) and halved the genre weight (2.0 to 1.0), then reran all seven profiles. The maximum score becomes 1.0 + 1.0 + 3.0 = 5.0, and a perfect match still hits it exactly (Sunrise City scores 5.00). The experiment was run without changing the committed weights, which are still 2.0 / 1.0 / 1.5.

| Profile | Result |
|---|---|
| Pop fan wants calm | **Changed, and more accurate.** The top 3 became Spacewalk Thoughts, Library Rain, and Midnight Coding (all calm and chill). The two high-energy pop songs dropped out of the top 5. |
| Conflicting (folk, 0.9) | **Still wrong.** Grey November (energy 0.30) stays #1, 3.20 vs 2.97, because genre plus mood still beats the energy mismatch. |
| Deep Intense Rock | **Unchanged.** Gym Hero still outranks Iron Requiem. |
| The other four profiles | **Same order**, with higher scores. |

The change was more accurate in one case and just different in the rest. It fixed the case where genre was overriding a clear energy preference. It did not fix the rock/metal problem or the conflicting profile, which need related-genre credit or additional features like `valence`, not a different weighting.

---

## Limitations and Risks

- **Tiny, uneven catalog.** There are only 18 songs, and 13 of the 15 genres have exactly one. Lofi fans get three strong matches. Rock and jazz fans get one, then unrelated songs.
- **Genre is over-weighted.** A genre match (2.0) plus a mood match (1.0) beats the largest possible energy penalty (1.5). A calm folk song won for a user who asked for very high energy, and loud pop songs won for a pop fan who asked for calm music.
- **Exact matching only.** Metal gets no credit for being close to rock, and indie pop gets none for being close to pop.
- **Unknown tastes get arbitrary results.** If the user's genre is not in the catalog, the top 5 scores fall within 0.12 of each other.
- **Most features are ignored.** Valence, danceability, acousticness, and tempo are loaded but not scored, so angry metal and euphoric EDM can look alike.
- **No lyrics, language, or listening history.** The system only knows what the user types in, and it cannot learn from other listeners.
- **Repeat winners.** Gym Hero appeared in 4 of the 7 top-5 lists I tested.

See [model_card.md](model_card.md) for more detail.

---

## Reflection

Full details are in the [**Model Card**](model_card.md).

**How recommenders turn data into predictions.** A recommender can be very simple and still feel real. Three inputs and a few points for each match were enough to give sensible lists for the Chill Lofi and High-Energy Pop profiles. The prediction is just a ranking, and every number in it comes from a choice about what to count. Scoring energy by closeness, not "higher is better", was one of those choices, and it made the results fairer to users at both ends of the scale. My tests also showed the limits of such a rule. The same song (Gym Hero) appeared in four of seven lists, because the system matches labels and numbers and cannot hear that workout music feels different from happy pop.

**Where bias or unfairness could show up.** Bias showed up in the weights and in the data. Genre was worth more than energy, so a user's genre label could override what they actually asked for. The catalog had three lofi songs and one of most other genres, so lofi fans got better recommendations than rock or jazz fans through no fault of their own. A real system at scale would have the same problems in a quieter form: whichever tastes have the most data, or the heaviest weight, get served best, and everyone else gets worse results without any obvious error to point at.



