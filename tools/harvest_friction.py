#!/usr/bin/env python3
"""Harvest chronicle session-friction notes into proposed `wyrd` issues.

Reads one or more chronicle repos' `log/friction.md` files (the format
`docs/design/16-session.md`'s "Session friction capture" section settles: a bullet list, each
entry naming `mechanic`, `what happened`, `what the GM did`), applies that document's own triage
line to separate a genuine engine gap from ordinary narrative color, checks each surviving
candidate against `wyrd`'s existing issues via kord's deterministic `github-issue-dedup-check`
primitive (the same one `kord-template-harvest` already uses for its own synthesized suggestions),
and prints a reviewable report -- new proposals distinct from likely duplicates. Nothing is filed
automatically (issue #95's own Definition of Done); filing a proposal for real is a separate,
explicit `gh issue create` an operator runs by hand after reviewing the report.

Never lets narrative content cross into a proposal (`CLAUDE.md`, "Nothing unpublishable may enter
this repository"): a proposal's title and body are built only from the friction entry's own
`mechanic` / `what happened` / `what the GM did` fields, never any other text from the chronicle
repo.

Run: python3 tools/harvest_friction.py --chronicle <path-or-owner/repo> [--chronicle ...]
Test: python3 -m unittest discover -s tools -p 'test_harvest_friction.py'
"""

from __future__ import annotations

import argparse
import base64
import dataclasses
import json
import os
import pathlib
import re
import subprocess
import sys
from collections.abc import Callable

# --- Parsing -----------------------------------------------------------------------------------

_ENTRY_START = re.compile(r"^-\s*mechanic:\s*(.*)$")
_WHAT_HAPPENED = re.compile(r"^\s+what happened:\s*(.*)$")
_WHAT_GM_DID = re.compile(r"^\s+what the GM did:\s*(.*)$")

_EMPTY_MECHANIC_VALUES = {"", "none", "n/a", "-"}

# The triage line from docs/design/16-session.md "What qualifies": mechanic-shaped language
# (a rule/table/roll producing an unpredicted or wrong-feeling result) or an improvisation gap.
_MECHANIC_SIGNAL = re.compile(
    r"\b(table|mechanic|rule|roll(?:ed)?|test|skill|difficulty|threshold|resolution|"
    r"track|check|die|dice|percentage|%|tier|threat|wound|taint|strain|stamina|advance|"
    r"downtime|rally|beat|arc)\b",
    re.IGNORECASE,
)
_IMPROVISE_SIGNAL = re.compile(
    r"\b(improvis\w*|nothing covered|no rule|ruled|gap|had to (?:decide|invent))\b",
    re.IGNORECASE,
)


@dataclasses.dataclass(frozen=True)
class FrictionEntry:
    """One qualifying-shaped bullet parsed from a chronicle's `log/friction.md`."""

    mechanic: str
    what_happened: str
    what_gm_did: str
    source_repo: str
    raw_index: int


@dataclasses.dataclass(frozen=True)
class MalformedEntry:
    """A bullet missing one or more of the three required fields (never guessed, never dropped
    without a record -- spec FR-008)."""

    source_repo: str
    raw_index: int
    missing_fields: tuple[str, ...]
    raw_text: str


def _split_entries(text: str) -> list[list[str]]:
    """Group friction-log lines into per-entry blocks, one block per '- mechanic:' bullet."""
    blocks: list[list[str]] = []
    current: list[str] | None = None
    for line in text.splitlines():
        if _ENTRY_START.match(line):
            if current is not None:
                blocks.append(current)
            current = [line]
        elif current is not None:
            current.append(line)
    if current is not None:
        blocks.append(current)
    return blocks


