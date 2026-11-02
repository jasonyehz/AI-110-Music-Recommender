# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  


**VibeMatch 1.0**

A small recommender that matches songs to your vibe.

---

## 2. Intended Use  


**Goal:** Suggest songs from a small catalog that fit a person's taste. It predicts which songs a user will like best.

**What it assumes about the user:** The user can say their favorite genre, their favorite mood, and how energetic they want the music to be.

**Intended use:** This is a classroom project. It helps me learn how recommenders turn data into rankings. It is meant for exploring and explaining, not for real listeners.

**Not intended for:**

- Real music apps or any product with real users.
- Making decisions about artists, such as who gets promoted.
- Judging anyone's taste. The system only knows 18 songs.
- Users who need fair results across all genres. The catalog is too small and uneven for that.

---

## 3. How the Model Works  

The recommender works like a judge giving every song in the catalog a score out of 4.5 points, then handing back the highest-scoring songs.

You tell it three things about your taste: your favorite genre, your favorite mood, and how energetic you want your music to be (a number from 0 for very calm to 1 for very intense). For each song, it awards points:

- **Genre:** 2 points if the song's genre is your favorite, otherwise nothing. This is the biggest prize because genre is the broadest sign of taste.
- **Mood:** 1 point if the song's mood is your favorite, otherwise nothing.
- **Energy:** up to 1.5 points for how close the song's energy is to what you asked for. A perfect match earns the full amount, and the points shrink the further away the song is. A song that is too mellow is penalized the same as one that is too intense, so "more energy" is not automatically better.

The songs are then lined up from highest score to lowest, and the top five are shown. Each one comes with its reasons, such as "genre match (+2.0)", so you can see why it was picked.

The starter code had no scoring logic, so all of this is new. The system only looks at genre, mood, and energy for now. It also learns nothing from other listeners, so it only reflects what you tell it.

---

## 4. Data  


- The catalog is `data/songs.csv`. It has **18 songs**.
- The starter file had 10 songs. I added 8 more to cover new genres and moods.
- Each song has a genre, a mood, and five numbers: energy, tempo, valence, danceability, and acousticness.
- There are **15 genres** and **14 moods**. Examples are pop, lofi, rock, jazz, edm, folk, happy, chill, angry, and romantic.
- The system only uses genre, mood, and energy. The other numbers are loaded but not scored.
- **Limits:** 13 of the 15 genres have only one song. Lofi has three songs and pop has two. I made up the songs and their numbers, so they are not real tracks. There are no lyrics, no language, and no listening history.

---

## 5. Strengths  


- It works well when a user's genre, mood, and energy agree with each other. The Chill Lofi and High-Energy Pop profiles both got results I would have picked myself.
- The top result is usually the song that matches all three things the user asked for.
- It separates very different tastes clearly. The pop list and the lofi list share no songs.
- It is easy to explain. Every recommendation comes with reasons, like "genre match (+2.0)".
- Energy is scored by closeness. A song that is too calm is penalized the same as one that is too intense.

---

## 6. Limitations and Bias 

The biggest weakness I found is that the system over-prioritizes genre, and the tiny catalog makes this worse. A genre match is worth 2.0 points, and the genre and mood matches together add up to 3.0, which is more than the largest possible energy penalty of 1.5. In my "pop fan wants calm" test, two high-energy pop songs (energy 0.82 and 0.93) outranked chill songs that matched the requested mood and energy almost perfectly, and in the "melancholy but high energy" test a folk song with energy 0.30 beat every song near the requested 0.90. The catalog also favors some users over others: 13 of its 15 genres have exactly one song, so a lofi fan gets three strong matches while a rock or jazz fan gets one and then a list of unrelated songs. A user whose genre is not in the catalog at all gets scores bunched within 0.12 of each other, so their ranking is nearly arbitrary. Genre matching is also all-or-nothing, so metal earns no credit for being close to rock.

---

## 7. Evaluation  

I checked the recommender by running seven user profiles through it and asking one question each time: does the top 5 look like what a person with that taste would actually want? The full terminal output for every profile is in the README.

**Profiles tested**

- Three typical listeners: **High-Energy Pop** (pop, happy, energy 0.9), **Chill Lofi** (lofi, chill, 0.4), and **Deep Intense Rock** (rock, intense, 0.95).
- Four edge cases built to trick the system: **melancholy but high energy** (folk, melancholy, 0.9), **a genre not in the catalog** (blues, sad, 0.3), **a pop fan who wants calm music** (pop, chill, 0.3), and **middle of the road** (no genre or mood match, energy 0.5).

