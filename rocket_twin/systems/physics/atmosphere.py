import numpy as np
from cosapp.base import System
from numpy import linalg


class Atmosphere(System):
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

        self.add_inward("Cx", 0.35, desc = "rocket drag coefficient")
        self.add_inward("A", 1.0, desc = "cross sectional area", unit = "m**2" )

        #outwards
        self.add_outward("rho", 1.0, desc = "air density", unit = "kg/m**3")
        self.add_outward("drag", np.array([0.0, 0.0, 0.0]), desc = "drag force at given velocity and altitude", unit = "N")
        self.add_outward("z", 1.0, desc = "altitude", unit = "m")
        self.add_inward("v_rela", 1.0, desc = "system velocity relative to the air", unit = "m/s")


    def compute(self):
        self.v_rela = np.linalg.norm(self.atm_v)
        self.z = self.atm_pos[2]

        ##density model
        if self.atmosphere_is_on :
                        # Constants for atmospheric calculations
            g = 9.80665  # gravitational acceleration (m/s^2)
            R = 287.05  # gas constant for air (J/(kg*K))
            
            # Base conditions at sea level
            T0 = 288.15  # sea level standard temperature (K)
            P0 = 101325  # sea level standard pressure (Pa)
            
            # Define the altitude ranges and temperature lapse rates for each atmospheric layer in meters
            atmosphere_layers = [
                {"name": "troposphere", "bottom": 0, "top": 11000, "lapse_rate": -0.0065},
                {"name": "lower_stratosphere", "bottom": 11000, "top": 20000, "lapse_rate": 0},
                {"name": "upper_stratosphere", "bottom": 20000, "top": 32000, "lapse_rate": 0.001},
                {"name": "stratopause", "bottom": 32000, "top": 47000, "lapse_rate": 0.0028},
                {"name": "lower_mesosphere", "bottom": 47000, "top": 51000, "lapse_rate": 0},
                {"name": "middle_mesosphere", "bottom": 51000, "top": 71000, "lapse_rate": -0.0028},
                {"name": "upper_mesosphere", "bottom": 71000, "top": 85000, "lapse_rate": -0.002},
                {"name": "lower_thermosphere", "bottom": 85000, "top": 90000, "lapse_rate": 0},
                {"name": "upper_thermosphere", "bottom": 90000, "top": None, "lapse_rate": 0.002}  # Extends into space
            ]
            
            def calculate_temperature(altitude, layers):
                T = T0
                for layer in layers:
                    if altitude < layer["bottom"]:
                        break
                    elif layer["top"] is None or altitude <= layer["top"]:
                        if layer["lapse_rate"] == 0:  # Isothermal layer
                            T = T
                        else:
                            T += layer["lapse_rate"] * (altitude - layer["bottom"])
                        break
                    else:
                        T += layer["lapse_rate"] * (layer["top"] - layer["bottom"])
                return T
            
            def calculate_pressure(altitude, layers):
                P = P0
                T_base = T0
                altitude_base = 0
                for layer in layers:
                    top = layer["top"] if layer["top"] is not None else float('inf')
                    
                    if altitude < layer["bottom"]:
                        break
                    elif altitude <= top:
                        h = altitude - altitude_base
                        if layer["lapse_rate"] == 0:  # Isothermal layer
                            P = P * np.exp(-g * h / (R * T_base))
                        else:
                            T = T_base + layer["lapse_rate"] * h
                            P = P * (T / T_base) ** (-g / (R * layer["lapse_rate"]))
                        break
                    else:
                        h = top - altitude_base
                        if layer["lapse_rate"] == 0:
                            P = P * np.exp(-g * h / (R * T_base))
                        else:
                            T_top = T_base + layer["lapse_rate"] * h
                            P = P * (T_top / T_base) ** (-g / (R * layer["lapse_rate"]))
                        altitude_base = top
                        T_base = T_top if top != float('inf') else T_base
                return P
            
            def calculate_density(altitude, layers):
                T = calculate_temperature(altitude, layers)
                P = calculate_pressure(altitude, layers)
                density = P / (R * T)
                return density

            self.rho = calculate_density(self.z,atmosphere_layers) # final variable

        else: #if we want to remove atmosphere from model
            self.rho = 0.0 

        self.drag = -0.5*self.Cx*self.A*self.rho*(self.v_rela**2)*(self.atm_v/np.linalg.norm(self.atm_v)) #must add self.Cx instead of 0.35
        print(self.drag, self.atm_v)