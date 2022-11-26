import numpy as np
from cosapp.base import System
from Utility import aeroCoefs

class Aerodynamics(System):
    
    def setup(self):
        
        #Rocket inputs
        self.add_inward('Sref', 1.767e-2, desc = "Aerodynamic Surface of Reference")
        # self.add_inward('Cd', 1., desc = "Drag Coefficient")
        # self.add_inward('Cl', 1., desc = "Lift Coefficient")
        # self.add_inward('gf', 1., desc = "GF Distance")

        #Trajectory inputs
        self.add_inward('v', np.ones(2), desc = "Rocket velocity")
        self.add_inward('theta', 0., desc = "Rocket direction")

        #Atmosphere inputs
        self.add_inward('rho', 1.225, desc = "Air density")

        #Aerodynamics outputs
        self.add_outward('Fa', np.zeros(2), desc = "Aerodynamic Force")
        self.add_outward('Ma', 0., desc = "Aerodynamic Moment")
        
    def compute(self):
        incidence = self.theta - np.arctan2(self.v[1],self.v[0])
        incidence = incidence%(2*np.pi) - np.pi

        Cx, Cn, Z_CPA = aeroCoefs(incidence)

        self.Fa = 0.5*self.rho*np.linalg.norm(self.v)**2*self.Sref*np.array([Cx, Cn]) # Selon l'axe de la fusée

        G = .300
        self.Ma = self.Fa[1]*(G - Z_CPA) # Bras de levier entre Le centre de masse et le centre de poussée aérodynamique

        self.Fa = np.array([-self.Fa[0]*np.cos(self.theta) - self.Fa[1]*np.sin(self.theta),
                            -self.Fa[0]*np.sin(self.theta) + self.Fa[1]*np.cos(self.theta)]) # Dans le repère cartésien