import numpy as np
from cosapp.drivers import RungeKutta
from cosapp.recorders import DataFrameRecorder

from rocket_twin.systems import Ground

class TestDrag:  
    """Tests for the rocket model."""



    def test_drag1(self):  #test if the drag is well computed during flight
        sys = Ground("sys",stations = ["station1"])
        driver = sys.add_driver(RungeKutta(order=4, dt=1.0))
        driver.add_recorder(DataFrameRecorder(includes=[]), period=1.0) # magie noire de Luca pour résoudre le bug de recorder (sinon il run tous les recorder)
        driver.time_interval = (0, 20)  # with the following set of data, the rocket reaches 6450e3 km at 45 seconds, so we stop the simulation right after it

        #init values must be re-adjusted every time a default value is changed in the code
        init = {"station1.rocket.flying" : True,
            "station1.fueling" : False, #skipping fueling phase
            "station1.rocket.controller.is_on_1": True,  #if we skip fueling phase, we need to manually switch on some variables before flying phase
            f"station1.rocket.stage_{1}.tank.fuel.w_out_max": 100.0,  #mass flow rate
            f"station1.rocket.stage_{1}.engine.perfo.isp": 500.0,  # 500 KN thrust (for wout = 100kg/s)
            f"station1.rocket.stage_{1}.tank.fuel.weight_p": 10000.0,
            "station1.rocket.atmo.Cx" : 0.2,
            "station1.rocket.atmo.A" : 5.0,
            "station1.rocket.atmo.atmosphere_is_on" : True
            }  

        driver.set_scenario(init=init)

        sys.run_drivers()
        Cx = sys.station1.rocket.atmo.Cx
        A = sys.station1.rocket.atmo.A
        rho = sys.station1.rocket.atmo.rho
        v_rela = sys.station1.rocket.atmo.v_rela
        atm_v = sys.station1.rocket.atmo.atm_v
        #unit test
        np.testing.assert_allclose(len(sys.station1.rocket.atmo.density_model), 8100)
        if sys.station1.rocket.atmo.z >0 and sys.station1.rocket.atmo.z < 81e3:
            assert sys.station1.rocket.atmo.rho > 0
        #integration test
        np.testing.assert_allclose(sys.station1.rocket.atmo.drag,  -0.5*Cx*A*rho*(v_rela**2)*(atm_v/np.linalg.norm(atm_v)))  #check that drag is well computed and transmitted
        np.testing.assert_array_less(0, np.linalg.norm(sys.station1.rocket.atmo.drag))  #check that drag is negative
        np.testing.assert_array_less(np.linalg.norm(sys.station1.rocket.atmo.drag), np.linalg.norm(sys.station1.rocket.stage_1.engine.perfo.force))  #check that drag is smaller than engine's thrust
        #assert 0 <= np.linalg.norm(sys.station1.rocket.atmo.drag)  # other method




    def test_drag2(self):  #test if drag is consistent with reality

        ## 1st system with atmosphere on
        sys1 = Ground("sys1",stations = ["station1"])
        driver = sys1.add_driver(RungeKutta(order=4, dt=1.0))
        driver.add_recorder(DataFrameRecorder(includes=[]), period=1.0) # magie noire de Luca pour résoudre le bug de recorder (sinon il run tous les recorder)
        driver.time_interval = (0, 20)  # with the following set of data, the rocket reaches 6450e3 km at 45 seconds, so we stop the simulation right after it

        #init values must be re-adjusted every time a default value is changed in the code
        init = {"station1.rocket.flying" : True,
            "station1.fueling" : False, #skipping fueling phase
            "station1.rocket.controller.is_on_1": True,  #if we skip fueling phase, we need to manually switch on some variables before flying phase
            f"station1.rocket.stage_{1}.tank.fuel.w_out_max": 100.0,  #mass flow rate
            f"station1.rocket.stage_{1}.engine.perfo.isp": 500.0,  # 500 KN thrust (for wout = 100kg/s)
            f"station1.rocket.stage_{1}.tank.fuel.weight_p": 10000.0,
            "station1.rocket.atmo.Cx" : 0.2,
            "station1.rocket.atmo.A" : 5.0,
            "station1.rocket.atmo.atmosphere_is_on" : True
            }  

        driver.set_scenario(init=init)

        sys1.run_drivers()
        v_rela1 = sys1.station1.rocket.atmo.v_rela
        atm_pos1 = sys1.station1.rocket.atmo.atm_pos
        drag1 = sys1.station1.rocket.atmo.drag

        ## 2nd system with no atmosphere
        sys2 = Ground("sys2",stations = ["station2"])
        driver = sys2.add_driver(RungeKutta(order=4, dt=1.0))
        driver.add_recorder(DataFrameRecorder(includes=[]), period=1.0) # magie noire de Luca pour résoudre le bug de recorder (sinon il run tous les recorder)
        driver.time_interval = (0, 20)  # with the following set of data, the rocket reaches 6450e3 km at 45 seconds, so we stop the simulation right after it

        #init values must be re-adjusted every time a default value is changed in the code
        init = {"station2.rocket.flying" : True,
            "station2.fueling" : False, #skipping fueling phase
            "station2.rocket.controller.is_on_1": True,  #if we skip fueling phase, we need to manually switch on some variables before flying phase
            f"station2.rocket.stage_{1}.tank.fuel.w_out_max": 100.0,  #mass flow rate
            f"station2.rocket.stage_{1}.engine.perfo.isp": 500.0,  # 500 KN thrust (for wout = 100kg/s)
            f"station2.rocket.stage_{1}.tank.fuel.weight_p": 10000.0,
            "station2.rocket.atmo.Cx" : 0.2,
            "station2.rocket.atmo.A" : 5.0,
            "station2.rocket.atmo.atmosphere_is_on" : False   # no atmosphere
            }  

        driver.set_scenario(init=init)

        sys2.run_drivers()
        rho2 = sys2.station2.rocket.atmo.rho
        v_rela2 = sys2.station2.rocket.atmo.v_rela
        atm_pos2 = sys2.station2.rocket.atmo.atm_pos
        drag2 = sys2.station2.rocket.atmo.drag

        np.testing.assert_allclose(rho2, 0.0)  #check that air density is 0 without atmosphere
        assert np.abs(np.linalg.norm(drag2)) <= np.abs(np.linalg.norm(drag1)) # check that drag with no atmosphere is smaller 
        assert v_rela1 <= v_rela2 #check that rocket with no atmosphere is faster
        assert np.linalg.norm(atm_pos1) <= np.linalg.norm(atm_pos2) #check that rocket with no atmosphere goes further
        