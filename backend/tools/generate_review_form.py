"""Generate a Google Apps Script that builds a rule-review form.

Every rule the application applies becomes one item an astrologer can mark
correct or flag, with room to say what should change instead. Responses land in
a Google Sheet, one row per submission.

    python -m tools.generate_review_form

Writes docs/review-form.gs. Paste it into script.google.com and run
``buildReviewForm`` once; it logs the form's edit and share URLs.

The rules are baked into the script, so it needs nothing from this repo at run
time. Regenerate whenever the rules change.
"""
from __future__ import annotations

import json
import os
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.astrology.rules.registry import all_rules  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "docs" / "review-form.gs"

# Same grouping as the rule reference, so a reviewer can work through the form
# alongside docs/RULES.pdf.
SECTIONS = [
    ("Time, place and configuration", ("TIME_", "CONFIG_", "GEO_"),
     "How the birth moment and the chart settings are resolved."),
    ("Houses and Nakshatras", ("HOUSE_", "NAK_"),
     "Which house frame is used, and how nakshatra lords are assigned."),
    ("Dignity", ("DIGNITY_", "VARGA_", "COMBUST_"),
     "Exaltation, debilitation, own sign, Mooltrikona, Vargottama, combustion."),
    ("Benefic, malefic and neutral", ("NATURE_",),
     "What each graha and each house is counted as, and how a graha's "
     "functional nature is decided for a given Lagna."),
    ("Friendship between planets", ("MAITRI_",),
     "Natural, temporary and the combined Panchadha Maitri."),
    ("Functional classification", ("FUNC_",),
     "Kendra, Trikona, Dusthana, Upachaya, Maraka, Badhaka, Yoga Karaka."),
    ("Avasthas", ("KUMARADI_", "CHAITANYADI_"),
     "The Kumaradi and Chaitanyadi degree bands."),
    ("Aspects, conjunction and structure", ("ASPECT_", "CONJ_", "DISPOSITOR_",
                                            "BENEFIC_"),
     "Graha Drishti, same-sign conjunction, dispositor chains."),
    ("Neecha Bhanga", ("NB_",),
     "The six conditions under which a debilitation is held to be cancelled."),
    ("Rahu and Ketu", ("RK_",),
     "Every point where the nodes are treated differently from the seven."),
    ("Yogas", ("YOGA_",), "The 22 yogas checked."),
    ("Doshas", ("DOSHA_",), "The 14 doshas checked."),
]

VERDICTS = [
    "Correct as stated",
    "Correct, but the wording could be clearer",
    "Needs a change",
    "Not sure / skip",
]

