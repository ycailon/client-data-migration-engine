from __future__ import annotations

import argparse
import random
from pathlib import Path

import pandas as pd
from faker import Faker


def build_base(rows: int, seed: int) -> pd.DataFrame:
    Faker.seed(seed)
    random.seed(seed)
    fake = Faker("en_PH")

    records = []
    for index in range(1, rows + 1):
        first_name = fake.first_name()
        last_name = fake.last_name()

        records.append(
            {
                "customer_id": f"CUST-{index:06d}",
                "first_name": first_name,
                "last_name": last_name,
                "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=80),
                "phone": f"09{random.randint(10**8, 10**9 - 1)}",
                "email": fake.email(),
                "address": fake.street_address(),
                "city": fake.city(),
                "state_province": fake.province(),
                "postal_code": fake.postcode(),
                "country": "Philippines",
            }
        )

    frame = pd.DataFrame(records)

    if rows >= 20:
        frame.loc[2, "email"] = "not-an-email"
        frame.loc[5, "first_name"] = None
        frame.loc[8, "phone"] = "12"
        frame.loc[12, "date_of_birth"] = "2099-01-01"

        duplicate_source = frame.loc[0].copy()
        duplicate_source["customer_id"] = f"CUST-{rows + 1:06d}"
        frame = pd.concat([frame, pd.DataFrame([duplicate_source])], ignore_index=True)

    return frame


def client_a(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.rename(
        columns={
            "customer_id": "Customer ID",
            "first_name": "First Name",
            "last_name": "Last Name",
            "date_of_birth": "DOB",
            "phone": "Mobile",
            "email": "Email Address",
            "address": "Address",
            "city": "City",
            "state_province": "Province",
            "postal_code": "Postal Code",
            "country": "Country",
        }
    ).copy()

    result["DOB"] = pd.to_datetime(result["DOB"], errors="coerce").dt.strftime("%m/%d/%Y")
    result["Mobile"] = result["Mobile"].astype(object)

    if len(result) >= 4:
        result.loc[1, "First Name"] = f"  {result.loc[1, 'First Name']}  "
        result.loc[3, "Email Address"] = f" {result.loc[3, 'Email Address']} "

    return result


def client_b(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.rename(
        columns={
            "customer_id": "id",
            "first_name": "fname",
            "last_name": "lname",
            "date_of_birth": "birth_date",
            "phone": "mobile_number",
            "email": "email",
            "address": "street_address",
            "city": "municipality",
            "state_province": "region",
            "postal_code": "zip",
            "country": "country_name",
        }
    ).copy()

    result["birth_date"] = pd.to_datetime(
        result["birth_date"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    def phone_variant(value: object) -> object:
        if not isinstance(value, str) or not value.startswith("09"):
            return value
        return f"+63 {value[1:4]} {value[4:7]} {value[7:]}"

    result["mobile_number"] = result["mobile_number"].map(phone_variant)
    return result


def client_c(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.rename(
        columns={
            "customer_id": "customer_no",
            "first_name": "given_name",
            "last_name": "surname",
            "date_of_birth": "birthday",
            "phone": "contact_no",
            "email": "email_address",
            "address": "home_address",
            "city": "town_city",
            "state_province": "state",
            "postal_code": "postcode",
            "country": "country",
        }
    ).copy()

    result["birthday"] = pd.to_datetime(
        result["birthday"], errors="coerce"
    ).dt.strftime("%d-%b-%Y")
    result["contact_no"] = result["contact_no"].map(
        lambda value: value[1:]
        if isinstance(value, str) and value.startswith("0")
        else value
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("data/generated"))
    args = parser.parse_args()

    if args.rows < 1:
        raise ValueError("--rows must be at least 1")

    args.output.mkdir(parents=True, exist_ok=True)

    base = build_base(args.rows, args.seed)

    client_a(base).to_csv(args.output / "client_a.csv", index=False)

    with pd.ExcelWriter(args.output / "client_b.xlsx", engine="openpyxl") as writer:
        client_b(base).to_excel(writer, sheet_name="Customers", index=False)

    client_c(base).to_csv(args.output / "client_c.csv", index=False)

    print(f"Generated sample files in {args.output.resolve()}")


if __name__ == "__main__":
    main()
