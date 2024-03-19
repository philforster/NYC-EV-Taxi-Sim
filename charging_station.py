from collections import deque
import taxi
class charging_station:
    
   
    queue = deque()
    
    def __init__(self,sim_env,id,x,y,charging_speed=1) -> None:
        self.id = id
        self.curr_x = x
        self.curr_y= y
        self.charging_speed = charging_speed
        self.sim_env = sim_env
    
    def getQueueLength(self):
        return self.queue.count()

    def getWaitingTime(self):
        charge = 0
        for taxi in self.queue:
            charge+=taxi.MAX_BATTERY-taxi.getBattery()
        
        return charge/self.charging_speed

    def addTaxi(self,taxi):
        self.queue.appendleft(taxi)

    def charge(self)->None:
        if(self.queue.count()>0):
            if(self.queue.index(0).getCharged(self.charging_speed)):
                self.queue.popleft().finishCharging()


