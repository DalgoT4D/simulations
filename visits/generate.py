"""generate simulation data"""

import os
from datetime import datetime
import argparse
from dotenv import load_dotenv

# from googlesheet import GoogleSheet
from postgres import Postgres
from screen import Screen
from simulation import Simulation

CONFIG = {
    "districts": 10,
    "district_size": {"min": 10000, "max": 1000000},
    "attendance": {"min": 0.001, "max": 0.01},
    "daily_capacity": {"min": 50, "max": 500},
    "age_distribution": {"child": 0.3, "adult": 0.5, "elder": 0.2},
    "health_workers": 5,
    "absenteeism": 0.1,
}

# ==============
parser = argparse.ArgumentParser(description="Generate simulation data")
parser.add_argument("--verbose", action="store_true", help="verbose output")
parser.add_argument("--output", choices=["db", "screen"], default="db")
parser.add_argument("start_date", help="start date")
parser.add_argument("end_date", help="start date")
args = parser.parse_args()

start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
end_date = datetime.strptime(args.end_date, "%Y-%m-%d")


# ==============
if args.output == "db":
    load_dotenv()

    DB_ENV = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "dbname": os.getenv("DB_NAME"),
    }

    datastore = Postgres(DB_ENV)

# ==============
elif args.output == "screen":
    datastore = Screen()

# ==============
datastore.open()
datastore.verbose = args.verbose

sim = Simulation(start_date, CONFIG, datastore)
while sim.context["current_date"] < end_date:
    sim.generate()

datastore.close()

# ==============
# generate some stats
print(f"Date: {sim.context['current_date'].strftime('%Y-%m-%d')}")
print(f"{sim.context['todays_visits']} visits today")
print(f"Current District: {sim.context['current_district']['name']} ")
print(f"Population: {sim.context['current_district']['size']} ")
print(
    f"Expected #visits: {(sim.context['current_district']['size'] * sim.context['current_district']['attendance']):.0f} "
)
print(f"Visits so far: {len(sim.context['current_district']['visits'])}")
print(f"Visits per day: {sim.config['daily_capacity']['max']}")
