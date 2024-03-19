#from taxi import Taxi
#import charging_station
#import user
from collections import deque
from random import random
import tkinter
import numpy as np
import math
from time import sleep
MAX_BATTERY = 100
MAP_WIDTH = 500
MAP_HEIGHT = 500

MAX_BATTERY = 100
CLOSEST_DISTANCE = 10000
MIN_DIST_TO_TAXI =100
NUM_TAXIS = 4

class Sim_env:
    
    
    taxis = []
    time = 0
    users = []
    num_users=0
    charging_stations = []
    init_users=1

    def __init__(self,num_taxis=1):
        self.root = tkinter.Tk()
        self.root.title("NYC Taxis")
        self.root.geometry(f"{MAP_WIDTH}x{MAP_HEIGHT}")
      
        self.myCanvas = tkinter.Canvas(self.root, bg="white", height=MAP_HEIGHT, width=MAP_WIDTH)
        self.myCanvas.pack(expand = True)

        for i in range(num_taxis):
           self.createTaxi()
        
        for i in range(self.init_users):
           self.createUser()
        
        self.placeChargers()

    def createTaxi(self,region=1):
      self.taxis.append(Taxi(self,len(self.taxis)+1,region))
    
    def createUser(self,region=1):
        self.num_users+=1
        self.users.append(User(self,self.num_users,self.time))
    
    def userDroppedOff(self,id):
        for i in range(len(self.users)):
            if self.users[i].id == id:
                del self.users[i]
                return

    def render(self,canvas):
        canvas.delete("all")
        for charger in self.charging_stations:
          charger.render(canvas)

       #move all taxis
        for taxi in self.taxis:
           taxi.render(canvas)

        for user in self.users:
            user.render(canvas)
        
        self.root.update()


    def placeChargers(self):
       #todo: Make this better 
       self.charging_stations.append(charging_station(self,1,25,25,charging_speed=2))
    #    self.charging_stations.append(charging_station(self,2,75,74,charging_speed=1))
    #    self.charging_stations.append(charging_station(self,3,100,50,charging_speed=2))

    def printSystemState(self):
        print(f"Time : {self.time}")
        print(f"Taxis: {len(self.taxis)}\nUsers Waiting: {self.getWaitingUsers()}/{len(self.users)}")
        print(f"Taxi 1: battery level:{self.taxis[0].get_battery()} state:{self.taxis[0].states[self.taxis[0].state]}")
        print(f"Taxi 1: Position:x:{self.taxis[0].curr_x}\ty:{self.taxis[0].curr_y}") 
        if(len(self.users)>0):
            print(f"Passenger initial Position:x:{self.users[0].start_x}\ty:{self.users[0].start_y}  \nPassenger destination: x:{self.users[0].dest_x} \ty:{self.users[0].dest_y}") 
        print(f"Charging location 1: Position:x:{self.charging_stations[0].curr_x}\ty:{self.charging_stations[0].curr_y}") 

#    def placeCharger(self,id,x,y,chaging_speed=1):
    def getWaitingUsers(self):
        numWaiting = 0
        for aUser in self.users:
            if (aUser.isPassenger()==False):
               numWaiting+=1
        return numWaiting

    def getChargingStations(self):
        return self.charging_stations          
    
    def getChargingStation(self,i):   
        return self.charging_stations[i]         

    def getUser(self,index):
       return self.users[index]

    def getUserById(self,id):
        for user in self.users:
            if user.id==id:
                return user
        return None

    def passTime(self):
       self.time +=1
    def getTime(self):
        return self.time

    
    def simloop(self):
       #charge all first taxis in charging stations
        for charger in self.charging_stations:
          charger.charge()

       #move all taxis
        for taxi in self.taxis:
           taxi.move()
    
        #stochastically create users
        if(random()<0.005):
            self.createUser(self)
        self.render(self.myCanvas)
        sleep(0.01)

class charging_station:
    size = 15
    color = "blue"

    queue = deque()
    
    def __init__(self,sim_env,id,x,y,charging_speed=0.2) -> None:
        self.id = id
        self.curr_x = x
        self.curr_y= y
        self.charging_speed = charging_speed
        self.sim_env = sim_env
    
    def render(self,canvas):
        canvas.create_oval(self.curr_x-self.size/2,self.curr_y-self.size/2,self.curr_x+self.size/2,self.curr_y+self.size/2,fill=self.color)


    def getQueueLength(self):
        return len(self.queue)

    def getWaitingTime(self):
        charge = 0
        for taxi in self.queue:
            charge+=MAX_BATTERY-taxi.getBattery()
        
        return charge/self.charging_speed

    def addTaxi(self,taxi):
        self.queue.appendleft(taxi)

    def charge(self)->None:
        if(len(self.queue)>0):
            if(self.queue[0].getCharged(self.charging_speed)):
                self.queue.popleft().finishCharging()




