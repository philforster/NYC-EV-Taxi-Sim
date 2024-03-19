from random import random
class user:
    id=0

    start_x=0
    start_y = 0
    
    dest_x=0
    dest_y=0

    init_time =0
    pickup_time=0


    def __init__(self,sim_env,id,init_time):
        self.id = id
        self.ack = False
        self.my_taxi=None


        
        self.sim_env = sim_env
        
        self.init_time = init_time
        
        self.start_x,self.start_y =self.generate_location()
        self.dest_x, self.dest_y = self.generate_location()
        
        self.init_time
    
    def getOnTaxi(self,taxi):
        self.my_taxi = taxi
        self.pickup_time = self.sim_env.getTime()

    def ack(self):
        self.ack = True

    def isAck(self):
        return self.ack

    def generateLocation(self):
        return self.sim_env.MAP_WIDTH*random(),self.sim_env.MAP_HEIGHT*random()

    def dropOff(self):
        #picked up = false
        print("dropped")
        self.my_taxi = None
        wait_time = self.pickup_time - self.init_time
        travel_time = self.sim_env.getTime()-self.pickupTime

    def isPassenger(self)->bool:
        return self.my_taxi != None