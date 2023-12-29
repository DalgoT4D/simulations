"""a simulation of visits to a set of districts"""
from random import random
from datetime import timedelta
from faker import Faker


class Simulation:
    """simulate visits to a set of districts"""

    def __init__(self, start_date, config, datastore):
        self.config = config
        self.datastore = datastore
        self.faker = Faker("en-IN")
        self.context = {
            "current_date": start_date,
            "current_district": self.make_district(),
            "last_health_worker": -1,
            "visited_districts": [],
            "todays_visits": 0,
        }

    def open(self):
        """open the destination"""
        self.datastore.open()

    def close(self):
        """close the destination"""
        self.datastore.close()

    def make_district(self):
        """set up a new district"""
        district = {
            "name": self.faker.city_name(),
            "size": self.faker.random_int(
                self.config["district_size"]["min"], self.config["district_size"]["max"]
            ),
            "visits": [],
            "attendance": self.config["attendance"]["min"]
            + random()
            * (self.config["attendance"]["max"] - self.config["attendance"]["min"]),
            "age_distribution": {},
        }
        district["age_distribution"]["child"] = self.config["age_distribution"][
            "child"
        ] + 0.1 * (random() - 0.5)
        district["age_distribution"]["adult"] = self.config["age_distribution"][
            "adult"
        ] + 0.1 * (random() - 0.5)
        district["age_distribution"]["elder"] = (
            1
            - district["age_distribution"]["adult"]
            - district["age_distribution"]["child"]
        )
        return district

    def record_visit(self, visit):
        """write the visit to the destination"""
        self.datastore.record_visit(visit)

    def generate(self):
        """
        one run per day
        within that day, we try to hit as many people as possible
        from the target population, some percentage will show up to be served
         - these are the *visits*
        """
        cdctx = self.context["current_district"]
        if cdctx is None:
            return

        if random() > cdctx["attendance"]:
            return

        current_date_str = self.context["current_date"].strftime("%Y-%m-%d")

        # somebody showed up! set up the visit
        visit = {"district": cdctx["name"], "date": current_date_str}
        # who served them
        visit["health_worker"] = (self.context["last_health_worker"] + 1) % self.config[
            "health_workers"
        ]
        # who showed up
        visit["name"] = self.faker.name()
        visit["gender"] = "male" if random() < 0.5 else "female"
        age_x = random()
        if age_x < cdctx["age_distribution"]["child"]:
            visit["age_group"] = "child"
        elif age_x < cdctx["age_distribution"]["adult"]:
            visit["age_group"] = "adult"
        else:
            visit["age_group"] = "elder"

        # add the visit to the list
        self.context["current_district"]["visits"].append(visit)

        # and save the visit
        self.record_visit(visit)

        # each health worker gets a turn
        self.context["last_health_worker"] = visit["health_worker"]

        # we move on to the next district if the number of visits exceeds the expected number..
        # of it it's close enough
        if (
            len(cdctx["visits"])
            > cdctx["attendance"] * cdctx["size"] - self.config["daily_capacity"]["min"]
        ):
            self.context["visited_districts"].append(cdctx)
            self.context["current_district"] = self.make_district()
            self.context["current_date"] += timedelta(days=1)
            self.context["todays_visits"] = 0
            return

        # can only serve so many people in a day!
        self.context["todays_visits"] += 1
        if self.context["todays_visits"] > self.config["daily_capacity"]["max"]:
            self.context["current_date"] += timedelta(days=1)
            self.context["todays_visits"] = 0
