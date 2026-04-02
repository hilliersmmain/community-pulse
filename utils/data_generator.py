import pandas as pd
import numpy as np
from typing import Optional
from faker import Faker
import random

fake = Faker()


EVENT_CHOICES = ["Spring Gala", "Summer Camp", "Fall Fundraiser", "None"]


def generate_messy_data(
    num_records: int = 500, save_path: Optional[str] = None, messiness_level: str = "medium"
) -> pd.DataFrame:
    """Generates a dataset with intentional messiness for cleaning demonstration."""
    if not isinstance(num_records, int) or num_records <= 0:
        raise ValueError(f"num_records must be a positive integer, got {num_records}")
    if messiness_level not in ("low", "medium", "high"):
        raise ValueError(f"messiness_level must be 'low', 'medium', or 'high', got '{messiness_level}'")

    if messiness_level == "low":
        duplicate_rate = 0.03  # 3% duplicates
        email_error_rate = 0.02  # 2% invalid emails
        name_mess_rate = 0.05  # 5% messy names
        date_mess_rate = 0.10  # 10% messy dates
        missing_rate = 0.02  # 2% missing values
    elif messiness_level == "high":
        duplicate_rate = 0.20  # 20% duplicates
        email_error_rate = 0.15  # 15% invalid emails
        name_mess_rate = 0.30  # 30% messy names
        date_mess_rate = 0.40  # 40% messy dates
        missing_rate = 0.15  # 15% missing values
    else:  # medium (default)
        duplicate_rate = 0.10  # 10% duplicates
        email_error_rate = 0.05  # 5% invalid emails
        name_mess_rate = 0.15  # 15% messy names
        date_mess_rate = 0.25  # 25% messy dates
        missing_rate = 0.05  # 5% missing values

    data = []

    for _ in range(num_records):
        event_registered = np.random.choice(EVENT_CHOICES, p=[0.25, 0.25, 0.25, 0.25])

        if event_registered != "None" and random.random() > 0.4:
            reg_date = fake.date_between(start_date="-6m", end_date="today")
        else:
            reg_date = None

        record = {
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
        data.append(record)

    df = pd.DataFrame(data)

    num_duplicates = int(num_records * duplicate_rate)
    duplicates = df.sample(num_duplicates, replace=True)
    df = pd.concat([df, duplicates], ignore_index=True)

    def mess_up_name(name):
        if random.random() < name_mess_rate:
            r = random.random()
            if r < 0.5:
                return name.upper()
            return name.lower()
        return name

    df["Name"] = df["Name"].apply(mess_up_name)

    def mess_up_email(email):
        if random.random() < email_error_rate:
            return email.replace("@", " at ")
        return email

    df["Email"] = df["Email"].apply(mess_up_email)

    def mess_up_date(d):
        r = random.random()
        if r < date_mess_rate * 0.4:
            return d.strftime("%m/%d/%Y")
        if r < date_mess_rate * 0.8:
            return d.strftime("%d-%m-%Y")
        if r < date_mess_rate:
            return "Unknown"
        return d

    df["Join_Date"] = df["Join_Date"].apply(mess_up_date)

    cols_to_nan = ["Event_Attendance", "Last_Login"]
    for col in cols_to_nan:
        df.loc[df.sample(frac=missing_rate).index, col] = np.nan

    df = df.sample(frac=1).reset_index(drop=True)

    if save_path:
        df.to_csv(save_path, index=False)
        print(f"Generated messy data at {save_path} with {len(df)} rows.")

    return df


if __name__ == "__main__":
    import os

    if not os.path.exists("../data"):
        os.makedirs("../data", exist_ok=True)

    generate_messy_data(save_path="../data/messy_club_data.csv")