class Taxi(object):
    size = 10
    color = "yellow"

    wait_color = "green"
    wait_size = 5
    pass_size = 4
    pass_color = 'red'
    id = 0
    assigned_region = 0
    occupied =False
    going_to_charger=False
    #curr_speed = 10
    #add return to region
    states = ['wait','charging','goingcharge','driving pass','going to pass']
    state = 0

    best_charger = 0
    closest_user = 0


    dest_charger_index = 0

    battery=20

    consumption =0.01
    def __init__(self,sim_env,id,assigned_region) -> None:
        
        self.dest_x=0.0
        self.dest_y=0.0

        self.curr_x=0.0
        self.curr_y=0.0
        
        self.id = id
        self.assigned_region = assigned_region
        self.sim_env = sim_env
        self.passenger = None
        self.moving_speed=1
        pass

    def init_position(self, region):
        self.curr_x = random()*MAP_WIDTH
        self.curr_y = random()*MAP_HEIGHT

    def getCharged(self,charging_speed)->bool:
        self.battery = max(MAX_BATTERY,self.battery+ charging_speed)            
        if(abs(self.battery-MAX_BATTERY)<0.1):
            self.state = 0
        return abs(self.battery-MAX_BATTERY)<0.01
    
    def render(self,canvas):
        canvas.create_oval(self.curr_x-self.size/2,self.curr_y-self.size/2,self.curr_x+self.size/2,self.curr_y+self.size/2,fill=self.color)
        canvas.create_text(self.curr_x,self.curr_y-10,text=f"{self.battery:3.0f}")
        if(self.state==3):
            canvas.create_oval(self.curr_x-self.pass_size/2,self.curr_y-self.pass_size/2,self.curr_x+self.pass_size/2,self.curr_y+self.pass_size/2,fill=self.pass_color)
        if(self.state==0):
            canvas.create_oval(self.dest_x-self.size/2,self.dest_y-self.size/2,self.dest_x+self.size/2,self.dest_y+self.size/2,fill=self.wait_color)


    def get_battery(self)->int:
        return self.battery
    def getId(self):
        return self.id
    def goTo(self):
        del_x = self.dest_x - self.curr_x
        del_y = self.dest_y - self.curr_y

        angle = math.atan2(del_y,del_x)
        
        self.curr_x += math.cos(angle)*self.moving_speed
        self.curr_y += math.sin(angle)*self.moving_speed

    #def pickup(self):

    def generateLocation(self):
        return MAP_WIDTH*random(),MAP_HEIGHT*random()

    def finishCharging(self):
        state = 0

    def decideToCharge(self):
        if(self.battery<15):
            return True
        
        if(self.sim_env.getWaitingUsers()<3 and self.battery<15):
            return True
        
        return False
    
    #TODO: Make speed dependent on region
    #def getg

    #TODO Add regions
    def move(self):
        #best_charger=0
        if self.state != 1:
            self.goTo()
            self.battery -= self.consumption
            if math.dist([self.curr_x,self.curr_y], [self.dest_x,self.dest_y])<self.moving_speed/2:
                match (self.state):
                    case 0:
                        self.curr_x,self.curr_y = self.dest_x,self.dest_y
                        self.dest_x,self.dest_y = self.generateLocation()
                        print("New Wait Spot")
                    case 2: #arrived at charger
                        #charging_stations = self.sim_env.get

                        self.sim_env.getChargingStation(self.best_charger).addTaxi(self)
                        self.curr_x,self.curr_y = self.dest_x,self.dest_y
                        self.state = 1
                        print("Arrived At charger")

                    case 3: #arriving at passenger destination
                        self.sim_env.userDroppedOff(self.passenger.getId())
                        self.passenger.dropOff()
                        #record journey stats
                        self.curr_x,self.curr_y = self.dest_x,self.dest_y
                        self.state = 0
                        print("Arrived At destination")

                    case 4: #pick up pass
                        
                        self.passenger = self.sim_env.getUser(self.closest_user)
                        self.passenger.getOnTaxi(self)
                        
                        self.curr_x,self.curr_y = self.dest_x,self.dest_y
                        self.dest_x,self.dest_y = self.passenger.dest_x,self.passenger.dest_y
                        self.state = 3
                        print("Picked up passenger")


        if(self.state==0): 
            if self.decideToCharge():

                best_cost=10000
                best_charger=0
                i=0
                charging_stations = self.sim_env.getChargingStations()
                for c in self.sim_env.charging_stations:
                    waiting_time = c.getWaitingTime()
                    charging_time = (MAX_BATTERY-self.battery)/c.charging_speed
                    #TODO: Make speed dependent on region
                    #calculate time to get to charger
                    moving_time = math.dist([self.curr_x, self.curr_y],[c.curr_x, c.curr_y])/self.moving_speed
                    #todo (maybe)
                    cost = waiting_time+charging_time + moving_time
                    if(cost<best_cost):
                        best_cost = cost
                        best_charger = i
                    #pick
                    i+=1

                self.dest_x = charging_stations[best_charger].curr_x
                self.dest_y = charging_stations[best_charger].curr_y
                self.dest_charger = best_charger
                print("going to charger")
                #self.going_to_charger=True
                self.state = 2


                self.goTo()
            else: 
                #move to best area
                #check customer list for distance between customer and taxi
                users = self.sim_env.users
                closest_distance = CLOSEST_DISTANCE
                min_dist_to_taxi = MIN_DIST_TO_TAXI
                closest_index=0
                i=0
                if(len(users)>0):
                    for u in users:
                        if u.isAck()==False:
                            distance_to_u = math.dist([self.curr_x, self.curr_y],[u.start_x, u.start_y])

                            if(distance_to_u<closest_distance):
                                closest_distance = distance_to_u
                                closest_index = i
                                # print(distance_to_u)
                        i=i+1    
                    user_id = self.sim_env.getUser(closest_index).getId()
                    closest_user = self.sim_env.getUserById(user_id)

                    if(closest_distance<min_dist_to_taxi):
                        #go to user
                        users
                        self.dest_x = closest_user.start_x
                        self.dest_y = closest_user.start_y                    #calculate time to get to charger
                        closest_user.ackUser()
                        print("going to passenger")
                        self.state = 4

                        #on the user side, set to picked up and record start time
                        self.goTo()

                
    
