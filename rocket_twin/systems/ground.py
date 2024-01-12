from cosapp.base import System

from rocket_twin.systems import Station


class Ground(System):
    """Ground system that manages the stations.

    Inputs
    ------
    stations : List[System],
        space stations

    Outputs
    ------
    """

    def setup(self, stations=None):

        if stations is None:
            stations = []

        self.add_property("stations", stations)  # to keep the station information in compute

        for station in stations:

            self.add_child(
                Station(station, n_stages=1), pulling={"a": f"a_{station}","v":f"v_{station}", "pos": f"pos_{station}"}
            )
            self.add_transient(
                f"v_{station}", der=f"a_{station}"
            )  # integrate acceleration to get velocity
            self.add_transient(
                f"r_{station}", der=f"v_{station}"
            )  # integrate velocity to get position

            # self.add_outward(f"pos_{station}")

    def compute(self):

        for station in self.stations:

            self[f"pos_{station}"] = self[f"r_{station}"]