def parse_friction_log(
    text: str, source_repo: str
) -> tuple[list[FrictionEntry], list[MalformedEntry]]:
    """Parse a `log/friction.md`'s text into well-formed entries and malformed ones."""
    entries: list[FrictionEntry] = []
    malformed: list[MalformedEntry] = []
    for index, block in enumerate(_split_entries(text)):
        header_match = _ENTRY_START.match(block[0])
        mechanic = header_match.group(1).strip() if header_match else ""
        what_happened = ""
        what_gm_did = ""
        for line in block[1:]:
            happened_match = _WHAT_HAPPENED.match(line)
            if happened_match:
                what_happened = happened_match.group(1).strip()
                continue
            gm_did_match = _WHAT_GM_DID.match(line)
            if gm_did_match:
                what_gm_did = gm_did_match.group(1).strip()

        missing: list[str] = []
        if not mechanic:
            missing.append("mechanic")
        if not what_happened:
            missing.append("what happened")
        if not what_gm_did:
            missing.append("what the GM did")

        if missing:
            malformed.append(
                MalformedEntry(
                    source_repo=source_repo,
                    raw_index=index,
                    missing_fields=tuple(missing),
                    raw_text="\n".join(block),
                )
            )
        else:
            entries.append(
                FrictionEntry(
                    mechanic=mechanic,
                    what_happened=what_happened,
                    what_gm_did=what_gm_did,
                    source_repo=source_repo,
                    raw_index=index,
                )
            )
    return entries, malformed


# --- Reading a chronicle's friction log ---------------------------------------------------------


