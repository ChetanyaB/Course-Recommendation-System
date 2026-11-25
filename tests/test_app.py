"""Functional test cases for the Course Recommendation System (run: pytest -v)."""
import os
import sys

import pytest
from markupsafe import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)  # app.py loads the .pkl files with relative paths

import app as course_app  # noqa: E402


@pytest.fixture()
def client():
    course_app.app.config["TESTING"] = True
    return course_app.app.test_client()


def test_tc01_home_page_lists_top_50(client):
    r = client.get("/")
    assert r.status_code == 200
    assert len(course_app.popular_df) == 50


def test_tc02_subject_search_returns_10_courses(client):
    r = client.post("/recommend_course", data={"user_in": "Python"})
    assert r.status_code == 200
    expected = course_app.course[course_app.course["subject"].str.strip() == "python"][0:10]
    assert len(expected) == 10
    html = r.data.decode()
    for name in expected["course name"]:
        assert escape(name.strip()) in html


def test_tc03_subject_search_is_case_insensitive(client):
    a = client.post("/recommend_course", data={"user_in": "MACHINE LEARNING"}).data
    b = client.post("/recommend_course", data={"user_in": "machine learning"}).data
    assert a == b


def test_tc04_subject_with_trailing_space_in_dataset(client):
    # 'ui ux designing ' is stored with a trailing space; this crashed the original code
    r = client.post("/recommend_course", data={"user_in": "ui ux designing"})
    assert r.status_code == 200
    assert b"SORRY" not in r.data


def test_tc05_unknown_subject_shows_friendly_message(client):
    r = client.post("/recommend_course", data={"user_in": "cooking"})
    assert r.status_code == 200
    assert b"SORRY FOR THE INCONVENIENCE" in r.data


def test_tc06_empty_subject_shows_friendly_message(client):
    r = client.post("/recommend_course", data={"user_in": "   "})
    assert r.status_code == 200
    assert b"SORRY FOR THE INCONVENIENCE" in r.data


def test_tc07_similar_courses_returns_5(client):
    r = client.post("/recommend_course_", data={"user_input": "AI For Everyone"})
    assert r.status_code == 200
    assert b"AI Foundations for Everyone Specialization" in r.data


def test_tc08_similar_courses_excludes_query_course(client):
    name = "AI For Everyone"
    idx = list(course_app.pt.index).index(name)
    top = sorted(enumerate(course_app.similarity_score[idx]), key=lambda x: x[1], reverse=True)[1:6]
    assert idx not in [i for i, _ in top]
    assert len(top) == 5


def test_tc09_unknown_course_shows_friendly_message(client):
    r = client.post("/recommend_course_", data={"user_input": "xyz"})
    assert r.status_code == 200
    assert b"Course not found" in r.data


def test_tc10_course_lookup_is_case_insensitive(client):
    r = client.post("/recommend_course_", data={"user_input": "ai for everyone"})
    assert r.status_code == 200
    assert b"Course not found" not in r.data
