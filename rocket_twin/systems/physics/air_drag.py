import numpy as np
from cosapp.base import System
from numpy import linalg
from ambiance import Atmosphere


class Drag(System):
    """Dynamics of a physical system.

    Inputs
    ------
    atm_pos [m]: float,
        psition of each component of the system
    v_rela [m/s]: float,
        velocity of each component of the system relative to air

    Outputs
    ------
    drag [N]: float,
        drag force of the air on the system
    rho [kg/m**3]
        air density of the atmosphere at given altitude
    z [m]
        altitude of each component of the system
    """

    


    def setup(self):

        #inwards
        self.add_inward("atm_pos", np.array([0.0, 0.0, 1.0]), desc = "position in earth atmosphere", unit = "m")
        self.add_inward("atm_v", np.array([0.0, 0.0, 1.0]), desc = "system velocity relative to the air", unit = "m/s")
        self.add_inward("atmosphere_is_on", True, desc = "whether we take into account air density or not")
        self.add_inward("density_model", Atmosphere(np.linspace(0, 81e3, num=int(8100))).density ,desc = "list that contains all the density value from 0 to 81km", unit = "kg/m**3") #one data each 10 meter from 0m to 81km

        self.add_inward("Cx", 0.35, desc = "rocket drag coefficient")
        self.add_inward("A", 1.0, desc = "cross sectional area", unit = "m**2" )

        #outwards
        self.add_outward("rho", 1.0, desc = "air density", unit = "kg/m**3")
        self.add_outward("drag", np.array([0.0, 0.0, 0.0]), desc = "drag force at given velocity and altitude", unit = "N")
        self.add_outward("z", 1.0, desc = "altitude", unit = "m")
        self.add_inward("v_rela", 1.0, desc = "system velocity relative to the air", unit = "m/s")


    def compute(self):
        self.v_rela = np.linalg.norm(self.atm_v)
        self.z = self.atm_pos[2] - 6400.0e3

        ##density model
        if self.atmosphere_is_on :
            if self.z < -10.0:
                raise ValueError("altitude can not be negative.")
            elif self.z < 81e3:
                arrondi = round(self.z / 10)
                #divide altitude by 10 and turn it into an integer so that it matches density index
                self.rho = self.density_model[arrondi]
            else:
                self.rho = 0.0 #at higher altitude than 81km, we neglect air density

        else: #if we want to remove atmosphere from model
            self.rho = 0.0 

        self.drag = -0.5*self.Cx*self.A*self.rho*(self.v_rela**2)*(self.atm_v/np.linalg.norm(self.atm_v)) 
        print(self.drag, self.atm_v, self.rho, self.atm_pos, self.time)