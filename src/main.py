"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


# Typical listeners: each has preferences that agree with each other.
STANDARD_PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.9},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.4},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.95},
}

# Edge cases designed to trick the scoring logic or expose its blind spots.
ADVERSARIAL_PROFILES = {
    "Conflicting: melancholy but high energy": {"genre": "folk", "mood": "melancholy", "energy": 0.9},
    "Genre not in catalog (blues/sad)": {"genre": "blues", "mood": "sad", "energy": 0.3},
    "Genre vs. vibe: pop fan wants calm": {"genre": "pop", "mood": "chill", "energy": 0.3},
    "Middle of the road: energy 0.5, no matches": {"genre": "k-pop", "mood": "party", "energy": 0.5},
}


def print_recommendations(name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Print the top k recommendations for one profile with their scoring reasons."""
    print("=" * 60)
    print(f"{name}")
    print(
        f"User profile: genre={user_prefs['genre']}, "
        f"mood={user_prefs['mood']}, energy={user_prefs['energy']}"
    )
    print("=" * 60)
    for rank, (song, score, explanation) in enumerate(recommend_songs(user_prefs, songs, k=k), start=1):
        print(f"{rank}. {song['title']} by {song['artist']} - Score: {score:.2f}")
        for reason in explanation.split("; "):
            print(f"     - {reason}")
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    for name, prefs in {**STANDARD_PROFILES, **ADVERSARIAL_PROFILES}.items():
        print_recommendations(name, prefs, songs)


if __name__ == "__main__":
    main()
