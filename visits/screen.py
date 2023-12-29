"""screen output for simulation data"""


class Screen:
    """write simulation data to the screen"""

    def open(self):
        """open the destination"""

    def close(self):
        """close the destination"""

    def record_visit(self, visit):
        """write the visit to the destination"""
        print(visit)
