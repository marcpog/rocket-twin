import numpy as np
from cosapp.drivers import RungeKutta
from cosapp.recorders import DataFrameRecorder

from rocket_twin.systems import Ground

class TestDrag:  
    """Tests for the rocket model."""



    def test_drag(self):  #test if the drag is well computed during flight
        sys = Ground("sys",stations = ["station1"])
        driver = sys.add_driver(RungeKutta(order=4, dt=1.0))
        driver.add_recorder(DataFrameRecorder(includes=[]), period=1.0) # magie noire de Luca pour résoudre le bug de recorder (sinon il run tous les recorder)
        driver.time_interval = (0, 40)  # with the following set of data, the rocket reaches 6450e3 km at 45 seconds, so we stop the simulation right after it

        #init values must be re-adjusted every time a default value is changed in the code
        init = {"station1.rocket.flying" : True,
            "station1.fueling" : False, #skipping fueling phase
            "station1.rocket.controller.is_on_1": True,  #if we skip fueling phase, we need to manually switch on some variables before flying phase
            f"station1.rocket.stage_{1}.tank.fuel.w_out_max": 100.0,  #mass flow rate
            f"station1.rocket.stage_{1}.engine.perfo.isp": 500.0,  # on affecte seulement des valeurs à des inputs
            f"station1.rocket.stage_{1}.tank.fuel.weight_p": 10000.0,
            "station1.rocket.atmo.Cx" : 0.2,
            "station1.rocket.atmo.A" : 5.0}  

        driver.set_scenario(init=init)

        sys.run_drivers()
        Cx = sys.station1.rocket.atmo.Cx
        A = sys.station1.rocket.atmo.A
        rho = sys.station1.rocket.atmo.rho
        v_rela = sys.station1.rocket.atmo.v_rela
        atm_v = sys.station1.rocket.atmo.atm_v
        np.testing.assert_allclose(sys.station1.rocket.atmo.drag,  -0.5*Cx*A*rho*(v_rela**2)*(atm_v/np.linalg.norm(atm_v)))