def read_chronicle_friction_log(
    chronicle: str,
    runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> str | None:
    """Read `log/friction.md` from a chronicle repo.

    `chronicle` is either a local filesystem path to a checkout, or an `owner/repo` slug fetched
    via `gh api` (no local clone required). Returns `None` -- never an error -- when the file does
    not exist (spec FR-006: a chronicle that has captured no friction yet is not a failure)."""
    local_dir = pathlib.Path(chronicle)
    if local_dir.is_dir():
        friction_path = local_dir / "log" / "friction.md"
        if friction_path.is_file():
            return friction_path.read_text(encoding="utf-8")
        return None

    proc = runner(
        ["gh", "api", f"repos/{chronicle}/contents/log/friction.md"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    try:
        payload = json.loads(proc.stdout)
        content_b64 = payload["content"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return None
    try:
        return base64.b64decode(content_b64).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return None


# --- Triage --------------------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class TriageVerdict:
    """The result of applying docs/design/16-session.md's "What qualifies" rule to one entry."""

    entry: FrictionEntry
    verdict: str  # "qualifies" | "does_not_qualify" | "needs_review"
    reason: str


def triage(entry: FrictionEntry) -> TriageVerdict:
    """Apply the triage line: qualifies (mechanic-shaped surprise, wrong-feeling correctly-applied
    result, or improvisation gap), does_not_qualify (no mechanic named at all -- ordinary color),
    or needs_review (a mechanic is named but no clear qualifying signal was found -- reported, not
    silently dropped, per spec Edge Cases / SC-002)."""
    if entry.mechanic.strip().lower() in _EMPTY_MECHANIC_VALUES:
        return TriageVerdict(entry, "does_not_qualify", "no mechanic named -- ordinary color")

    combined = f"{entry.mechanic} {entry.what_happened} {entry.what_gm_did}"
    signal = _MECHANIC_SIGNAL.search(combined) or _IMPROVISE_SIGNAL.search(combined)
    if signal:
        return TriageVerdict(
            entry, "qualifies", f"mechanic-shaped language matched ({signal.group(0)!r})"
        )
    return TriageVerdict(
        entry,
        "needs_review",
        "a mechanic is named but no clear qualifying signal was found -- needs a human read",
    )


# --- Proposal building -----------------------------------------------------------------------


@dataclasses.dataclass
class DedupVerdict:
    """The result of running github-issue-dedup-check against one proposal."""

    matched_issue: dict | None
    is_new: bool


@dataclasses.dataclass
class HarvestProposal:
    """A candidate `wyrd` issue, built only from the mechanical fields of one or more
    same-mechanic friction entries (spec FR-005 -- never any other text from the chronicle)."""

    title: str
    body: str
    source_entries: list[FrictionEntry]
    dedup_verdict: DedupVerdict | None = None


def _normalize_mechanic(mechanic: str) -> str:
    return re.sub(r"\s+", " ", mechanic.strip().lower())


def group_qualifying_entries(entries: list[FrictionEntry]) -> list[list[FrictionEntry]]:
    """Merge same-log repeats of the same mechanic into one group (spec Edge Cases: "the same
    finding appears twice within one friction log") -- so one harvest run proposes it once."""
    groups: dict[tuple[str, str], list[FrictionEntry]] = {}
    order: list[tuple[str, str]] = []
    for entry in entries:
        key = (entry.source_repo, _normalize_mechanic(entry.mechanic))
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(entry)
    return [groups[key] for key in order]


def build_proposal(entries: list[FrictionEntry]) -> HarvestProposal:
    """Build a proposal from one or more (same-mechanic) friction entries. The title names only
    the mechanic; the body restates each entry's what-happened/what-the-GM-did verbatim, plus
    provenance -- nothing else is appended (spec FR-005)."""
    if not entries:
        raise ValueError("build_proposal requires at least one entry")
    primary = entries[0]
    title = f"Friction: {primary.mechanic}"
    lines = [f"Mechanic: {primary.mechanic}", ""]
    for entry in entries:
        lines.append(f"- Source: {entry.source_repo}")
        lines.append(f"  What happened: {entry.what_happened}")
        lines.append(f"  What the GM did: {entry.what_gm_did}")
    body = "\n".join(lines)
    return HarvestProposal(title=title, body=body, source_entries=list(entries))


# --- Duplicate detection ---------------------------------------------------------------------


def _find_kord_client() -> pathlib.Path | None:
    """Locate kord's client.py. Checked in order: an explicit `KORD_CLIENT_PY` override, the
    `CLAUDE_PLUGIN_ROOT` a kord skill invocation sets, then the plugin cache's usual install
    location. Returns `None` (never raises) if nothing is found -- dedup then fails open (a
    proposal is reported as new rather than the whole harvest erroring), since a missing
    kord installation is an environment gap, not a defect in a friction entry."""
    candidates: list[pathlib.Path] = []
    env_override = os.environ.get("KORD_CLIENT_PY")
    if env_override:
        candidates.append(pathlib.Path(env_override))
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root:
        candidates.append(pathlib.Path(plugin_root) / "src" / "kord" / "client.py")
    candidates.append(
        pathlib.Path.home()
        / ".claude"
        / "plugins"
        / "cache"
        / "kord"
        / "kord"
        / "plugin"
        / "src"
        / "kord"
        / "client.py"
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def check_duplicate(
    proposal: HarvestProposal,
    repo: str = "neilgfoster/wyrd",
    runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
    client_path: pathlib.Path | None = None,
) -> DedupVerdict:
    """Check `proposal` against `repo`'s existing issues via kord's `github-issue-dedup-check`
    primitive (specs/057-harvest-dedup in the kord repo) -- the same deterministic keyword/skill-
    name/file-path overlap check `kord-template-harvest` already uses for its own suggestions."""
    client = client_path if client_path is not None else _find_kord_client()
    if client is None:
        return DedupVerdict(matched_issue=None, is_new=True)

    text = f"{proposal.title}\n\n{proposal.body}"
    proc = runner(
        [
            "python3",
            str(client),
            "github-issue-dedup-check",
            "--repo",
            repo,
            "--text",
            text,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return DedupVerdict(matched_issue=None, is_new=True)
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return DedupVerdict(matched_issue=None, is_new=True)

    matched = result.get("match")
    return DedupVerdict(matched_issue=matched, is_new=matched is None)


# --- Per-chronicle harvest -------------------------------------------------------------------


@dataclasses.dataclass
class HarvestReport:
    """The full result of harvesting one chronicle repo's friction log."""

    source_repo: str
    new_proposals: list[HarvestProposal]
    duplicate_proposals: list[HarvestProposal]
    malformed_entries: list[MalformedEntry]
    non_qualifying_entries: list[TriageVerdict]
    needs_review_entries: list[TriageVerdict]


def harvest_chronicle(
    chronicle: str,
    *,
    read: Callable[[str], str | None] = read_chronicle_friction_log,
    dedup_repo: str = "neilgfoster/wyrd",
    dedup_runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
    dedup_client_path: pathlib.Path | None = None,
) -> HarvestReport:
    """Read, triage, propose, and dedup-check one chronicle's friction log end to end."""
    text = read(chronicle)
    if text is None:
        return HarvestReport(
            source_repo=chronicle,
            new_proposals=[],
            duplicate_proposals=[],
            malformed_entries=[],
            non_qualifying_entries=[],
            needs_review_entries=[],
        )

    entries, malformed = parse_friction_log(text, chronicle)
    verdicts = [triage(entry) for entry in entries]

    qualifying = [v.entry for v in verdicts if v.verdict == "qualifies"]
    non_qualifying = [v for v in verdicts if v.verdict == "does_not_qualify"]
    needs_review = [v for v in verdicts if v.verdict == "needs_review"]

    new_proposals: list[HarvestProposal] = []
    duplicate_proposals: list[HarvestProposal] = []
    for group in group_qualifying_entries(qualifying):
        proposal = build_proposal(group)
        proposal.dedup_verdict = check_duplicate(
            proposal,
            repo=dedup_repo,
            runner=dedup_runner,
            client_path=dedup_client_path,
        )
        if proposal.dedup_verdict.is_new:
            new_proposals.append(proposal)
        else:
            duplicate_proposals.append(proposal)

    return HarvestReport(
        source_repo=chronicle,
        new_proposals=new_proposals,
        duplicate_proposals=duplicate_proposals,
        malformed_entries=malformed,
        non_qualifying_entries=non_qualifying,
        needs_review_entries=needs_review,
    )


# --- CLI reporting ---------------------------------------------------------------------------


def format_report(report: HarvestReport) -> str:
    lines = [f"=== {report.source_repo} ==="]

    if not (
        report.new_proposals
        or report.duplicate_proposals
        or report.malformed_entries
        or report.non_qualifying_entries
        or report.needs_review_entries
    ):
        lines.append("nothing to harvest (no log/friction.md, or an empty log)")
        return "\n".join(lines)

    if report.new_proposals:
        lines.append(f"\n-- {len(report.new_proposals)} new proposal(s) --")
        for proposal in report.new_proposals:
            lines.append(f"\n[NEW] {proposal.title}")
            lines.append(proposal.body)

    if report.duplicate_proposals:
        lines.append(f"\n-- {len(report.duplicate_proposals)} likely duplicate(s) --")
        for proposal in report.duplicate_proposals:
            matched = proposal.dedup_verdict.matched_issue if proposal.dedup_verdict else None
            matched_ref = f"#{matched['number']} ({matched['url']})" if matched else "unknown"
            lines.append(f"\n[DUPLICATE of {matched_ref}] {proposal.title}")
            lines.append(proposal.body)

    if report.needs_review_entries:
        lines.append(f"\n-- {len(report.needs_review_entries)} entr(y/ies) needing review --")
        for verdict in report.needs_review_entries:
            lines.append(f"- mechanic: {verdict.entry.mechanic} ({verdict.reason})")

    if report.non_qualifying_entries:
        lines.append(f"\n-- {len(report.non_qualifying_entries)} non-qualifying (color) --")
        for verdict in report.non_qualifying_entries:
            lines.append(f"- {verdict.entry.what_happened[:80]!r} ({verdict.reason})")

    if report.malformed_entries:
        lines.append(f"\n-- {len(report.malformed_entries)} malformed entr(y/ies), skipped --")
        for malformed in report.malformed_entries:
            missing = ", ".join(malformed.missing_fields)
            lines.append(f"- entry #{malformed.raw_index} missing: {missing}")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    parser.add_argument(
        "--chronicle",
        action="append",
        required=True,
        help=(
            "A chronicle repo: a local checkout path, or an owner/repo slug fetched via "
            "'gh api'. Repeatable."
        ),
    )
    parser.add_argument(
        "--dedup-repo",
        default="neilgfoster/wyrd",
        help="The wyrd repo to check proposals against for duplicates (default: %(default)s).",
    )
    args = parser.parse_args(argv)

    exit_code = 0
    for chronicle in args.chronicle:
        report = harvest_chronicle(chronicle, dedup_repo=args.dedup_repo)
        print(format_report(report))
        print()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
