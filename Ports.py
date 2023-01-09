from cosapp.base import Port, BaseConnector
import numpy as np

def RotMat3D(ang):
    
    #ang[0] = phi, ang[1] = theta, ang[2] = psi
    
    l1 = np.array([np.cos(ang[2])*np.cos(ang[1]), -np.sin(ang[2])*np.cos(ang[0]) + np.cos(ang[2])*np.sin(ang[1])*np.sin(ang[0]),
                    np.sin(ang[2])*np.sin(ang[0]) + np.cos(ang[2])*np.sin(ang[1])*np.cos(ang[0])])
    l2 = np.array([np.sin(ang[2])*np.cos(ang[1]),  np.cos(ang[2])*np.cos(ang[0]) + np.sin(ang[2])*np.sin(ang[1])*np.sin(ang[0]),
                   -np.cos(ang[2])*np.sin(ang[0]) + np.sin(ang[2])*np.sin(ang[1])*np.cos(ang[0])])
    l3 = np.array([-np.sin(ang[1]), np.cos(ang[1])*np.sin(ang[0]), np.cos(ang[1])*np.cos(ang[0])])
    
    A = np.round(np.array([l1,l2,l3]), 5)
    
    return A



class VelPort(Port):
    """Velocity Port """
    def setup(self):
        self.add_variable('val', np.zeros(3), desc = "Velocity Components", unit = 'm/s')
        

    class Connector(BaseConnector):
        """Custom connector for `VelPort` objects
        """
        def __init__(self, name: str, sink: Port, source: Port, *args, **kwargs):
            super().__init__(name, sink, source)

        def transfer(self) -> None:
            sink = self.sink
            source = self.source
            
            if source.owner.referential == 'Earth' and sink.owner.referential == 'Rocket': 
                sink.val = np.matmul(RotMat3D(sink.owner[f'{sink.owner.name}_ang']), source.val)

            elif sink.owner.referential == 'Earth' and source.owner.referential == 'Rocket':
                sink.val = np.matmul(RotMat3D(-source.owner[f'{source.owner.name}_ang']), source.val)
                
            else:
                sink.val = source.val



class AclPort(Port):
    """Acceleration Port """
    def setup(self):
        self.add_variable('val', np.zeros(3), desc = "Acceleration Components", unit = 'm/s**2')
        

    class Connector(BaseConnector):
        """Custom connector for `AclPort` objects
        """
        def __init__(self, name: str, sink: Port, source: Port, *args, **kwargs):
            super().__init__(name, sink, source)

        def transfer(self) -> None:
            sink = self.sink
            source = self.source
            
            # try:
            #     gini = source.owner.g
            #     gfin = sink.owner.g
            #     print(f'Going from {source.owner.__str__} to {sink.owner.__str__}')
            #     print("Intitial", gini)
            #     print("Final", gfin)
            # except:
            #     pass

            if source.owner.referential == 'Earth' and sink.owner.referential == 'Rocket': 
                sink.val = np.matmul(RotMat3D(sink.owner[f'{sink.owner.name}_ang']), source.val)
                 # print(RotMat3D(sink.owner[f'{sink.owner.name}_ang']))
                print(sink.owner[f'{sink.owner.name}_ang'], sink.owner.name)


            elif sink.owner.referential == 'Earth' and source.owner.referential == 'Rocket':
                sink.val = np.matmul(RotMat3D(-source.owner[f'{source.owner.name}_ang']), source.val)
                # print(RotMat3D(-source.owner[f'{source.owner.name}_ang']))
            else:
                sink.val = source.val