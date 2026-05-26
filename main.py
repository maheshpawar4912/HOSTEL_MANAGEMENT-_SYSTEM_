from datetime import date, datetime
from data_manager import (
    DEFAULT_DATA,
    export_complaints,
    export_rooms,
    export_students,
    export_visitors,
    get_next_id,
    load_data,
    save_data,
)
from utils import clear_screen, format_money, pause, read_amount, read_int, read_nonempty, read_choice


def add_student(data):
    print("\n=== Add Student ===")
    roll = read_nonempty("Roll number: ")
    if roll in data["students"]:
        print("A student with that roll number already exists.")
        return
    student = {
        "name": read_nonempty("Full name: "),
        "contact": read_nonempty("Contact number: "),
        "email": read_nonempty("Email address: "),
        "course": read_nonempty("Course / Department: "),
        "room": None,
        "fees_paid": 0.0,
        "fees_due": read_amount("Starting fees due (0 if none): ", default=0.0),
        "joined_on": date.today().isoformat(),
    }
    data["students"][roll] = student
    save_data(data)
    print("Student added successfully.")


def update_student(data):
    print("\n=== Update Student ===")
    roll = read_nonempty("Roll number: ")
    student = data["students"].get(roll)
    if not student:
        print("Student not found.")
        return
    student["name"] = input(f"Name [{student['name']}]: ").strip() or student["name"]
    student["contact"] = input(f"Contact [{student['contact']}]: ").strip() or student["contact"]
    student["email"] = input(f"Email [{student['email']}]: ").strip() or student["email"]
    student["course"] = input(f"Course [{student['course']}]: ").strip() or student["course"]
    save_data(data)
    print("Student profile updated.")


def delete_student(data):
    print("\n=== Delete Student ===")
    roll = read_nonempty("Roll number: ")
    student = data["students"].pop(roll, None)
    if not student:
        print("Student not found.")
        return
    if student["room"]:
        room = data["rooms"].get(student["room"])
        if room:
            room["occupant"] = None
    save_data(data)
    print("Student removed and room released if assigned.")


def view_student(data):
    print("\n=== View Student ===")
    roll = read_nonempty("Roll number: ")
    student = data["students"].get(roll)
    if not student:
        print("Student not found.")
        return
    print(f"Name: {student['name']}")
    print(f"Contact: {student['contact']}")
    print(f"Email: {student['email']}")
    print(f"Course: {student['course']}")
    print(f"Room: {student['room'] or 'Not assigned'}")
    print(f"Fees Paid: {format_money(student['fees_paid'])}")
    print(f"Fees Due: {format_money(student['fees_due'])}")
    print(f"Joined On: {student['joined_on']}")


def list_students(data):
    print("\n=== Student List ===")
    if not data["students"]:
        print("No students registered.")
        return
    print(f"Total students: {len(data['students'])}")
    for roll, student in sorted(data["students"].items()):
        room = student["room"] or "None"
        status = "Due" if student["fees_due"] > 0 else "Paid"
        print(f"{roll}: {student['name']} | Room: {room} | Fees Due: {format_money(student['fees_due'])} | {status}")


def search_students(data):
    print("\n=== Search Students ===")
    query = read_nonempty("Enter name, roll or room: ").lower()
    results = []
    for roll, student in data["students"].items():
        if (query in roll.lower() or
                query in student["name"].lower() or
                (student["room"] and query in student["room"].lower())):
            results.append((roll, student))
    if not results:
        print("No matching students found.")
        return
    for roll, student in results:
        print(f"{roll}: {student['name']} | Room: {student['room'] or 'None'} | Due: {format_money(student['fees_due'])}")


def add_room(data):
    print("\n=== Add Room ===")
    room_number = read_nonempty("Room number: ")
    if room_number in data["rooms"]:
        print("Room already exists.")
        return
    capacity = read_int("Capacity (1-4): ", default=1, minimum=1, maximum=4)
    room_type = read_nonempty("Room type (Single/Double/Mixed): ")
    data["rooms"][room_number] = {
        "capacity": capacity,
        "occupant": None,
        "room_type": room_type.title(),
    }
    save_data(data)
    print("Room added successfully.")


