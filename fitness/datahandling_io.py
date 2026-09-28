import csv
import re

from collections import defaultdict
from pathlib import Path

from .models import (
    Obs,
    Person,
    Ref,
    Session
)

# Custom exceptions
class InvalidIdentifierError(ValueError):   # ID wrong format
    """Used when an ID does not match the required format."""


class InvalidRecordError(ValueError):       
    """Raised when a CSV record cannot be accepted."""

    def __init__(self, fld, msg):
        super().__init__(msg)
        self.fld = fld

# regex 
PID_RE = re.compile(        # p + 3 numbers
    r"^P\d{3}$"             # P001
)

SID_RE = re.compile(        # FIT + 4 numbers + (-) + 3 numbers
    r"^FIT-\d{4}-\d{3}$"    # FIT-2026-001
)

# Informs the program which colloums participants.csv and the session files should have
P_COLS = [
    "participant_id",
    "name",
    "baseline_heart_rate",
    "baseline_skin_response",
    "baseline_temperature"
]


S_COLS = [
    "session_id",
    "participant_id",
    "timestamp",
    "heart_rate",
    "skin_response",
    "temperature",
    "activity_level",
    "signal_quality"
]


def check_id(v, pat, fld):      # v value, pat regrex pattern, fld field
    if not pat.fullmatch(v or ""):
        raise InvalidIdentifierError(
            f"Invalid {fld}: {v!r}."
        )

# Checks if this particular row have all required fields. If a field is missing or empty a InvalidRecordError is raised
def check_req(d, cols):     # d dictionary 
    if None in d:
        raise InvalidRecordError(
            "row",
            "Unexpected number of columns."
        )

    for k in cols:
        if (
            k not in d
            or d[k] is None
            or d[k].strip() == ""
        ):
            raise InvalidRecordError(
                k,
                f"Missing required field: {k}."
            )

# converts text from csv file to numbers, from "22" to 22.0. If it contains text like "stable" an error is raised.  
def num(d, k, tp=float):
    try:
        return tp(d[k])

    except KeyError as e:
        raise InvalidRecordError(
            k,
            f"Missing field: {k}."
        ) from e

    except (TypeError, ValueError) as e:
        raise InvalidRecordError(
            k,
            f"Invalid value for {k}: {d.get(k)!r}."
        ) from e

# Correct range
def rng(v, lo, hi, fld):
    if not lo <= v <= hi:
        raise InvalidRecordError(
            fld,
            f"{fld} must be between {lo} and {hi}."
        )

# Creates a dictionary fro rejected rows
def rejected(src, row, fld, msg):
    return {
        "source": Path(src).name,
        "row": row,
        "field": fld,
        "reason": msg
    }

# Checks if all the correct columns are in the CSV header
def check_header(rd, cols, src):
    if rd.fieldnames != cols:
        raise InvalidRecordError(
            "header",
            f"Unexpected header in {Path(src).name}."
        )

# Reads the file participants.csv and stores the people in ppl{}. If one row is wrong the program shouldn't stop
# but prints out "row 9 rejected, row 10 valid"
def read_people(path):
    path = Path(path)

    ppl = {}
    rej = []

    with path.open(
        "r",
        encoding="utf-8",
        newline=""
    ) as f:

        rd = csv.DictReader(f)

        check_header(
            rd,
            P_COLS,
            path
        )

        for row, d in enumerate(
            rd,
            start=2
        ):

            try:
                check_req(
                    d,
                    P_COLS
                )

                pid = d[
                    "participant_id"
                ].strip()

                check_id(
                    pid,
                    PID_RE,
                    "participant_id"
                )

                hr = num(
                    d,
                    "baseline_heart_rate"
                )

                sk = num(
                    d,
                    "baseline_skin_response"
                )

                tp = num(
                    d,
                    "baseline_temperature"
                )

                rng(
                    hr,
                    35,
                    205,
                    "baseline_heart_rate"
                )

                if sk < 0:
                    raise InvalidRecordError(
                        "baseline_skin_response",
                        "baseline_skin_response cannot be negative."
                    )

                rng(
                    tp,
                    25,
                    42,
                    "baseline_temperature"
                )

                if pid in ppl:
                    raise InvalidRecordError(
                        "participant_id",
                        f"Duplicate participant ID: {pid}."
                    )

                ref = Ref(
                    hr,
                    sk,
                    tp
                )

                p = Person(
                    pid,
                    d["name"].strip(),
                    ref
                )

                ppl[pid] = p

            except InvalidIdentifierError as e:
                rej.append(
                    rejected(
                        path,
                        row,
                        "participant_id",
                        str(e)
                    )
                )

            except InvalidRecordError as e:
                rej.append(
                    rejected(
                        path,
                        row,
                        e.fld,
                        str(e)
                    )
                )

            except ValueError as e:
                rej.append(
                    rejected(
                        path,
                        row,
                        "profile",
                        str(e)
                    )
                )

    return ppl, rej

