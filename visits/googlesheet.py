"""a google sheets data store"""


class GoogleSheet:
    """a google sheets destination"""

    def __init__(self, worksheet_name: str):
        self.worksheet = None
        raise NotImplementedError(
            "todo: create a worksheet connection usign the given name " + worksheet_name
        )

    def open(self):
        """no-op"""

    def close(self):
        """no-op"""

    def record_visit(self, visit):
        """record the visit"""
        self.worksheet.append_row(
            [
                visit["date"],
                visit["district"],
                visit["name"],
                visit["gender"],
                visit["age_group"],
                visit["health_worker"],
            ]
        )