def update_room(data):
    print("\n=== Update Room ===")
    room_number = read_nonempty("Room number: ")
    room = data["rooms"].get(room_number)
    if not room:
        print("Room not found.")
        return
    room["capacity"] = read_int(f"Capacity [{room['capacity']}]: ", default=room["capacity"], minimum=1, maximum=10)
    room_type = input(f"Type [{room['room_type']}]: ").strip()
    if room_type:
        room["room_type"] = room_type.title()
    save_data(data)
    print("Room updated successfully.")


def delete_room(data):
    print("\n=== Delete Room ===")
    room_number = read_nonempty("Room number: ")
    room = data["rooms"].get(room_number)
    if not room:
        print("Room not found.")
        return
    if room["occupant"]:
        print("Cannot delete a room that still has an occupant.")
        return
    data["rooms"].pop(room_number)
    save_data(data)
    print("Room deleted successfully.")


def list_rooms(data):
    print("\n=== Room List ===")
    if not data["rooms"]:
        print("No rooms available.")
        return
    for room_number, room in sorted(data["rooms"].items()):
        occupant = room["occupant"] or "Available"
        print(f"{room_number}: {room['room_type']} | Capacity: {room['capacity']} | Occupant: {occupant}")


def assign_room(data):
    print("\n=== Assign Room ===")
    roll = read_nonempty("Student roll number: ")
    student = data["students"].get(roll)
    if not student:
        print("Student not found.")
        return
    if student["room"]:
        print(f"Student already assigned to room {student['room']}.")
        return
    room_number = read_nonempty("Room number: ")
    room = data["rooms"].get(room_number)
    if not room:
        print("Room not found.")
        return
    if room["occupant"]:
        print("Room is already occupied.")
        return
    room["occupant"] = roll
    student["room"] = room_number
    save_data(data)
    print("Room assigned successfully.")


def release_room(data):
    print("\n=== Release Room ===")
    room_number = read_nonempty("Room number: ")
    room = data["rooms"].get(room_number)
    if not room:
        print("Room not found.")
        return
    if not room["occupant"]:
        print("Room is already available.")
        return
    student_roll = room["occupant"]
    room["occupant"] = None
    if student_roll in data["students"]:
        data["students"][student_roll]["room"] = None
    save_data(data)
    print("Room released successfully.")


def set_monthly_fee(data):
    print("\n=== Set Monthly Fee ===")
    amount = read_amount("Monthly fee amount: ")
    data["settings"]["monthly_fee"] = amount
    save_data(data)
    print("Monthly fee recorded.")


def pay_fee(data):
    print("\n=== Record Fee Payment ===")
    roll = read_nonempty("Student roll number: ")
    student = data["students"].get(roll)
    if not student:
        print("Student not found.")
        return
    amount = read_amount("Payment amount: ")
    student["fees_paid"] += amount
    student["fees_due"] = max(0.0, student["fees_due"] - amount)
    payment_id = get_next_id(data, "next_payment_id") if "next_payment_id" in data["settings"] else None
    if payment_id:
        data["payments"][payment_id] = {
            "student_roll": roll,
            "amount": amount,
            "date": datetime.now().isoformat(),
        }
    save_data(data)
    print("Payment recorded.")


def update_fees_due(data):
    print("\n=== Update Fees Due ===")
    roll = read_nonempty("Student roll number: ")
    student = data["students"].get(roll)
    if not student:
        print("Student not found.")
        return
    student["fees_due"] = read_amount("New due amount: ")
    save_data(data)
    print("Fees due updated.")


def add_attendance(data):
    print("\n=== Record Attendance ===")
    attendance_date = input("Date (YYYY-MM-DD) [today]: ").strip() or date.today().isoformat()
    try:
        date.fromisoformat(attendance_date)
    except ValueError:
        print("Invalid date format.")
        return
    roll = read_nonempty("Student roll number: ")
    if roll not in data["students"]:
        print("Student not found.")
        return
    status = read_choice("Status present/absent: ", {"present", "absent"})
    if not status:
        print("Invalid status.")
        return
    data["attendance"].setdefault(attendance_date, {})[roll] = status.title()
    save_data(data)
    print("Attendance recorded.")


