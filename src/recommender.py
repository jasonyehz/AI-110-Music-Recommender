import csv
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Tuple, Optional, Union

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
    # Advanced attributes. Defaults keep older code that builds a Song without them working.
    popularity: int = 50
    release_decade: int = 2020
    mood_tags: List[str] = field(default_factory=list)
    instrumentalness: float = 0.0
    language: str = "english"

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
    # Optional advanced preferences. None or empty means "no preference", so they are not scored.
    target_popularity: Optional[int] = None
    preferred_decade: Optional[int] = None
    favorite_tags: List[str] = field(default_factory=list)
    target_instrumentalness: Optional[float] = None
    preferred_language: Optional[str] = None

@dataclass(frozen=True)
class ScoringMode:
    """A scoring strategy: how many points each feature can earn."""
    genre: float
    mood: float
    energy: float
    tags: float = 1.0
    popularity: float = 0.5
    decade: float = 0.5
    instrumentalness: float = 0.5
    language: float = 0.5


# Each mode is a swappable strategy. score_song looks up the weights, so adding a
# new ranking style means adding one entry here and no new scoring code.
SCORING_MODES: Dict[str, ScoringMode] = {
    "genre-first": ScoringMode(genre=2.0, mood=1.0, energy=1.5),
    "mood-first": ScoringMode(genre=1.0, mood=2.0, energy=1.5, tags=1.5),
    "energy-focused": ScoringMode(genre=1.0, mood=1.0, energy=3.0),
}
DEFAULT_MODE = "genre-first"

# Diversity re-ranking: points taken off a song for each already-picked song that shares a trait.
ARTIST_PENALTY = 1.0
GENRE_PENALTY = 0.5


def get_mode(mode: Union[str, ScoringMode]) -> ScoringMode:
    """Return the ScoringMode for a mode name, or pass a ScoringMode straight through."""
    if isinstance(mode, ScoringMode):
        return mode
    if mode not in SCORING_MODES:
        raise ValueError(f"Unknown mode '{mode}'. Choose from: {', '.join(SCORING_MODES)}")
    return SCORING_MODES[mode]


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(
        self,
        user: UserProfile,
        k: int = 5,
        mode: Union[str, ScoringMode] = DEFAULT_MODE,
        diversity: bool = False,
    ) -> List[Song]:
        """Return the top k songs for the user, ranked by score_song, highest first."""
        song_dicts = [asdict(song) for song in self.songs]
        by_dict = {id(song_dict): song for song_dict, song in zip(song_dicts, self.songs)}
        ranked = recommend_songs(_profile_to_prefs(user), song_dicts, k, mode, diversity)
        return [by_dict[id(song_dict)] for song_dict, _, _ in ranked]

    def explain_recommendation(
        self, user: UserProfile, song: Song, mode: Union[str, ScoringMode] = DEFAULT_MODE
    ) -> str:
        """Return the scoring reasons for one song as a single readable string."""
        _, reasons = score_song(_profile_to_prefs(user), asdict(song), mode)
        return "; ".join(reasons) if reasons else "No matching preferences"