I also ran one logic experiment: I doubled the weight on energy and halved the weight on genre, then compared the results.

**What surprised me**

- **Gym Hero kept showing up.** It appeared in 4 of the 7 top-5 lists. The reason is simple: Gym Hero is a pop song with very high energy. For someone who asks for "happy pop," it gets full credit for being pop and nearly full credit for energy, and it only misses on mood, because it is tagged "intense", not "happy". The system can't hear the song, so it can't tell that workout music feels different from sunny pop. It also has little else to choose from: the catalog has only two songs labeled "pop", and a third pop-sounding song is labeled "indie pop", which counts as a different genre.
- **A song that ignored the request still won.** For the "melancholy but high energy" profile, a calm folk song ranked first even though the user asked for very high energy, because matching on genre and mood outweighed the energy mismatch.
- **A pop fan who wanted calm music got loud pop songs first.** Genre points beat the mood and energy that the user also asked for.

**Comparing pairs of profiles**

- **High-Energy Pop vs. Chill Lofi:** The pop list is full of loud, upbeat songs, and the lofi list is full of quiet, slow, acoustic ones. This is correct: the energy target moves from 0.9 to 0.4, and genre and mood move with it. There is no overlap in the top 5, which tells me the profiles are testing real differences.
- **Chill Lofi vs. Deep Intense Rock:** Rock is the mirror image of lofi, with high energy, electric sounds, and an intense mood. Lofi gets three strong matches, but rock gets only one (Storm Runner), followed by high-energy songs from other genres. The difference makes sense, but it reveals that the catalog is lopsided: lofi has three songs and rock has one.
- **High-Energy Pop vs. Deep Intense Rock:** Both want very high energy (0.9 vs. 0.95), so the energy-based songs overlap: Storm Runner, Gym Hero, and Neon Overdrive appear in both lists. What differs is the top spot and the reasons: Sunrise City wins for pop because of genre and mood, and Storm Runner wins for rock for the same reasons. This shows that when energy is similar, genre and mood decide the winner.
- **High-Energy Pop vs. melancholy but high energy:** Both want energy around 0.9, but the melancholy profile puts a quiet folk song (energy 0.30) first and the loud songs second. The loud songs are the ones that fit the energy request, so this is the system putting a genre and mood match above what the user asked for. I consider this result wrong.
- **Chill Lofi vs. blues/sad (genre not in catalog):** The lofi profile has several strong matches and scores up to 4.47. The blues profile matches nothing on genre or mood, so its top scores are all about 1.4 to 1.5. The songs it recommends (Grey November, Spacewalk Thoughts, Library Rain) are calm and fairly sad-sounding, which is reasonable, but the scores are so close that the order is almost arbitrary.
- **High-Energy Pop vs. pop fan who wants calm:** Both profiles ask for pop, but the energy targets are 0.9 and 0.3. The top two songs for the calm profile are still the loud pop songs, so asking for a much calmer sound barely changed the top of the list. When I shifted the weights toward energy, the calm profile finally got calm songs first. This pair shows that the original weights let genre drown out energy.
- **Deep Intense Rock vs. middle of the road:** The rock profile has clear winners, while the middle-of-the-road profile has none, because no song matches its genre or mood. Its results are decided by energy alone, and two songs tie at 1.47. The ranking makes sense for the energy, but it shows that the system has little to say when a user's genre and mood don't exist in the catalog.

**What the experiment showed:** Shifting weight toward energy fixed the pop fan who wants calm music, because calm songs moved to the top. It did not fix the melancholy-but-high-energy profile or the rock-versus-metal problem. Those need a better way to compare genres, or more song features, not just different weights.

---

## 8. Future Work  


1. **Give partial credit for related genres.** Rock and metal should score close to each other. Pop and indie pop should too.
2. **Use more song features.** Valence, danceability, and acousticness would help tell angry metal from happy EDM, even when both have high energy.
3. **Add more songs.** Most genres have only one. A bigger catalog would give every user a real top 5.
4. **Lower the genre weight, or make it flexible.** Right now genre can beat a better match on energy and mood.
5. **Add variety to the top 5.** Right now the same song, like Gym Hero, can appear in many lists.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

I learned that a weight is a decision about whose taste counts. Genre was worth 2.0 points and the energy penalty tops out at 1.5, so a calm folk song beat every high-energy song for a user who preferred 0.9 energy. I used Claude extensively throughout the project. I ran every profile myself and compared the output to what I would expect. This is mainly due to Claude's inaccuracies that must be monitored at all times. 