def view_attendance(data):
    print("\n=== Attendance Records ===")
    attendance_date = input("Date (YYYY-MM-DD) [today]: ").strip() or date.today().isoformat()
    if attendance_date not in data["attendance"]:
        print("No attendance entries for that date.")
        return
    records = data["attendance"][attendance_date]
    for roll, status in records.items():
        student = data["students"].get(roll, {})
        print(f"{roll}: {student.get('name', 'Unknown')} | {status}")


def add_visitor(data):
    print("\n=== Register Visitor ===")
    visitor_id = get_next_id(data, "next_visitor_id")
    visitor = {
        "name": read_nonempty("Visitor name: "),
        "student_roll": read_nonempty("Visiting student roll: "),
        "in_time": datetime.now().isoformat(sep=" ", timespec="minutes"),
        "out_time": None,
    }
    if visitor["student_roll"] not in data["students"]:
        print("Student not found.")
        return
    data["visitors"][visitor_id] = visitor
    save_data(data)
    print(f"Visitor registered with ID {visitor_id}.")


def checkout_visitor(data):
    print("\n=== Visitor Checkout ===")
    visitor_id = read_nonempty("Visitor ID: ")
    visitor = data["visitors"].get(visitor_id)
    if not visitor:
        print("Visitor not found.")
        return
    if visitor["out_time"]:
        print("Visitor already checked out.")
        return
    visitor["out_time"] = datetime.now().isoformat(sep=" ", timespec="minutes")
    save_data(data)
    print("Visitor checked out.")


def list_visitors(data):
    print("\n=== Visitor Log ===")
    if not data["visitors"]:
        print("No visitor entries.")
        return
    for visitor_id, visitor in data["visitors"].items():
        print(f"{visitor_id}: {visitor['name']} | Student: {visitor['student_roll']} | In: {visitor['in_time']} | Out: {visitor['out_time'] or 'Still present'}")


def add_complaint(data):
    print("\n=== Lodge Complaint ===")
    complaint_id = get_next_id(data, "next_complaint_id")
    student_roll = read_nonempty("Student roll number: ")
    if student_roll and student_roll not in data["students"]:
        print("Student not found.")
        return
    complaint = {
        "student_roll": student_roll,
        "subject": read_nonempty("Complaint subject: "),
        "message": read_nonempty("Complaint description: "),
        "status": "Open",
        "date": date.today().isoformat(),
    }
    data["complaints"][complaint_id] = complaint
    save_data(data)
    print(f"Complaint lodged with ID {complaint_id}.")


def view_complaints(data):
    print("\n=== Complaints ===")
    if not data["complaints"]:
        print("No complaints recorded.")
        return
    for complaint_id, complaint in data["complaints"].items():
        print(f"{complaint_id}: {complaint['subject']} | Student: {complaint['student_roll'] or 'N/A'} | Status: {complaint['status']}")
        print(f"   {complaint['message']}")
        print(f"   Date: {complaint['date']}")


def update_complaint(data):
    print("\n=== Update Complaint Status ===")
    complaint_id = read_nonempty("Complaint ID: ")
    complaint = data["complaints"].get(complaint_id)
    if not complaint:
        print("Complaint not found.")
        return
    status = read_choice("New status (open/in progress/closed): ", {"open", "in progress", "closed"})
    if not status:
        print("Invalid status.")
        return
    complaint["status"] = status.title()
    save_data(data)
    print("Complaint status updated.")


def show_reports(data):
    print("\n=== Reports ===")
    total_students = len(data["students"])
    occupied_rooms = sum(1 for room in data["rooms"].values() if room["occupant"])
    total_rooms = len(data["rooms"])
    total_due = sum(student["fees_due"] for student in data["students"].values())
    total_paid = sum(student["fees_paid"] for student in data["students"].values())
    open_complaints = sum(1 for c in data["complaints"].values() if c["status"] == "Open")
    print(f"Total students: {total_students}")
    print(f"Total rooms: {total_rooms}")
    print(f"Occupied rooms: {occupied_rooms}")
    print(f"Total fees paid: {format_money(total_paid)}")
    print(f"Total fees due: {format_money(total_due)}")
    print(f"Open complaints: {open_complaints}")


