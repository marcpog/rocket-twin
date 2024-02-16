import numpy as np
from cosapp.drivers import RungeKutta
from cosapp.recorders import DataFrameRecorder

from rocket_twin.systems import Ground

class TestGround2:  
    """Tests for the rocket model."""

    def test_run_once(self):
        sys = Ground("sys")

        sys.run_once()

    def test_flight_rotation(self):  #test the ability of the rocket to rotate by an agle teta at the expected altitude
        sys = Ground("sys",stations = ["station1"])
        driver = sys.add_driver(RungeKutta(order=4, dt=1.0))
        driver.add_recorder(DataFrameRecorder(includes=[]), period=1.0) # magie noire de Luca pour résoudre le bug de recorder (sinon il run tous les recorder)
        driver.time_interval = (0, 45.5)  # with the following set of data, the rocket reaches 6450e3 km at 45 seconds, so we stop the simulation right after it

        #init values must be re-adjusted every time a default value is changed in the code
        init = {"station1.rocket.teta" : 10*np.pi/180, 
            "station1.rocket.Hm": 6450.0e3,
            f"station1.rocket.stage_{1}.tank.fuel.w_out_max": 100.0,
            "station1.rocket.flying" : True,
            "station1.fueling" : False, #skipping fueling phase
            "station1.rocket.controller.is_on_1": True,  #if we skip fueling phase, we need to manually switch on some variables before flying phase
            f"station1.rocket.stage_{1}.engine.perfo.isp": 500.0,  # on affecte seulement des valeurs à des inputs
            f"station1.rocket.stage_{1}.tank.fuel.weight_p": 10000.0}  

        driver.set_scenario(init=init)

        sys.run_drivers()


        theta = sys.station1.rocket.teta
        np.testing.assert_allclose(sys.station1.rocket.stage_1.engine.perfo.w_out, 100.0) #check if variables are well assigned
        np.testing.assert_allclose(sys.station1.rocket.stage_1.engine.perfo.force ,np.dot(np.array([[np.cos(theta), 0, np.sin(theta)], [0, 1, 0], [-np.sin(theta), 0, np.cos(theta)]]), np.array([0,0,sys.station1.rocket.stage_1.engine.perfo.isp * sys.station1.rocket.stage_1.engine.perfo.w_out * sys.station1.rocket.stage_1.engine.perfo.g_0]).T ).T,atol=500 )
        #absolute tolerance =500 N (0.01% relative tolerance) because thrust orientation changes during one second after rotation time between 45 sec and 45.5 sec due to gravity effect.

#debugging
#A= TestGround2()
#A.test_flight_rotation() 