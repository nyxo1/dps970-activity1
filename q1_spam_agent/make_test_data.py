"""Run once:  python q1_spam_agent/make_test_data.py"""
from email.message import EmailMessage
from pathlib import Path

OUT = Path(__file__).parent / "test_data"
OUT.mkdir(exist_ok=True)

SIX = "free winner prize cash lottery urgent"
FIVE = "free winner prize cash lottery"
CLEAN = "Hi, here are the notes from today's lecture. See you Friday."


def make(filename, sender, body, base64=False, attachment=None):
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = "student@example.com"
    msg["Subject"] = "Test email"
    if base64:
        msg.set_content(body, cte="base64")
    else:
        msg.set_content(body)
    if attachment:
        msg.add_attachment(attachment, subtype="plain", filename="notes.txt")
    (OUT / filename).write_bytes(bytes(msg))


make("01_allow_listed_many_bad_words.eml", "Prof <boss@seneca.ca>", SIX + " " + SIX)
make("02_restricted_clean_body.eml", "Promo <promo@spamdomain.com>", CLEAN)
make("03_unknown_six_bad_words.eml", "Bob <bob@random.org>", SIX)
make("04_unknown_five_bad_words.eml", "Bob <bob@random.org>", FIVE)
make("05_base64_six_bad_words.eml", "Bob <bob@random.org>", SIX, base64=True)
make("06_attachment_six_bad_words.eml", "Bob <bob@random.org>",
     "Hello, see attached.", attachment=SIX)
make("07_clean_unknown_sender.eml", "Amy <amy@random.org>", CLEAN)
make("08_domain_on_both_lists.eml", "Zed <zed@both.com>", CLEAN)
print("Created sample emails in", OUT)