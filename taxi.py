import numpy as np
import random as random
import math
import user
import charging_station
import sim_env
MAX_BATTERY = 100
CLOSEST_DISTANCE = 10000
MIN_DIST_TO_TAXI =100
NUM_TAXIS = 10

class Taxi():
    id = 0
    assigned_region = 0
    occupied =False
    going_to_charger=False
    curr_speed = 1.2
    #add return to region
    states = ['wait','charging','goingcharge','driving pass','going to pass']
    state = 0

    best_charger = 0
    closest_user = 0


    dest_charger_index = 0

    
    battery=0

    consumption =0.1
    def __init__(self,sim_env,id,assigned_region) -> None:
        
        
        self.id = id
        self.assigned_region = assigned_region
        self.sim_env = sim_env
        self.passenger = None
        pass

    def init_position(self, region):
        self.curr_x = random()*self.sim_env.MAP_WIDTH
        self.curr_y = random()*self.sim_env.MAP_HEIGHT

    def getCharged(self,charging_speed)->bool:
        self.battery = max(MAX_BATTERY,self.battery+ charging_speed)
        if(self.battery==MAX_BATTERY):
            self.charging = False
        return self.battery==MAX_BATTERY
    
    def get_battery(self)->int:
        return self.battery
    
    def goTo(self):
        del_x = self.dest_x - self.curr_x
        del_y = self.dest_y - self.curr_y

        angle = math.arctan(del_y/del_x)

        self.curr_x += math.cos(angle)*self.curr_speed
        self.curr_y += math.sin(angle)*self.curr_speed

    #def pickup(self):

    def finishCharging(self):
        state = 0

    def decideToCharge(self):
        if(self.battery<15):
            return True
        
        if(self.sim_env.getWaiting()<3):
            return True
        
        return False
    
    #TODO: Make speed dependent on region
    #def getg

    #TODO Add regions
    def move(self):
        best_charger=0
        battery -= self.consumption
        if self.state>1:
            self.goTo()
            if math.dist([self.curr_x,self.curr_y], [self.dest_x,self.dest_y])<self.moving_speed/2:
                match (self.state):
                    case 2: #arrived at charger
                        self.charging_stations[best_charger].addTaxi(self)
                        self.curr_x,self.curr_y = self.dest_x,self.dest_y
                        self.state = 1
                    case 3: #arriving at passenger destination
                        self.passenger.dropOff()
                        #record journey stats
                        self.curr_x,self.curr_y = self.dest_x,self.dest_y
                        self.state = 0
                    case 4: #pick up pass
                        
                        self.passenger = self.sim_env.getUser(closest_user)
                        self.passenger.getOnTaxi(self)
                        
                        self.curr_x,self.curr_y = self.dest_x,self.dest_y
                        self.state = 3


        else: 
            if self.decideToCharge():

                best_cost=10000
                best_charger=0
                i=0
                charging_stations = self.sim_env.charging_stations
                for c in self.sim_env.charging_stations:
                    waiting_time = c.getWaitingTime()
                    charging_time = (MAX_BATTERY-self.battery)/c.charging_speed
                    #TODO: Make speed dependent on region
                    #calculate time to get to charger
                    moving_time = math.dist([self.curr_x, self.curr_y],[c.x, c.y])/self.curr_speed
                    #todo (maybe)
                    cost = waiting_time+charging_time + moving_time
                    if(cost<best_cost):
                        best_cost = cost
                        best_charger = i
                    #pick
                    i+=1

                self.dest_x = charging_stations[best_charger].x
                self.dest_y = charging_stations[best_charger].y
                self.dest_charger = best_charger
                #self.going_to_charger=True
                self.state = 2


                self.goTo()
            else: 
                #move to best area
                #check customer list for distance between customer and taxi
                users = self.sim_env.users
                closest_distance = CLOSEST_DISTANCE
                min_dist_to_taxi = MIN_DIST_TO_TAXI
                closest_user=0
                for u in users:
                    if u.isAck()==False:
                        distance_to_u = math.dist([self.curr_x, self.curr_y],[u.start_x, u.start_y])

                        if(distance_to_u<closest_distance):
                            closest_distance = distance_to_u
                            closest_user = i
                    
                self.sim_env.getUser(closest_user).ack()
                if(closest_distance<min_dist_to_taxi):
                    #go to user
                    self.dest_x = users[closest_user].start_x
                    self.dest_y = users[closest_user].start_y                    #calculate time to get to charger
                    self.state = 4

                    #on the user side, set to picked up and record start time
                    self.goTo()

                    #pick
                    i+=1
    
    


