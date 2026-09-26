"""
parse_xml.py

Parses modified_sms_v2.xml (an Android SMS backup export) and converts
each <sms> record into a structured transaction dictionary.

The raw XML only gives us generic SMS metadata (date, address, etc.) --
the actual transaction details (type, amount, sender/receiver, fee,
balance, transaction reference) are embedded as free text inside the
`body` attribute, in several different message formats depending on
what kind of MoMo event triggered the SMS. This module identifies which
format each message is, and extracts fields out of it with regex.
"""
import re
import json
import xml.etree.ElementTree as ET
from datetime import datetime


def _to_number(raw):
    """Convert a string like '1,000' or '1000' to an int. Returns None
    if raw is falsy/unparseable."""
    if not raw:
        return None
    try:
        return int(raw.replace(",", "").strip())
    except ValueError:
        return None


def _epoch_ms_to_iso(epoch_ms):
    """Convert a millisecond epoch timestamp string to an ISO datetime string."""
    try:
        return datetime.fromtimestamp(int(epoch_ms) / 1000).isoformat()
    except (ValueError, TypeError):
        return None


# Each entry: (type_name, compiled regex to detect it, function to extract fields from a match)
# All extractor functions take the raw body string and return a dict of fields.

def _extract_received_money(body):
    m = re.search(
        r"You have received (?P<amount>[\d,]+) RWF from (?P<sender>.+?) \("
        r".*?\).*?Financial Transaction Id:\s*(?P<ref>\d+)",
        body,
    )
    if not m:
        return {}
    return {
        "amount": _to_number(m.group("amount")),
        "sender": m.group("sender").strip(),
        "receiver": "me",
        "transaction_ref": m.group("ref"),
    }


def _extract_payment_txid(body):
    m = re.search(
        r"TxId:\s*(?P<ref>\d+)\.\s*Your payment of (?P<amount>[\d,]+) RWF to "
        r"(?P<receiver>.+?)\s+\d+ has been completed.*?"
        r"Your new balance:\s*(?P<balance>[\d,]+) RWF\.\s*Fee was (?P<fee>[\d,]+) RWF",
        body,
    )
    if not m:
        return {}
    return {
        "amount": _to_number(m.group("amount")),
        "sender": "me",
        "receiver": m.group("receiver").strip(),
        "balance": _to_number(m.group("balance")),
        "fee": _to_number(m.group("fee")),
        "transaction_ref": m.group("ref"),
    }


def _extract_bank_deposit(body):
    m = re.search(
        r"A bank deposit of (?P<amount>[\d,]+) RWF has been added.*?"
        r"NEW BALANCE\s*:(?P<balance>[\d,]+) RWF",
        body,
    )
    if not m:
        return {}
    return {
        "amount": _to_number(m.group("amount")),
        "sender": "bank",
        "receiver": "me",
        "balance": _to_number(m.group("balance")),
    }


def _extract_transfer_165(body):
    m = re.search(
        r"(?P<amount>[\d,]+) RWF transferred to (?P<receiver>.+?) \("
        r"(?P<phone>\d+)\) from.*?Fee was:\s*(?P<fee>[\d,]+) RWF\.\s*"
        r"New balance:\s*(?P<balance>[\d,]+) RWF",
        body,
    )
    if not m:
        return {}
    return {
        "amount": _to_number(m.group("amount")),
        "sender": "me",
        "receiver": m.group("receiver").strip(),
        "phone": m.group("phone"),
        "fee": _to_number(m.group("fee")),
        "balance": _to_number(m.group("balance")),
    }


def _extract_airtime_162(body):
    m = re.search(
        r"TxId:(?P<ref>\d+)\*S\*Your payment of (?P<amount>[\d,]+) RWF to "
        r"Airtime.*?Fee was (?P<fee>[\d,]+) RWF\.\s*Your new balance:\s*(?P<balance>[\d,]+) RWF",
        body,
    )
    if not m:
        return {}
    return {
        "amount": _to_number(m.group("amount")),
        "sender": "me",
        "receiver": "Airtime",
        "fee": _to_number(m.group("fee")),
        "balance": _to_number(m.group("balance")),
        "transaction_ref": m.group("ref"),
    }