def export_data_menu(data):
    print("\n=== Export Data ===")
    print("1. Export students to CSV")
    print("2. Export rooms to CSV")
    print("3. Export complaints to CSV")
    print("4. Export visitors to CSV")
    print("5. Back")
    choice = input("Choice: ").strip()
    if choice == "1":
        export_students(data, "students_export.csv")
        print("Students exported to students_export.csv")
    elif choice == "2":
        export_rooms(data, "rooms_export.csv")
        print("Rooms exported to rooms_export.csv")
    elif choice == "3":
        export_complaints(data, "complaints_export.csv")
        print("Complaints exported to complaints_export.csv")
    elif choice == "4":
        export_visitors(data, "visitors_export.csv")
        print("Visitors exported to visitors_export.csv")
    else:
        return


def main():
    data = load_data()
    while True:
        clear_screen()
        print("===== Hostel Management System =====")
        print("1. Student management")
        print("2. Room management")
        print("3. Fee management")
        print("4. Attendance")
        print("5. Visitor management")
        print("6. Complaint management")
        print("7. Reports")
        print("8. Export data")
        print("9. Settings")
        print("0. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            clear_screen()
            print("--- Student Management ---")
            print("1. Add student")
            print("2. Update student")
            print("3. Delete student")
            print("4. View student")
            print("5. List students")
            print("6. Search students")
            print("0. Back")
            sub = input("Choice: ").strip()
            if sub == "1":
                add_student(data)
            elif sub == "2":
                update_student(data)
            elif sub == "3":
                delete_student(data)
            elif sub == "4":
                view_student(data)
            elif sub == "5":
                list_students(data)
            elif sub == "6":
                search_students(data)
        elif choice == "2":
            clear_screen()
            print("--- Room Management ---")
            print("1. Add room")
            print("2. Update room")
            print("3. Delete room")
            print("4. List rooms")
            print("5. Assign room")
            print("6. Release room")
            print("0. Back")
            sub = input("Choice: ").strip()
            if sub == "1":
                add_room(data)
            elif sub == "2":
                update_room(data)
            elif sub == "3":
                delete_room(data)
            elif sub == "4":
                list_rooms(data)
            elif sub == "5":
                assign_room(data)
            elif sub == "6":
                release_room(data)
        elif choice == "3":
            clear_screen()
            print("--- Fee Management ---")
            print("1. Set monthly fee")
            print("2. Record payment")
            print("3. Update fees due")
            print("0. Back")
            sub = input("Choice: ").strip()
            if sub == "1":
                set_monthly_fee(data)
            elif sub == "2":
                pay_fee(data)
            elif sub == "3":
                update_fees_due(data)
        elif choice == "4":
            clear_screen()
            print("--- Attendance ---")
            print("1. Record attendance")
            print("2. View attendance")
            print("0. Back")
            sub = input("Choice: ").strip()
            if sub == "1":
                add_attendance(data)
            elif sub == "2":
                view_attendance(data)
        elif choice == "5":
            clear_screen()
            print("--- Visitor Management ---")
            print("1. Register visitor")
            print("2. Check out visitor")
            print("3. List visitors")
            print("0. Back")
            sub = input("Choice: ").strip()
            if sub == "1":
                add_visitor(data)
            elif sub == "2":
                checkout_visitor(data)
            elif sub == "3":
                list_visitors(data)
        elif choice == "6":
            clear_screen()
            print("--- Complaint Management ---")
            print("1. Lodge complaint")
            print("2. View complaints")
            print("3. Update complaint status")
            print("0. Back")
            sub = input("Choice: ").strip()
            if sub == "1":
                add_complaint(data)
            elif sub == "2":
                view_complaints(data)
            elif sub == "3":
                update_complaint(data)
        elif choice == "7":
            show_reports(data)
        elif choice == "8":
            export_data_menu(data)
        elif choice == "9":
            clear_screen()
            print("--- Settings ---")
            print("1. Show monthly fee")
            print("0. Back")
            sub = input("Choice: ").strip()
            if sub == "1":
                print(f"Monthly fee: {format_money(data['settings'].get('monthly_fee', 0.0))}")
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid selection.")
        pause()


if __name__ == "__main__":
    main()
