from pathlib import Path

from src.core.models import ResidentNoteModel
from src.parsers.policy_parser import PolicyParserImpl
from src.services.compliance_engine import ComplianceEngine


def _engine() -> ComplianceEngine:
    rules = PolicyParserImpl(Path("data/raw/Falls_Management_Policy_ProcessX.docx")).parse()
    return ComplianceEngine(rules)


def test_john_doe_day1_no_flags():
    note = ResidentNoteModel(
        resident_name="John Doe",
        day_label="Day 1",
        date="10 June 2025",
        documented_by="RN Sarah Okafor",
        note_text=(
            "Date: 10 June 2025 | Time of fall: 07:15\n"
            "Resident found on floor beside bed by carer during morning round. Fall not witnessed.\n"
            "Complaining of pain in left knee — rates 5/10.\n"
            "Vital signs taken: BP 148/86, HR 78, RR 16, Temp 36.5, SpO2 97%.\n"
            "GP (Dr Maria Santos) notified at 07:40. Advised to monitor pain and mobility.\n"
            "NOK: Wife (Helen Doe) notified at 07:55. Acknowledged and will visit today.\n"
            "Risk factors identified: Two previous falls in the past six months.\n"
            "Care plan reviewed and updated: Yes.\n"
            "Falls risk score reassessed and documented — HIGH."
        ),
    )
    assert _engine().analyze(note) == []


def test_peter_parker_day1_flags_are_specific():
    note = ResidentNoteModel(
        resident_name="Peter Parker",
        day_label="Day 1",
        date="10 June 2025",
        documented_by="RN James Obi",
        note_text=(
            "Resident found on floor in corridor near nurses station. Witnessed by AIN Tom Baxter. "
            "Complaining of right hip pain. Alert and orientated. No visible injury.\n"
            "Immediate actions: Assisted back to wheelchair. Comfort measures applied.\n"
            "GP (Dr Kevin Park) notified. Advised to monitor.\n"
            "Family has been informed.\n"
            "Risk factors: History of falls. On blood pressure medication.\n"
            "Care plan: Will update."
        ),
    )
    flags = _engine().analyze(note)
    fields = {flag.field for flag in flags}
    assert "Pain scale" in fields
    assert "Vital signs" in fields
    assert "GP notification time" in fields
    assert "NOK notification" in fields
    assert "Care plan review" in fields
