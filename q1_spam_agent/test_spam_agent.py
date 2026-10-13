import shutil
from pathlib import Path

import pytest

from spam_agent import EMAIL, SPAM, SpamFilterAgent, run_environment

TEST_DATA = Path(__file__).parent / "test_data"

# Fixed lists so the tests never depend on edits to data/*.txt
ALLOW = {"seneca.ca", "both.com"}
RESTRICT = {"spamdomain.com", "both.com"}
BAD_WORDS = {"free", "winner", "prize", "cash", "lottery", "urgent"}

CASES = [
    ("01_allow_listed_many_bad_words.eml", EMAIL),  # allow list beats bad words
    ("02_restricted_clean_body.eml", SPAM),         # restrict list beats clean body
    ("03_unknown_six_bad_words.eml", SPAM),         # 6 > 5
    ("04_unknown_five_bad_words.eml", EMAIL),       # 5 is not more than 5
    ("05_base64_six_bad_words.eml", SPAM),          # encoded body is decoded
    ("06_attachment_six_bad_words.eml", SPAM),      # text attachment is read
    ("07_clean_unknown_sender.eml", EMAIL),
    ("08_domain_on_both_lists.eml", EMAIL),         # allow wins over restrict
]


@pytest.fixture
def agent():
    return SpamFilterAgent(ALLOW, RESTRICT, BAD_WORDS)


@pytest.mark.parametrize("filename, expected", CASES)
def test_agent_decision(agent, filename, expected):
    assert agent(TEST_DATA / filename) == expected


def test_environment_moves_files(agent, tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    for filename, _ in CASES:
        shutil.copy(TEST_DATA / filename, inbox / filename)

    spam_dir = tmp_path / "spam"
    email_dir = tmp_path / "email"
    run_environment(agent, inbox, spam_dir, email_dir)

    for filename, expected in CASES:
        folder = spam_dir if expected == SPAM else email_dir
        assert (folder / filename).exists(), filename
    assert list(inbox.glob("*.eml")) == []