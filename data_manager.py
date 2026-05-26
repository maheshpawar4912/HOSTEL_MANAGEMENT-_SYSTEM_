import csv
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(BASE_DIR, "hostel_data.json")

DEFAULT_DATA = {
    "students": {},
    "rooms": {},
    "complaints": {},
    "visitors": {},
    "attendance": {},
    "payments": {},
    "settings": {
        "next_complaint_id": 1,
        "next_visitor_id": 1,
        "next_payment_id": 1,
        "monthly_fee": 0.0
    }
}


def load_data():
    if not os.path.exists(DATA_FILE):
        return DEFAULT_DATA.copy()
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except (json.JSONDecodeError, ValueError):
            data = DEFAULT_DATA.copy()
    for key, default_value in DEFAULT_DATA.items():
        if key not in data:
            data[key] = default_value.copy() if isinstance(default_value, dict) else default_value
    return data


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def get_next_id(data, key):
    next_id = data["settings"].get(key, 1)
    data["settings"][key] = next_id + 1
    return str(next_id)


def export_to_csv(filename, rows, headers):
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def export_students(data, filename):
    rows = []
    for roll, student in data["students"].items():
        rows.append({
            "roll_number": roll,
            "name": student["name"],
            "contact": student["contact"],
            "email": student["email"],
            "course": student["course"],
            "room": student["room"] or "None",
            "fees_paid": student["fees_paid"],
            "fees_due": student["fees_due"]
        })
    export_to_csv(filename, rows, ["roll_number", "name", "contact", "email", "course", "room", "fees_paid", "fees_due"])


def export_rooms(data, filename):
    rows = []
    for room, info in data["rooms"].items():
        rows.append({
            "room_number": room,
            "capacity": info["capacity"],
            "occupant": info["occupant"] or "Available",
            "room_type": info["room_type"]
        })
    export_to_csv(filename, rows, ["room_number", "capacity", "occupant", "room_type"])


def export_complaints(data, filename):
    rows = []
    for complaint_id, complaint in data["complaints"].items():
        rows.append({
            "id": complaint_id,
            "student_roll": complaint["student_roll"],
            "subject": complaint["subject"],
            "message": complaint["message"],
            "status": complaint["status"],
            "date": complaint["date"]
        })
    export_to_csv(filename, rows, ["id", "student_roll", "subject", "message", "status", "date"])


def export_visitors(data, filename):
    rows = []
    for visitor_id, visitor in data["visitors"].items():
        rows.append({
            "id": visitor_id,
            "name": visitor["name"],
            "student_roll": visitor["student_roll"],
            "in_time": visitor["in_time"],
            "out_time": visitor["out_time"] or "Still in hostel"
        })
    export_to_csv(filename, rows, ["id", "name", "student_roll", "in_time", "out_time"])