def _profile_to_prefs(user: UserProfile) -> Dict:
    """Convert a UserProfile into the prefs dict that score_song expects."""
    prefs: Dict = {
        "genre": user.favorite_genre,
        "mood": user.favorite_mood,
        "energy": user.target_energy,
    }
    if user.target_popularity is not None:
        prefs["popularity"] = user.target_popularity
    if user.preferred_decade is not None:
        prefs["decade"] = user.preferred_decade
    if user.favorite_tags:
        prefs["tags"] = user.favorite_tags
    if user.target_instrumentalness is not None:
        prefs["instrumentalness"] = user.target_instrumentalness
    if user.preferred_language is not None:
        prefs["language"] = user.preferred_language
    return prefs

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file into dicts, converting numeric columns and splitting mood tags."""
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for line_number, row in enumerate(csv.DictReader(f), start=2):
            try:
                for field_name in ("id", "popularity", "release_decade"):
                    row[field_name] = int(row[field_name])
                for field_name in ("energy", "tempo_bpm", "valence", "danceability", "acousticness", "instrumentalness"):
                    row[field_name] = float(row[field_name])
                row["mood_tags"] = [tag.strip() for tag in row["mood_tags"].split("|") if tag.strip()]
            except (KeyError, ValueError, AttributeError) as error:
                raise ValueError(f"{csv_path} line {line_number}: bad or missing value ({error})") from error
            songs.append(row)
    return songs

def _same_text(song_value: Optional[str], wanted: Optional[str]) -> bool:
    """Compare two labels ignoring case and surrounding spaces; no preference never matches."""
    if wanted is None or song_value is None:
        return False
    wanted = str(wanted).strip().lower()
    return wanted != "" and str(song_value).strip().lower() == wanted


def _clean_tags(tags) -> List[str]:
    """Return tags as a lowercase list without duplicates. A single string counts as one tag."""
    if isinstance(tags, str):
        tags = [tags]
    return list(dict.fromkeys(str(tag).strip().lower() for tag in tags if str(tag).strip()))


def numeric_similarity(song_value: float, target_value: float, value_range: float = 1.0) -> float:
    """Return a 0.0-1.0 closeness score that falls linearly with distance from the target, above or below."""
    distance = abs(song_value - target_value)
    return max(0.0, 1.0 - distance / value_range)


def score_song(
    user_prefs: Dict, song: Dict, mode: Union[str, ScoringMode] = DEFAULT_MODE
) -> Tuple[float, List[str]]:
    """Score one song from the features the user gave preferences for, and return the score and reasons."""
    weights = get_mode(mode)
    score = 0.0
    reasons: List[str] = []

    if _same_text(song["genre"], user_prefs.get("genre")):
        score += weights.genre
        reasons.append(f"genre match: {song['genre']} (+{weights.genre:.1f})")

    if _same_text(song["mood"], user_prefs.get("mood")):
        score += weights.mood
        reasons.append(f"mood match: {song['mood']} (+{weights.mood:.1f})")

    if "energy" in user_prefs:
        target_energy = float(user_prefs["energy"])
        similarity = numeric_similarity(float(song["energy"]), target_energy)
        points = weights.energy * similarity
        score += points
        reasons.append(f"energy {float(song['energy']):.2f} vs target {target_energy:.2f} (+{points:.2f})")

    # Advanced attributes: each is scored only when the user gave a preference for it.
    wanted_tags = _clean_tags(user_prefs.get("tags") or [])
    if wanted_tags:
        song_tags = _clean_tags(song.get("mood_tags", []))
        shared = [tag for tag in wanted_tags if tag in song_tags]
        points = weights.tags * len(shared) / len(wanted_tags)
        if shared:
            score += points
            reasons.append(f"mood tags {'/'.join(shared)} (+{points:.2f})")

    if "popularity" in user_prefs and "popularity" in song:
        target = float(user_prefs["popularity"])
        points = weights.popularity * numeric_similarity(song["popularity"], target, 100.0)
        score += points
        reasons.append(f"popularity {song['popularity']} vs target {target:.0f} (+{points:.2f})")

    if "decade" in user_prefs and "release_decade" in song:
        # 60 years (1960s to 2020s) is the widest gap in the catalog.
        target = float(user_prefs["decade"])
        points = weights.decade * numeric_similarity(song["release_decade"], target, 60.0)
        score += points
        reasons.append(f"{song['release_decade']}s vs preferred {target:.0f}s (+{points:.2f})")

    if "instrumentalness" in user_prefs and "instrumentalness" in song:
        target = float(user_prefs["instrumentalness"])
        points = weights.instrumentalness * numeric_similarity(float(song["instrumentalness"]), target)
        score += points
        reasons.append(
            f"instrumentalness {float(song['instrumentalness']):.2f} vs target {target:.2f} (+{points:.2f})"
        )

    if _same_text(song.get("language"), user_prefs.get("language")):
        score += weights.language
        reasons.append(f"language match: {song['language']} (+{weights.language:.1f})")

    return score, reasons

def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: Union[str, ScoringMode] = DEFAULT_MODE,
    diversity: bool = False,
) -> List[Tuple[Dict, float, str]]:
    """Score every song and return the top k as (song, score, explanation), highest score first."""
    if k < 0:
        raise ValueError("k must be 0 or greater")
    scored = [(song, *score_song(user_prefs, song, mode)) for song in songs]

    if not diversity:
        ranked = sorted(scored, key=lambda item: item[1], reverse=True)[:k]
        return [(song, score, "; ".join(reasons)) for song, score, reasons in ranked]

    # Greedy re-ranking: each pick is the best remaining song after penalizing repeats
    # of an artist or genre that is already in the list.
    picked: List[Tuple[Dict, float, str]] = []
    remaining = list(scored)
    while remaining and len(picked) < k:
        best = None
        for song, score, reasons in remaining:
            same_artist = sum(1 for p, _, _ in picked if p["artist"] == song["artist"])
            same_genre = sum(1 for p, _, _ in picked if p["genre"] == song["genre"])
            penalty = ARTIST_PENALTY * same_artist + GENRE_PENALTY * same_genre
            if best is None or score - penalty > best[1]:
                best = (song, score - penalty, reasons, same_artist, same_genre)
        song, adjusted, reasons, same_artist, same_genre = best
        reasons = list(reasons)
        if same_artist:
            reasons.append(f"diversity penalty: artist {song['artist']} already picked (-{ARTIST_PENALTY * same_artist:.1f})")
        if same_genre:
            reasons.append(f"diversity penalty: genre {song['genre']} already picked (-{GENRE_PENALTY * same_genre:.1f})")
        picked.append((song, adjusted, "; ".join(reasons)))
        remaining = [item for item in remaining if item[0] is not song]
    return picked
