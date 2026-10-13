"""
Spam filter agent (simple reflex agent, AIMA Chapter 2).

Book structure:
    function SIMPLE-REFLEX-AGENT(percept) returns an action
        persistent: rules, a set of condition-action rules
        state  <- INTERPRET-INPUT(percept)
        rule   <- RULE-MATCH(state, rules)
        action <- rule.ACTION
        return action

Percept : path to one .eml file
Action  : "spam" or "email" (the directory the file is moved to)

Assumptions:
  - If a domain is on BOTH the allow and restrict lists, allow wins.
  - "More than 5 bad words" counts total occurrences in the body
    (every occurrence counts, so 6 hits = spam, 5 hits = not spam).
  - Subdomains match their parent (mail.seneca.ca matches seneca.ca).
  - Only text/* parts (body and text attachments) are read.
"""
import argparse
import re
import shutil
from dataclasses import dataclass
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
MAX_BAD_WORDS = 5

SPAM = "spam"
EMAIL = "email"


def load_list(path):
    """Read one entry per line into a lowercase set (ignores blanks and # comments)."""
    with open(path, encoding="utf-8") as f:
        return {
            line.strip().lower()
            for line in f
            if line.strip() and not line.startswith("#")
        }


def domain_matches(domain, domain_list):
    return any(domain == d or domain.endswith("." + d) for d in domain_list)


@dataclass
class State:
    """What the agent understands about the current email."""
    sender_domain: str
    on_allow_list: bool
    on_restrict_list: bool
    bad_word_count: int


class SpamFilterAgent:
    def __init__(self, allow_list, restrict_list, bad_words):
        self.allow_list = set(allow_list)
        self.restrict_list = set(restrict_list)
        self.bad_words = set(bad_words)
        # persistent: rules (condition, action), checked in order
        self.rules = [
            (lambda s: s.on_allow_list, EMAIL),
            (lambda s: s.on_restrict_list, SPAM),
            (lambda s: s.bad_word_count > MAX_BAD_WORDS, SPAM),
            (lambda s: True, EMAIL),  # default rule
        ]

    @classmethod
    def from_files(cls, data_dir=DATA_DIR):
        data_dir = Path(data_dir)
        return cls(
            load_list(data_dir / "allow_list.txt"),
            load_list(data_dir / "restrict_list.txt"),
            load_list(data_dir / "bad_words.txt"),
        )

    def __call__(self, percept):
        """SIMPLE-REFLEX-AGENT(percept)"""
        state = self.interpret_input(percept)
        action = self.rule_match(state)
        return action

    def interpret_input(self, percept):
        """Turn the raw .eml file into an abstract State."""
        with open(percept, "rb") as f:
            msg = BytesParser(policy=policy.default).parse(f)

        _, address = parseaddr(str(msg.get("From", "")))
        domain = address.rsplit("@", 1)[-1].lower() if "@" in address else ""

        body = self._extract_text(msg)
        words = re.findall(r"[a-z']+", body.lower())
        count = sum(1 for w in words if w in self.bad_words)

        return State(
            sender_domain=domain,
            on_allow_list=domain_matches(domain, self.allow_list),
            on_restrict_list=domain_matches(domain, self.restrict_list),
            bad_word_count=count,
        )

    def rule_match(self, state):
        """Return the action of the first rule whose condition is true."""
        for condition, action in self.rules:
            if condition(state):
                return action

    @staticmethod
    def _extract_text(msg):
        parts = []
        for part in msg.walk():
            if part.is_multipart() or part.get_content_maintype() != "text":
                continue
            try:
                parts.append(part.get_content())  # decodes base64 / quoted-printable
            except (LookupError, UnicodeDecodeError):
                payload = part.get_payload(decode=True) or b""
                parts.append(payload.decode("utf-8", errors="ignore"))
        return "\n".join(parts)


def run_environment(agent, inbox, spam_dir, email_dir):
    """Feed every .eml in inbox to the agent and carry out its action (actuator)."""
    spam_dir, email_dir = Path(spam_dir), Path(email_dir)
    spam_dir.mkdir(parents=True, exist_ok=True)
    email_dir.mkdir(parents=True, exist_ok=True)

    results = {SPAM: 0, EMAIL: 0}
    for eml in sorted(Path(inbox).glob("*.eml")):
        action = agent(eml)
        target = spam_dir if action == SPAM else email_dir
        shutil.move(str(eml), str(target / eml.name))
        results[action] += 1
        print(f"{eml.name} -> {action}")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spam filter agent")
    parser.add_argument("inbox", help="folder containing .eml files")
    parser.add_argument("--spam-dir", default="spam")
    parser.add_argument("--email-dir", default="email")
    args = parser.parse_args()

    agent = SpamFilterAgent.from_files()
    print(run_environment(agent, args.inbox, args.spam_dir, args.email_dir))