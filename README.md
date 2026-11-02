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

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