def _extract_third_party_164(body):
    m = re.search(
        r"A transaction of (?P<amount>[\d,]+) RWF by (?P<sender>.+?) on your MOMO "
        r"account was successfully completed.*?"
        r"Financial Transaction Id:\s*(?P<ref>\d+)",
        body,
    )
    if not m:
        return {}
    return {
        "amount": _to_number(m.group("amount")),
        "sender": m.group("sender").strip(),
        "receiver": "me",
        "transaction_ref": m.group("ref"),
    }


def _extract_withdrawal(body):
    m = re.search(
        r"withdrawn (?P<amount>[\d,]+) RWF from your mobile money account",
        body,
    )
    if not m:
        return {}
    return {
        "amount": _to_number(m.group("amount")),
        "sender": "me",
        "receiver": "agent",
    }


def _extract_bundle_purchase(body):
    m = re.search(r"igura (?P<amount>[\d,]+) RWF", body)
    if not m:
        return {}
    return {
        "amount": _to_number(m.group("amount")),
        "sender": "me",
        "receiver": "bundle_purchase",
    }


def _extract_reversal(body):
    m = re.search(
        r"transaction to (?P<receiver>.+?) \((?P<phone>\d+)\) with (?P<amount>[\d,]+) RWF",
        body,
    )
    if not m:
        return {}
    return {
        "amount": _to_number(m.group("amount")),
        "sender": "me",
        "receiver": m.group("receiver").strip(),
        "phone": m.group("phone"),
    }


# Order matters: more specific patterns should be checked before more general ones.
CLASSIFIERS = [
    ("received_money", re.compile(r"You have received", re.I), _extract_received_money),
    ("payment", re.compile(r"^TxId:\s*\d+\.\s*Your payment", re.I), _extract_payment_txid),
    ("bank_deposit", re.compile(r"\*113\*R\*A bank deposit", re.I), _extract_bank_deposit),
    ("transfer", re.compile(r"\*165\*S\*", re.I), _extract_transfer_165),
    ("airtime", re.compile(r"\*162\*TxId", re.I), _extract_airtime_162),
    ("third_party_payment", re.compile(r"\*164\*S\*", re.I), _extract_third_party_164),
    ("withdrawal", re.compile(r"have via agent", re.I), _extract_withdrawal),
    ("otp", re.compile(r"one-time password", re.I), lambda b: {}),
    ("bundle_purchase", re.compile(r"Yello!Umaze kugura", re.I), _extract_bundle_purchase),
    ("reversal", re.compile(r"A reversal has been initiated", re.I), _extract_reversal),
]


def classify_and_extract(body):
    """Return (type_name, extracted_fields_dict) for a single SMS body."""
    for type_name, pattern, extractor in CLASSIFIERS:
        if pattern.search(body):
            return type_name, extractor(body)
    return "other", {}


def parse_sms_xml(xml_path):
    """Parse the SMS backup XML file and return a list of transaction dicts."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    transactions = []
    for idx, sms in enumerate(root.findall("sms"), start=1):
        body = sms.get("body", "") or ""
        type_name, fields = classify_and_extract(body)

        transaction = {
            "id": idx,
            "type": type_name,
            "amount": fields.get("amount"),
            "fee": fields.get("fee"),
            "balance": fields.get("balance"),
            "sender": fields.get("sender"),
            "receiver": fields.get("receiver"),
            "phone": fields.get("phone"),
            "transaction_ref": fields.get("transaction_ref"),
            "timestamp": sms.get("readable_date") or _epoch_ms_to_iso(sms.get("date")),
            "raw_body": body,
        }
        transactions.append(transaction)

    return transactions


if __name__ == "__main__":
    import sys

    xml_path = sys.argv[1] if len(sys.argv) > 1 else "modified_sms_v2.xml"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "transactions.json"

    transactions = parse_sms_xml(xml_path)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(transactions, f, indent=2, ensure_ascii=False)

    # Quick summary so you can sanity-check the parse from the command line
    from collections import Counter
    type_counts = Counter(t["type"] for t in transactions)
    print(f"Parsed {len(transactions)} SMS records -> {out_path}")
    for type_name, count in type_counts.most_common():
        print(f"  {type_name:20s} {count}")
