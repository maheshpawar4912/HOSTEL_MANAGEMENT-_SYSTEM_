import os
import re


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def pause(message="Press Enter to continue..."):
    input(message)


def read_nonempty(prompt, default=None):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        if default is not None:
            return default
        print("Value cannot be empty. Please try again.")


def read_choice(prompt, choices):
    choice = input(prompt).strip().lower()
    return choice if choice in choices else None


def read_amount(prompt, default=0.0):
    while True:
        value = input(prompt).strip()
        if value == "" and default is not None:
            return default
        try:
            amount = float(value)
            if amount < 0:
                print("Amount cannot be negative.")
                continue
            return amount
        except ValueError:
            print("Please enter a valid number.")


def read_int(prompt, default=None, minimum=None, maximum=None):
    while True:
        value = input(prompt).strip()
        if value == "" and default is not None:
            return default
        if not re.match(r"^-?\d+$", value):
            print("Please enter a whole number.")
            continue
        number = int(value)
        if minimum is not None and number < minimum:
            print(f"Value must be at least {minimum}.")
            continue
        if maximum is not None and number > maximum:
            print(f"Value cannot exceed {maximum}.")
            continue
        return number


def format_money(amount):
    return f"{amount:.2f}"