HEADER = """/**
 * Rule review form for the Planetary Status Analyzer.
 *
 * GENERATED FILE - do not edit by hand.
 * Regenerate with:  python -m tools.generate_review_form
 *
 * How to use
 * ----------
 *  1. Open https://script.google.com and start a new project.
 *  2. Replace the contents of Code.gs with this file.
 *  3. Run buildReviewForm(). Approve the permissions it asks for; it needs to
 *     create a form and a spreadsheet on your account.
 *  4. The execution log prints two links: one to edit the form, one to send to
 *     the astrologer.
 *
 * Each rule becomes a required multiple-choice question and an optional
 * comment box. Responses collect in a linked Google Sheet, one row per
 * submission, so several reviewers can be compared side by side.
 */

var FORM_TITLE = %(title)s;
var FORM_DESCRIPTION = %(description)s;
var VERDICTS = %(verdicts)s;
var SECTIONS = %(sections)s;

function buildReviewForm() {
  var form = FormApp.create(FORM_TITLE)
      .setDescription(FORM_DESCRIPTION)
      .setProgressBar(true)
      .setAllowResponseEdits(true)
      .setShowLinkToRespondAgain(false);

  form.addTextItem()
      .setTitle('Your name')
      .setHelpText('So a follow-up question can reach the right person.')
      .setRequired(true);

  form.addParagraphTextItem()
      .setTitle('Which tradition or lineage do you follow?')
      .setHelpText('Useful context where the classics differ. Optional.')
      .setRequired(false);

  var total = 0;
  for (var s = 0; s < SECTIONS.length; s++) {
    var section = SECTIONS[s];

    form.addPageBreakItem()
        .setTitle(section.title)
        .setHelpText(section.blurb + '  (' + section.rules.length +
                     (section.rules.length === 1 ? ' rule)' : ' rules)'));

    for (var r = 0; r < section.rules.length; r++) {
      var rule = section.rules[r];
      total++;

      form.addMultipleChoiceItem()
          .setTitle(rule.id + ' - ' + rule.name)
          .setHelpText(rule.statement)
          .setChoiceValues(VERDICTS)
          .setRequired(true);

      form.addParagraphTextItem()
          .setTitle(rule.id + ' - what should change?')
          .setHelpText('Only if you marked it above. A source or citation helps.')
          .setRequired(false);
    }
  }

  form.addPageBreakItem()
      .setTitle('Anything else')
      .setHelpText('Rules that are missing, or anything the form did not ask.');

  form.addParagraphTextItem()
      .setTitle('Rules you would add or remove')
      .setRequired(false);

  form.addParagraphTextItem()
      .setTitle('Any other comment')
      .setRequired(false);

  var sheet = SpreadsheetApp.create(FORM_TITLE + ' - responses');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, sheet.getId());

  Logger.log('Rules in the form : ' + total);
  Logger.log('Edit the form     : ' + form.getEditUrl());
  Logger.log('Send this link    : ' + form.getPublishedUrl());
  Logger.log('Responses sheet   : ' + sheet.getUrl());
  return form.getPublishedUrl();
}
"""


def statement(rule) -> str:
    """The rule in the reviewer's terms: what it says, and what it produces."""
    text = " ".join(rule.description.split())
    if rule.output:
        text += f"   [Result: {' '.join(rule.output.split())}]"
    return text


def build() -> str:
    rules = all_rules()
    by_id = {r.rule_id: r for r in rules}
    placed: set[str] = set()
    sections = []

    for title, prefixes, blurb in SECTIONS:
        members = [r for r in rules if r.rule_id.startswith(prefixes)]
        placed.update(r.rule_id for r in members)
        if not members:
            continue
        sections.append({
            "title": title,
            "blurb": blurb,
            "rules": [{"id": r.rule_id, "name": r.name,
                       "statement": statement(r)} for r in members],
        })

    # Anything the grouping missed still has to reach the reviewer.
    leftover = [r for r in rules if r.rule_id not in placed]
    if leftover:
        sections.append({
            "title": "Other rules",
            "blurb": "Rules not covered by the sections above.",
            "rules": [{"id": r.rule_id, "name": r.name,
                       "statement": statement(r)} for r in leftover],
        })

    counted = sum(len(s["rules"]) for s in sections)
    assert counted == len(rules), f"{counted} placed, {len(rules)} exist"

    description = textwrap.dedent(f"""\
        Every rule this software applies, one at a time, for you to confirm or
        correct.

        There are {len(rules)} rules across {len(sections)} sections. Each shows
        exactly what the software does. Mark it correct, or say what it should
        do instead. A citation is welcome but not required.

        The full reference with all the tables is in RULES.pdf. Nothing here
        interprets a chart or predicts anything; these are only the rules used
        to derive the facts.""")

    return HEADER % {
        "title": json.dumps("Planetary Status Analyzer - rule review"),
        "description": json.dumps(description),
        "verdicts": json.dumps(VERDICTS, indent=2),
        "sections": json.dumps(sections, indent=2, ensure_ascii=False),
    }


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build(), encoding="utf-8")
    n = len(all_rules())
    print(f"Wrote {OUT} ({os.path.getsize(OUT):,} bytes)")
    print(f"{n} rules, {n * 2 + 4} form questions")
