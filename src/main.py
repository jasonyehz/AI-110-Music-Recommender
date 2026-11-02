"""
Command line runner for the Music Recommender Simulation.

Examples:
    python -m src.main
    python -m src.main --mode mood-first
    python -m src.main --diversity --profile "chill lofi"
"""

import argparse
import textwrap

from src.recommender import DEFAULT_MODE, SCORING_MODES, load_songs, recommend_songs


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

# Profiles that use the advanced song attributes (tags, decade, popularity, ...).
ADVANCED_PROFILES = {
    "Nostalgic 90s country fan": {
        "genre": "country", "mood": "nostalgic", "energy": 0.5,
        "decade": 1990, "tags": ["nostalgic", "warm"], "language": "english",
    },
    "Instrumental study music": {
        "genre": "lofi", "mood": "focused", "energy": 0.4,
        "instrumentalness": 0.9, "tags": ["focused", "studious"], "popularity": 50,
    },
}

ALL_PROFILES = {**STANDARD_PROFILES, **ADVERSARIAL_PROFILES, **ADVANCED_PROFILES}
REASON_WIDTH = 62


def format_table(recommendations: list) -> str:
    """Build an ASCII table of rank, title, artist, score, and wrapped reasons."""
    headers = ["#", "Title", "Artist", "Score", "Reasons"]
    rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        reasons = textwrap.wrap(explanation, REASON_WIDTH) or [""]
        rows.append([[str(rank)], [song["title"]], [song["artist"]], [f"{score:.2f}"], reasons])

    widths = [
        max(len(headers[i]), *(len(line) for row in rows for line in row[i]))
        for i in range(len(headers))
    ]
    border = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def line(cells: list) -> str:
        return "| " + " | ".join(cell.ljust(w) for cell, w in zip(cells, widths)) + " |"

    out = [border, line(headers), border]
    for row in rows:
        for i in range(max(len(cell) for cell in row)):
            out.append(line([cell[i] if i < len(cell) else "" for cell in row]))
        out.append(border)
    return "\n".join(out)


def describe_profile(user_prefs: dict) -> str:
    """Return a one-line summary of a user profile."""
    return ", ".join(f"{key}={value}" for key, value in user_prefs.items())


def print_recommendations(name: str, user_prefs: dict, songs: list, mode: str, diversity: bool, k: int = 5) -> None:
    """Print the top k recommendations for one profile as a table."""
    print(f"{name}")
    print(f"Profile: {describe_profile(user_prefs)}")
    print(f"Mode: {mode} | Diversity penalty: {'on' if diversity else 'off'}")
    print(format_table(recommend_songs(user_prefs, songs, k=k, mode=mode, diversity=diversity)))
    print()


def parse_args() -> argparse.Namespace:
    """Read the command line options."""
    parser = argparse.ArgumentParser(description="Music Recommender Simulation")
    parser.add_argument("--mode", choices=list(SCORING_MODES), default=DEFAULT_MODE, help="scoring strategy")
    parser.add_argument("--diversity", action="store_true", help="penalize repeated artists and genres")
    parser.add_argument("--profile", help="only run profiles whose name contains this text")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    chosen = {
        name: prefs for name, prefs in ALL_PROFILES.items()
        if not args.profile or args.profile.lower() in name.lower()
    }
    if not chosen:
        raise SystemExit(f"No profile matches '{args.profile}'. Options: {', '.join(ALL_PROFILES)}")

    for name, prefs in chosen.items():
        print_recommendations(name, prefs, songs, args.mode, args.diversity)


if __name__ == "__main__":
    main()
