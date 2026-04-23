import pandas as pd
import numpy as np
from typing import Optional
from faker import Faker
import random

fake = Faker()


EVENT_CHOICES = ["Spring Gala", "Summer Camp", "Fall Fundraiser", "None"]
MESSINESS_PROFILES = {
    "low": {
        "duplicate_rate": 0.03,
        "email_error_rate": 0.02,
        "name_mess_rate": 0.05,
        "date_mess_rate": 0.10,
        "missing_rate": 0.02,
    },
    "medium": {
        "duplicate_rate": 0.10,
        "email_error_rate": 0.05,
        "name_mess_rate": 0.15,
        "date_mess_rate": 0.25,
        "missing_rate": 0.05,
    },
    "high": {
        "duplicate_rate": 0.20,
        "email_error_rate": 0.15,
        "name_mess_rate": 0.30,
        "date_mess_rate": 0.40,
        "missing_rate": 0.15,
    },
}


def _validate_inputs(num_records: int, messiness_level: str) -> None:
    if not isinstance(num_records, int) or num_records <= 0:
        raise ValueError(f"num_records must be a positive integer, got {num_records}")
    if messiness_level not in MESSINESS_PROFILES:
        raise ValueError(f"messiness_level must be 'low', 'medium', or 'high', got '{messiness_level}'")


def _build_record() -> dict:
    event_registered = np.random.choice(EVENT_CHOICES, p=[0.25, 0.25, 0.25, 0.25])
    reg_date = fake.date_between(start_date="-6m", end_date="today") if event_registered != "None" and random.random() > 0.4 else None
    return {
        "ID": fake.uuid4(),
        "Name": fake.name(),
        "Email": fake.email(),
        "Join_Date": fake.date_between(start_date="-2y", end_date="today"),
        "Last_Login": fake.date_time_between(start_date="-1y", end_date="now"),
        "Event_Attendance": np.random.randint(0, 20),
        "Role": np.random.choice(["Member", "Admin", "Guest"], p=[0.8, 0.05, 0.15]),
        "Event_Registered": event_registered,
        "Registration_Date": reg_date,
    }


def _add_duplicates(df: pd.DataFrame, duplicate_rate: float) -> pd.DataFrame:
    num_duplicates = int(len(df.index) * duplicate_rate)
    if num_duplicates == 0:
        return df
    duplicates = df.sample(num_duplicates, replace=True)
    return pd.concat([df, duplicates], ignore_index=True)


def _mess_up_name(name: str, name_mess_rate: float) -> str:
    if random.random() < name_mess_rate:
        return name.upper() if random.random() < 0.5 else name.lower()
    return name


def _mess_up_email(email: str, email_error_rate: float) -> str:
    if random.random() < email_error_rate:
        return email.replace("@", " at ")
    return email


def _mess_up_date(date_value, date_mess_rate: float):
    roll = random.random()
    if roll < date_mess_rate * 0.4:
        return date_value.strftime("%m/%d/%Y")
    if roll < date_mess_rate * 0.8:
        return date_value.strftime("%d-%m-%Y")
    if roll < date_mess_rate:
        return "Unknown"
    return date_value


def _apply_missing_values(df: pd.DataFrame, missing_rate: float) -> pd.DataFrame:
    for col in ["Event_Attendance", "Last_Login"]:
        df.loc[df.sample(frac=missing_rate).index, col] = np.nan
    return df


def _apply_messiness(df: pd.DataFrame, profile: dict) -> pd.DataFrame:
    df = _add_duplicates(df, profile["duplicate_rate"])
    df["Name"] = df["Name"].apply(lambda name: _mess_up_name(name, profile["name_mess_rate"]))
    df["Email"] = df["Email"].apply(lambda email: _mess_up_email(email, profile["email_error_rate"]))
    df["Join_Date"] = df["Join_Date"].apply(lambda date_value: _mess_up_date(date_value, profile["date_mess_rate"]))
    df = _apply_missing_values(df, profile["missing_rate"])

    return df.sample(frac=1).reset_index(drop=True)


def generate_messy_data(
    num_records: int = 500, save_path: Optional[str] = None, messiness_level: str = "medium"
) -> pd.DataFrame:
    """Generates a dataset with intentional messiness for cleaning demonstration."""
    _validate_inputs(num_records, messiness_level)
    profile = MESSINESS_PROFILES[messiness_level]
    df = pd.DataFrame([_build_record() for _ in range(num_records)])
    df = _apply_messiness(df, profile)

    if save_path:
        df.to_csv(save_path, index=False)
        print(f"Generated messy data at {save_path} with {len(df)} rows.")

    return df


if __name__ == "__main__":
    import os

    if not os.path.exists("../data"):
        os.makedirs("../data", exist_ok=True)

    generate_messy_data(save_path="../data/messy_club_data.csv")
