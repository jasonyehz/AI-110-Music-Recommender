from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# --- Advanced attributes, scoring modes, and diversity ---

import pytest

from src.recommender import load_songs, recommend_songs, score_song


def make_song_dict(**overrides) -> dict:
    song = {
        "id": 1, "title": "T", "artist": "A", "genre": "pop", "mood": "happy",
        "energy": 0.8, "tempo_bpm": 120.0, "valence": 0.8, "danceability": 0.8,
        "acousticness": 0.2, "popularity": 50, "release_decade": 2020,
        "mood_tags": ["warm", "bright"], "instrumentalness": 0.1, "language": "english",
    }
    song.update(overrides)
    return song


def test_load_songs_converts_types_and_splits_tags():
    songs = load_songs("data/songs.csv")
    first = songs[0]
    assert isinstance(first["id"], int)
    assert isinstance(first["energy"], float)
    assert isinstance(first["popularity"], int)
    assert isinstance(first["release_decade"], int)
    assert isinstance(first["mood_tags"], list) and first["mood_tags"]


def test_advanced_attributes_only_scored_when_user_asks():
    song = make_song_dict()
    base_score, _ = score_song({"genre": "pop", "mood": "happy", "energy": 0.8}, song)
    assert base_score == pytest.approx(4.5)

    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8, "tags": ["warm", "dark"], "decade": 2020}
    score, reasons = score_song(prefs, song)
    # tags: half of the wanted tags match (+0.5), decade matches exactly (+0.5)
    assert score == pytest.approx(5.5)
    assert any("mood tags" in reason for reason in reasons)


def test_decade_closeness_rewards_nearer_decades():
    prefs = {"decade": 1990}
    near, _ = score_song(prefs, make_song_dict(release_decade=2000))
    far, _ = score_song(prefs, make_song_dict(release_decade=1960))
    assert near > far


def test_modes_change_the_ranking():
    pop_song = make_song_dict(id=1, title="Pop", genre="pop", mood="happy", energy=0.8)
    chill_song = make_song_dict(id=2, title="Chill", genre="lofi", mood="chill", energy=0.3)
    prefs = {"genre": "pop", "mood": "chill", "energy": 0.3}

    genre_first = recommend_songs(prefs, [pop_song, chill_song], k=2, mode="genre-first")
    mood_first = recommend_songs(prefs, [pop_song, chill_song], k=2, mode="mood-first")
    assert genre_first[0][0]["title"] == "Pop"
    assert mood_first[0][0]["title"] == "Chill"


def test_unknown_mode_raises():
    with pytest.raises(ValueError):
        score_song({"genre": "pop"}, make_song_dict(), mode="nope")


def test_diversity_penalty_demotes_repeated_artist():
    songs = [
        make_song_dict(id=1, title="First", artist="Same", genre="pop", energy=0.80),
        make_song_dict(id=2, title="Second", artist="Same", genre="pop", mood="chill", energy=0.79),
        make_song_dict(id=3, title="Other", artist="Different", genre="jazz", mood="happy", energy=0.78),
    ]
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    plain = [s["title"] for s, _, _ in recommend_songs(prefs, songs, k=3)]
    diverse = recommend_songs(prefs, songs, k=3, diversity=True)
    assert plain[:2] == ["First", "Second"]
    assert [s["title"] for s, _, _ in diverse][:2] == ["First", "Other"]
    assert "diversity penalty" in diverse[-1][2]


# --- Edge cases found in the bug sweep ---

from src.main import format_table


def test_negative_k_is_rejected():
    songs = [make_song_dict()]
    with pytest.raises(ValueError):
        recommend_songs({"genre": "pop"}, songs, k=-1)
    with pytest.raises(ValueError):
        recommend_songs({"genre": "pop"}, songs, k=-1, diversity=True)


def test_k_larger_than_catalog_and_zero():
    songs = [make_song_dict(id=1), make_song_dict(id=2)]
    assert len(recommend_songs({"genre": "pop"}, songs, k=10)) == 2
    assert len(recommend_songs({"genre": "pop"}, songs, k=10, diversity=True)) == 2
    assert recommend_songs({"genre": "pop"}, songs, k=0) == []


def test_empty_table_does_not_crash():
    assert "Title" in format_table([])


def test_text_preferences_ignore_case_and_spaces():
    song = make_song_dict()
    score, reasons = score_song({"genre": " Pop ", "mood": "HAPPY", "language": "English"}, song)
    assert score == pytest.approx(2.0 + 1.0 + 0.5)


def test_tags_ignore_case_duplicates_and_plain_strings():
    song = make_song_dict(mood_tags=["warm", "bright"])
    assert score_song({"tags": ["Warm"]}, song)[0] == pytest.approx(1.0)
    assert score_song({"tags": ["bright", "bright"]}, song)[0] == pytest.approx(1.0)
    assert score_song({"tags": "warm"}, song)[0] == pytest.approx(1.0)
    assert score_song({"tags": []}, song)[0] == 0.0


def test_numeric_preferences_given_as_text_still_work():
    song = make_song_dict(energy=0.8)
    assert score_song({"energy": "0.8"}, song)[0] == pytest.approx(1.5)


def test_recommender_handles_duplicate_song_ids():
    def song(title):
        return Song(1, title, "x", "pop", "happy", 0.5, 100, 0.5, 0.5, 0.5)
    rec = Recommender([song("a"), song("b")])
    user = UserProfile("pop", "happy", 0.5, False)
    assert sorted(s.title for s in rec.recommend(user, k=2)) == ["a", "b"]


def test_load_songs_reports_bad_rows(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text(
        "id,title,artist,genre,mood,energy,tempo_bpm,valence,danceability,acousticness,"
        "popularity,release_decade,mood_tags,instrumentalness,language\n"
        "1,T,A,pop,happy,not-a-number,100,0.5,0.5,0.5,50,2020,warm,0.1,english\n"
    )
    with pytest.raises(ValueError, match="line 2"):
        load_songs(str(bad))
