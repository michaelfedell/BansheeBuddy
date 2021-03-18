import requests
import json
from enum import Enum
import os
from dataclasses import dataclass
import smtplib
from pathlib import Path

api_key = os.enivron["BUNGIE_API_KEY"]
api = "https://www.bungie.net/platform/Destiny2"
HEADERS = {"X-API-Key": api_key}

COLLECTIBLES = "800"
NOT_AQCUIRED = 0b0000001

MEMBER_LIST_FILE = Path(__file__).absolute() / "member_list.csv"
assert MEMBER_LIST_FILE.exists()

SENDER = os.getenv("EMAIL_SENDER")
EMAIL = """From: Banshee Buddy <{sender}>
To: {name} <{email}>
Subject: Banshee Buddy - Daily Mod Check

Howdy {name}, today's wares include:
{message}
"""
LIVE = bool(os.getenv("EMAIL_LIVE"))

@dataclass
class Member:
    membership_id: int
    email: str
    name: str


members = [
    Member(mem_id, email, name)
    for mem_id, email, name in line.strip().split(",")
    for line in MEMBER_LIST_FILE.open().read()
]


class MembershipType(Enum):
    XBOX = 1
    PSN = 2
    STEAM = 3
    BLIZZARD = 4


def check_manifest(entity_type, hash_id):
    r = requests.get(
        f"{api}/Manifest/{entity_type}/{hash_id}",
        headers=HEADERS
    )
    return r.json()


def get_player(membership_type: MembershipType, display_name: str):
    r = requests.get(
        f"{api}/SearchDestinyPlayer/{membership_type.value}/{display_name}",
        headers=HEADERS
    )
    return r.json()


def get_item(membership_id: int, item_hash):
    r = requests.get(
        f"{api}/2/Profile/{membership_id}/Item/{item_hash}?components=",
        headers=HEADERS
    )
    return r.json()


def get_profile(membership_id, components):
    r = requests.get(
        f"{api}/2/Profile/{membership_id}?components={components}",
        headers=HEADERS
    )
    return r.json()


def get_mods():
    r = requests.get(
        "https://api.banshee44mods.com/info"
    )
    return r.json()["inventory"]["mods"]


if __name__ == '__main__':
    mods = get_mods()
    for member in members:
        print(member.name)
        profile_inventory = get_profile(member.membership_id, COLLECTIBLES)
        collectilbes = profile_inventory["Response"]["profileCollectibles"]["data"]["collectibles"]
        msgs = []
        for mod in mods:
            item = check_manifest("DestinyInventoryItemDefinition", mod["itemHash"])["Response"]
            #print(item)
            collectible_hash = str(item["collectibleHash"])
            #print(collectible_hash)
            status = "NOT AQUIRED" if collectilbes[collectible_hash]["state"] & NOT_AQCUIRED else "AQUIRED"
            msg = f"{mod['name']} ({mod['timesSoldInLastYear'] / 365 :.2%}): {status}"
            print(msg)
            msgs.append(msg)
        if LIVE:
            try:
                smtpObj = smtplib.SMTP("localhost")
                mail = EMAIL.format(name=member.name, email=member.email, message="\n".join(msgs), sender=SENDER)
                smtpObj.sendmail(SENDER, member.email, mail)
            except smtplib.SMTPException as e:
                print("ERROR: Unable to send email", e)
