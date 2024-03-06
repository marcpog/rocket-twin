import numpy as np
from numpy import linalg
from cosapp.base import System



class EnginePerfo(System):
    """Simple model of an engine's thrust force.

    Inputs
    ------
    w_out [kg/s]: float,
        fuel consumption rate

    Outputs
    ------
    force [N]: float,
        thrust force
    """

    def setup(self, stations= None):
        
        self.add_transient("test", der = "1", desc ="random variable so that w_out doesn't stick to 0 in tests")  # Enable to solve a cosApp bug (Otherwise, engine perfo is only run once)
        # Inputs
        self.add_inward("w_out", 0.0, desc="Fuel consumption rate", unit="kg/s")

        # Parameters
        self.add_inward("v", np.array([0.0, 0.0, 1.0]), desc = "velocity", unit= "m/s")
        self.add_inward("isp", 300.0, desc="Specific impulsion in vacuum", unit="s")
        self.add_inward("g_0", 10.0, desc="Gravity at Earth's surface", unit="m/s**2")

        self.add_outward("force", np.array([0.0, 0.0, 1.0]), desc="Thrust force", unit="N")

    def compute(self):

        if np.linalg.norm(self.v) >= 1:  #avoid dividing by 0
            self.force = (self.v/np.linalg.norm(self.v))*self.isp * self.w_out * self.g_0
        else:
            self.force = np.array([0,0,self.isp * self.w_out * self.g_0])