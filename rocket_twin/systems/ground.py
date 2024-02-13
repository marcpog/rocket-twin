from cosapp.base import System
from math import pi
import numpy as np

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

        self.add_property("stations", stations)  # to keep the station information in compute  (property turned into an inward so that I can initiate a value in test)

        for station in stations:

            self.add_child(
                Station(station, n_stages=1), pulling={"a": f"a_{station}","v":f"v_station_{station}", "pos": f"pos_{station}"}
            )
            self.add_transient(
                f"v_{station}", der=f"a_{station}"
            )  # integrate acceleration to get velocity
            self.add_transient(
                f"pos_{station}", der=f"v_{station}"
            )  # integrate velocity to get position
            

           # self.add_outward(f"v_station_{station}", np.zeros(3), desc = "velocity" , unit = "m/s")
            
    def transition(self):
        for station in self.stations:

            if self[station].rocket.rotation.present:  # rotate the speed vector around y-axis by multiplying by rotation matrix at a given height (Hm)
                teta = self[station].rocket.teta
                self[f"v_{station}"] = np.dot(np.array([[np.cos(teta), 0, np.sin(teta)], [0, 1, 0], [-np.sin(teta), 0, np.cos(teta)]]),self[f"v_{station}"].T ).T 
                print("test")

    def compute(self):
        
        for station in self.stations:

            self[f"v_station_{station}"] = self[f"v_{station}"]   # required so that the v value is correctly stored during simulation
            print(self[f"pos_{station}"], self[f"v_{station}"], self.time)  #visualize data 
