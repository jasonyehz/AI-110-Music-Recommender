# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

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

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
