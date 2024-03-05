import numpy as np
from cosapp.drivers import RungeKutta
from cosapp.recorders import DataFrameRecorder
from scipy import optimize
from rocket_twin.systems import Station

from rocket_twin.systems import Ground

z_LEO = (6400e3 + 300e3) #LEO altitude
V_LEO = 7.8e3 #7.8km/s

def simulation(Z): # Z = np.array([Hm1, Hm2, teta1, teta2, tvol]) (vector to optimize)
    Hm1, Hm2, teta1, teta2, tvol = Z[0], Z[1], Z[2], Z[3], Z[4]

    sys = Ground("sys",stations = ["station1"])
    driver = sys.add_driver(RungeKutta(order=4, dt=1.0))
    driver.add_recorder(DataFrameRecorder(includes=[]), period=1.0) # magie noire de Luca pour résoudre le bug de recorder (sinon il run tous les recorder)
    driver.time_interval = (0, tvol)  # with the following set of data, the rocket reaches 6450e3 km at 45 seconds, so we stop the simulation right after it

        #init values must be re-adjusted every time a default value is changed in the code
    init = {"station1.rocket.teta1" : teta1, 
            "station1.rocket.teta2" : teta2,
            "station1.rocket.Hm1": Hm1,
            "station1.rocket.Hm2": Hm2,
            f"station1.rocket.stage_{1}.tank.fuel.w_out_max": 100.0,
            "station1.rocket.flying" : True,
            "station1.fueling" : False, #skipping fueling phase
            "station1.rocket.controller.is_on_1": True,  #if we skip fueling phase, we need to manually switch on some variables before flying phase
            f"station1.rocket.stage_{1}.engine.perfo.isp": 500.0,  
            f"station1.rocket.stage_{1}.tank.fuel.weight_p": 30000.0}  

    driver.set_scenario(init=init)

    sys.run_drivers()

    print(sys.station1.pos[2])
    #return (sys.pos_station1[2], sys.v_station1[0])
    return (sys.station1.pos[2], sys.station1.v[0]) #altitude and tangential velocity

#sys2 = Station("station1")
#sys = Ground("sys", stations = [sys2])  #for some reason it works like this if Ground is used outside of a test


def objective_func(Z): # Z= np.array([Hm1, Hm2, teta1, teta2, tvol])
    return Z[4]  #function to minimze (time of flight engine on)

def eq_constraint1(Z):  # Z= np.array([Hm1, Hm2, teta1, teta2, tvol])
    return simulation(Z)[0] - z_LEO #altitude must be equal to LEO orbital altitude

def eq_constraint2(Z):  # Z= [Hm1, Hm2, teta1, teta2, tvol]
    return simulation(Z)[1] - V_LEO #velocity must be equal to LEO orbital speed
    

Hm1_guess, Hm2_guess, teta1_guess, teta2_guess, tvol_guess = 6600e3, 6650e3, 45*np.pi/180, 45*np.pi/180, 50  #or 300   #initial guess for optimization algorithm  
Z_guess = np.array([Hm1_guess, Hm2_guess, teta1_guess, teta2_guess, tvol_guess])

print(simulation(Z_guess))

eq_cons = [eq_constraint1, eq_constraint2]

res = optimize.fmin_slsqp(objective_func, Z_guess, eqcons = eq_cons, bounds=((0.,6800e3),(0.,6800e3),(0.,2*np.pi/180),(0.,2*np.pi/180),(0.,500)))
Hm1_opti, Hm2_opti, teta1_opti, teta2_opti, tvol_opti = res



print("Hm1 optimal =", Hm1_opti, "Hm2 optimal =", Hm2_opti, "teta1 optimal =", teta1_opti, "teta2 optimal =", teta2_opti, "optimal time of flight =", tvol_opti)