class User:
    id=0

    start_x=0
    start_y = 0
    
    dest_x=0
    dest_y=0

    init_time =0
    pickup_time=0

    size = 5
    color = "red"

    def __init__(self,sim_env,id,init_time):
        self.id = id
        self.ack = False
        self.my_taxi=None
        self.ack = False
        self.sim_env = sim_env
        
        self.init_time = init_time
        
        # self.start_x,self.start_y =100,100
        # self.dest_x, self.dest_y = 400,100

        self.start_x,self.start_y =self.generateLocation()
        self.dest_x, self.dest_y = self.generateLocation()
        # print(f"start: {self.start_x}, {self.start_y}")
        # print(f"dest: {self.dest_x}, {self.dest_y}")

        self.init_time
    
    def getOnTaxi(self,taxi):
        self.my_taxi = taxi
        self.pickup_time = self.sim_env.getTime()

    def getId(self):
        return self.id

    def ackUser(self):
        print(f"{self.id} blegh")
        self.ack = True

    def isAck(self):
        return self.ack

    def generateLocation(self):
        return MAP_WIDTH*random(),MAP_HEIGHT*random()

    def dropOff(self):
        #picked up = false
        print("dropped")
        self.my_taxi = None
        wait_time = self.pickup_time - self.init_time
        travel_time = self.sim_env.getTime()-self.pickup_time

    def isPassenger(self)->bool:
        return self.my_taxi != None
    
    def render(self,canvas):
        canvas.create_oval(self.dest_x-self.size/2,self.dest_y-self.size/2,self.dest_x+self.size/2,self.dest_y+self.size/2,fill="pink")
        canvas.create_oval(self.start_x-self.size/2,self.start_y-self.size/2,self.start_x+self.size/2,self.start_y+self.size/2,fill="black")

        # if(self.isPassenger()==True):
        #     canvas.create_oval(self.my_taxi.curr_x-self.size/2,self.my_taxi.curr_y-self.size/2,self.my_taxi.curr_x+self.size/2,self.my_taxi.curr_y+self.size/2,fill=self.color)



env = Sim_env(NUM_TAXIS)


while True:
    # if(env.getTime() % 100 ==0):
    #     env.printSystemState()
    env.simloop()
    env.passTime()