# Reads the session files and groups all observations with the same session id together
def read_sessions(path, ppl):
    path = Path(path)

    grp = defaultdict(list)     # group 
    own = {}                    # particiant that owns this session
    tot = defaultdict(int)      # Total number of rows for each session

    rej = []
    ok = 0

    with path.open(
        "r",
        encoding="utf-8",
        newline=""
    ) as f:

        rd = csv.DictReader(f)

        check_header(
            rd,
            S_COLS,
            path
        )

        for row, d in enumerate(
            rd,
            start=2
        ):

            try:
                check_req(
                    d,
                    S_COLS
                )

                sid = d[
                    "session_id"
                ].strip()

                pid = d[
                    "participant_id"
                ].strip()

                check_id(
                    sid,
                    SID_RE,
                    "session_id"
                )

                check_id(
                    pid,
                    PID_RE,
                    "participant_id"
                )

                if pid not in ppl:
                    raise InvalidRecordError(
                        "participant_id",
                        f"Unknown participant ID: {pid}."
                    )

                if (
                    sid in own
                    and own[sid] != pid
                ):
                    raise InvalidRecordError(
                        "participant_id",
                        "A session cannot belong to "
                        "multiple participants."
                    )

                own[sid] = pid

                grp[sid]

                tot[sid] += 1

                t = num(
                    d,
                    "timestamp",
                    int
                )

                hr = num(
                    d,
                    "heart_rate"
                )

                sk = num(
                    d,
                    "skin_response"
                )

                tp = num(
                    d,
                    "temperature"
                )

                act = num(
                    d,
                    "activity_level"
                )

                q = num(
                    d,
                    "signal_quality"
                )

                if t < 0:
                    raise InvalidRecordError(
                        "timestamp",
                        "timestamp cannot be negative."
                    )

                rng(
                    hr,
                    35,
                    205,
                    "heart_rate"
                )

                if sk < 0:
                    raise InvalidRecordError(
                        "skin_response",
                        "skin_response cannot be negative."
                    )

                rng(
                    tp,
                    25,
                    42,
                    "temperature"
                )

                rng(
                    act,
                    0,
                    1,
                    "activity_level"
                )

                rng(
                    q,
                    0,
                    1,
                    "signal_quality"
                )

                if q < 0.60:
                    raise InvalidRecordError(
                        "signal_quality",
                        "Poor signal quality. "
                        "The value must be 0.60 or higher."
                    )

                o = Obs(
                    t,
                    hr,
                    sk,
                    tp,
                    act,
                    q
                )

                grp[sid].append(o)

                ok += 1

            except InvalidIdentifierError as e:
                sid = (
                    d.get(
                        "session_id",
                        ""
                    )
                    or ""
                ).strip()

                if not SID_RE.fullmatch(sid):
                    fld = "session_id"

                else:
                    fld = "participant_id"

                rej.append(
                    rejected(
                        path,
                        row,
                        fld,
                        str(e)
                    )
                )

            except InvalidRecordError as e:
                rej.append(
                    rejected(
                        path,
                        row,
                        e.fld,
                        str(e)
                    )
                )

            except KeyError as e:
                rej.append(
                    rejected(
                        path,
                        row,
                        "row",
                        f"Missing CSV field: {e}"
                    )
                )

            except csv.Error as e:
                rej.append(
                    rejected(
                        path,
                        row,
                        "row",
                        f"CSV error: {e}"
                    )
                )

    ses = []

    for sid in sorted(grp):
        p = ppl[
            own[sid]
        ]

        s = Session(
            sid,
            p,
            grp[sid],
            tot[sid]
        )

        ses.append(s)

    return ses, rej, ok


def get_avg(s, k):
    if not s:
        return ""

    return f"{s[k]['avg']:.2f}"

# Creates the output files 
def save_reports(out, res, rej):
    out = Path(out)

    out.mkdir(
        parents=True,
        exist_ok=True
    )

    p1 = out / "analysis_summary.csv"
    p2 = out / "analysis_report.txt"
    p3 = out / "rejected_records.txt"

    with p1.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as f:

        w = csv.writer(f)

        w.writerow([
            "session_id",
            "participant_id",
            "participant_name",
            "classification",
            "usable_observations",
            "total_observations",
            "rejected_observations",
            "avg_heart_rate",
            "avg_skin_response",
            "avg_temperature",
            "avg_activity_level",
            "avg_signal_quality"
        ])

        for r in res:
            s = r["summary"]

            w.writerow([
                r["session_id"],
                r["participant_id"],
                r["participant_name"],
                r["classification"],
                r["usable"],
                r["total"],
                r["rejected"],
                get_avg(
                    s,
                    "heart_rate"
                ),
                get_avg(
                    s,
                    "skin_response"
                ),
                get_avg(
                    s,
                    "temperature"
                ),
                get_avg(
                    s,
                    "activity_level"
                ),
                get_avg(
                    s,
                    "signal_quality"
                )
            ])

    with p2.open(
        "w",
        encoding="utf-8"
    ) as f:

        for r in res:
            f.write(
                f"Session: {r['session_id']}\n"
            )

            f.write(
                f"Participant: "
                f"{r['participant_id']} - "
                f"{r['participant_name']}\n"
            )

            f.write(
                f"Usable observations: "
                f"{r['usable']}/{r['total']}\n"
            )

            f.write(
                f"Rejected observations: "
                f"{r['rejected']}\n"
            )

            f.write(
                f"Classification: "
                f"{r['classification']}\n"
            )

            f.write(
                f"Explanation: "
                f"{r['explanation']}\n"
            )

            f.write(
                "-" * 60 + "\n"
            )

    with p3.open(
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "Source | Row | Field | Reason\n"
        )

        f.write(
            "-" * 70 + "\n"
        )

        if not rej:
            f.write(
                "No rejected records.\n"
            )

        else:
            for r in rej:
                f.write(
                    f"{r['source']} | "
                    f"{r['row']} | "
                    f"{r['field']} | "
                    f"{r['reason']}\n"
                )

    return [
        p1,
        p2,
        p3
    ]