import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file into dicts, converting numeric columns to int/float."""
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["id"] = int(row["id"])
            for field in ("energy", "tempo_bpm", "valence", "danceability", "acousticness"):
                row[field] = float(row[field])
            songs.append(row)
    return songs

# Points available for each feature. Genre outweighs mood on purpose.
GENRE_POINTS = 2.0
MOOD_POINTS = 1.0
ENERGY_POINTS = 1.5


def numeric_similarity(song_value: float, target_value: float, value_range: float = 1.0) -> float:
    """Return a 0.0-1.0 closeness score that falls linearly with distance from the target, above or below."""
    distance = abs(song_value - target_value)
    return max(0.0, 1.0 - distance / value_range)


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song (max 4.5) from genre match, mood match, and energy closeness, and return the reasons."""
    score = 0.0
    reasons: List[str] = []

    if song["genre"] == user_prefs.get("genre"):
        score += GENRE_POINTS
        reasons.append(f"genre match: {song['genre']} (+{GENRE_POINTS:.1f})")

    if song["mood"] == user_prefs.get("mood"):
        score += MOOD_POINTS
        reasons.append(f"mood match: {song['mood']} (+{MOOD_POINTS:.1f})")

    if "energy" in user_prefs:
        similarity = numeric_similarity(float(song["energy"]), user_prefs["energy"])
        points = ENERGY_POINTS * similarity
        score += points
        reasons.append(
            f"energy {float(song['energy']):.2f} vs target {user_prefs['energy']:.2f} (+{points:.2f})"
        )

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song and return the top k as (song, score, explanation), highest score first."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, "; ".join(reasons)))

    return sorted(scored, key=lambda item: item[1], reverse=True)[:k]
