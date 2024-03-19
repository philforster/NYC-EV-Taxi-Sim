#from taxi import Taxi
#import charging_station
#import user
from collections import deque
from random import random, seed
import tkinter
import numpy as np
import math
import time
from datetime import datetime
import os

MAX_BATTERY = 100
MAP_WIDTH = 225
MAP_HEIGHT = 1000

SIM_WIDTH = 4.44
SIM_HEIGHT = 14.11

NUM_GRID_X = 5
NUM_GRID_Y = 15

BLOCK_WIDTH = SIM_WIDTH/NUM_GRID_X
BLOCK_HEIGHT = SIM_HEIGHT/NUM_GRID_Y

X_RENDER_RATIO = MAP_WIDTH/SIM_WIDTH
Y_RENDER_RATIO = MAP_HEIGHT/SIM_HEIGHT

OUTPUT_FOLDER = "out"

CLOSEST_DISTANCE = 10000
MIN_DIST_TO_TAXI =0.1
NUM_TAXIS = 13587
NUM_CHARGERS=10
USER_PROB = 1
RENDER = False

TICK_TIME_SEC = 15
SPEED = 30#speed in kph

TICK_TIME_HOUR = TICK_TIME_SEC/3600
NOMINAL_SPEED = TICK_TIME_HOUR*SPEED #distance travelled in one tick at 30kph

TOTAL_TIME = 1
TOTAL_TICS = TOTAL_TIME*3600/TICK_TIME_SEC

CONSUMPTION =187.0 #wh perkm
AVE_RANGE = 377 #KM
BATTERY_CAPACITY = 71200 #Wh
MAX_BATTERY = BATTERY_CAPACITY
LEVEL2_CHARGER = 19000 #W
DCDC_CHARGER = 350000 #W

INIT_BATTERY_COEF = 0.4
CITY = "Manhattan, NY"

class Sim_env:
    
    taxis = []
    time = 0
    users = []
    users_data =[]
    taxis_data=[]
    chargers_data = []
    num_users=0
    charging_stations = []
    init_users=1

    def __init__(self,num_taxis=1,render =True,sim_time=10000,sim_number = 1):
        seed(1)
        self.start_time = time.time()

        self.sim_number = sim_number
        self.renderSim = render
        self.sim_time = sim_time
        if(render==True):
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
      self.taxis.append(Taxi(self,len(self.taxis)+1,math.floor(random()*NUM_GRID_X*NUM_GRID_Y)))
    
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
        self.placeRandomChargers(num_chargers=NUM_CHARGERS)
    #    self.charging_stations.append(charging_station(self,3,100,50,charging_speed=2))

    def placeRandomChargers(self,num_chargers=2):
        for i in range(num_chargers):
            self.charging_stations.append(charging_station(self,i,random()*SIM_WIDTH,random()*SIM_HEIGHT))
        

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

    def passTime(self):
       self.time +=1

    def getTime(self):
        return self.time
    
    def getUserById(self,id):
        for user in self.users:
            if user.id==id:
                return user
        return None
    
    def record_user(self,id,wait_time,travel_time,distance_travelled,start_region,end_region):
        user_data = [id,wait_time,travel_time,distance_travelled,start_region,end_region]
        self.users_data.append(user_data)


    def record_taxis(self):
        for taxi in self.taxis:
            self.taxis_data.append(taxi.get_stats())

    def record_chargers(self):
        for charger in self.charging_stations:
            self.chargers_data.append(charger.get_stats())

    def record_stats(self):
        #generate customer waitTime
        self.record_taxis()
        self.record_chargers()

        
        #generate file
        lines = []
        lines.append(f"Sim Number {self.sim_number}")
        lines.append(f"City: {CITY} size:{SIM_WIDTH}x{SIM_HEIGHT}")
        lines.append(f"Battery Capacity: {BATTERY_CAPACITY}WH, Car Consumption: {CONSUMPTION}WH/km, Average Vehicle Speed: {SPEED}")
        lines.append(f"Number of Taxis: {NUM_TAXIS}, Number of Charging Stations: {NUM_CHARGERS}")
        lines.append(f"User generation probability: {USER_PROB}")
        lines.append(f"Simulation duration: {(time.time()-self.start_time)}s")
        lines.append("\n\n")

        #aggregate customer data
        lines.append(f"Customer Aggregate data:")
        ave_wait = 0
        ave_trav = 0
        ave_dist = 0

        for user_data in self.users_data:
            ave_wait += user_data[2]
            ave_trav += user_data[3]
            ave_dist += user_data[4]
        
        ave_wait = ave_wait/self.num_users
        ave_trav = ave_trav/self.num_users
        ave_dist = ave_dist/self.num_users

        lines.append(f"Number of Customers served: {self.num_users}")
        lines.append(f"\nAverage Waiting Time: {ave_wait} Average Travel Time: {ave_trav} Average Distance Travelled: {ave_dist}")

        lines.append("\nTaxi Aggregate Data\n")
        taxi_averages = np.array([0.0]*13)
        num_died =0
        for taxi_data in self.taxis_data:
            if taxi_data[2]==True:
                num_died+=1
            for i in range(3,len(taxi_data)):
                taxi_averages[i-3] += taxi_data[i]
        
        taxi_averages = taxi_averages/NUM_TAXIS

        taxi_stat_desc = ["Customers Served","Time At Charger","Time Spent Charging",
                           "Distance Looking For Customers","Distance Charging (Should be 0)","Distance Driving to Charger",
                           "Distance Driving Passengers to Destination","Distance Driving to Passengers",
                           "Time Looking For Customers","Time Charging (Should be 0)","Time Driving to Charger",
                           "Time Driving Passengers to Destination","Time Driving to Passengers"]
        
        for i in range(len(taxi_averages)):
            lines.append(f"Average {taxi_stat_desc[i]}: {taxi_averages[i]}")

        lines.append(f"Number of Taxis that Died: {num_died}")

        lines.append(f"\nCharging Station Aggregate_data\n") 
        charger_positions = []
        charger_averages = np.array([0.0]*4)
        for charger_data in self.chargers_data:
            charger_positions.append((charger_data[1],charger_data[2]))
            for i in range(4,len(charger_data)):
                charger_averages[i-4]+=charger_data[i]
        charger_averages = charger_averages/NUM_CHARGERS
        charger_stat_desc = ["Charging Time", "Idle Time", "Queue Length","Arrival Rate"]

        for i in range(len(charger_averages)):
            lines.append(f"Average {charger_stat_desc[i]}: {charger_averages[i]}")
        lines.append(f"\nCharging positions:\n")
        
        for charger_position in charger_positions:
            lines.append(f"Position: {charger_position}")

        current_directory = os.path.dirname(__file__)

        now = datetime.now()
        date_time = now.strftime("%m_%d_%Y___%H_%M_%S")
        filename=f"Simulation{self.sim_number}_{date_time}.txt"
       
        path = os.path.join(current_directory,OUTPUT_FOLDER)
        
        os.makedirs(path, exist_ok=True)
        path = os.path.join(path,filename)
        #save into file
        print(f"File path:--{path}--")  # Debug: Print the file path to verify its value

        with open(path, "w") as txt_file:
            for line in lines:
                txt_file.write(line+ "\n") # works with any number of elements in a line

    def simloop(self):
        
        #charge all first taxis in charging stations
        for charger in self.charging_stations:
            charger.charge()

        #move all taxis
        for taxi in self.taxis:
            taxi.move()
        
            #stochastically create users
        if(random()<USER_PROB):
            for i in range(50):
                self.createUser(self)
        if(self.renderSim==True):
            self.render(self.myCanvas)
            #sleep(0.01)

class charging_station:
    size = 15
    color = "blue"

    queue = deque()
    
    ave_q_length = 0.0
    charging_time=0
    waiting_time = 0
    arrival_rate = 0.0

    def __init__(self,sim_env,id,x,y,charging_speed=LEVEL2_CHARGER) -> None:
        self.id = id
        self.curr_x = x
        self.curr_y= y
        self.charging_speed = charging_speed
        self.sim_env = sim_env
    
    def render(self,canvas):
        canvas.create_oval(self.curr_x*X_RENDER_RATIO-self.size/2,self.curr_y*Y_RENDER_RATIO-self.size/2,self.curr_x*X_RENDER_RATIO+self.size/2,self.curr_y*Y_RENDER_RATIO+self.size/2,fill=self.color)


    def getQueueLength(self):
        return len(self.queue)

    def getWaitingTime(self):
        charge = 0
        for taxi in self.queue:
            charge+=MAX_BATTERY-taxi.get_battery()
        
        return charge/self.charging_speed

    def get_stats(self):
        return [self.id,self.curr_x,self.curr_y,self.charging_speed,self.charging_time,self.waiting_time,self.ave_q_length,self.arrival_rate]

    def addTaxi(self,taxi):
        self.arrival_rate+=1/TOTAL_TICS*TICK_TIME_HOUR
        self.queue.appendleft(taxi)

    def charge(self)->None:
        if(len(self.queue)>0):
            self.ave_q_length+=(len(self.queue)-1)/TOTAL_TICS
            self.charging_time+=1
            if(self.queue[0].getCharged(self.charging_speed)):
                self.queue.popleft().finishCharging()
        else:
            self.waiting_time+=1

        


    def get_stats(self):
        return [id,self.charging_time,self.waiting_time]




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
    distance_stats=[0,0,0,0,0]

    time_stats=[0,0,0,0,0]
    died=False
    served_customers = 0
    time_spent_charging=0
    time_at_charger =0


    dest_charger_index = 0

    charge_wait_start = 0
    charge_wait_end = 0

    user_wait_times=[]
    user_travel_times=[]

    taxi_charging_times=[]

    consumption =CONSUMPTION
    def __init__(self,sim_env,id,assigned_region) -> None:
        
        self.dest_x=0.0
        self.dest_y=0.0

        self.curr_x=0.0
        self.curr_y=0.0

        self.closest_user=-1
        self.id = id
        self.assigned_region = assigned_region
        self.sim_env = sim_env
        self.passenger = None
        self.moving_speed=NOMINAL_SPEED
        self.battery=BATTERY_CAPACITY*random()*INIT_BATTERY_COEF

        self.init_position()
        pass

    def init_position(self, start_region=1,end_region=5):
        self.curr_x =  (random()+start_region%NUM_GRID_X)*BLOCK_WIDTH
        self.curr_y = (random()+start_region//NUM_GRID_X)*BLOCK_HEIGHT 

        self.dest_x = (random()+end_region%NUM_GRID_X)*BLOCK_WIDTH
        self.dest_y = (random()+end_region//NUM_GRID_X)*BLOCK_HEIGHT 

    def getCharged(self,charging_speed)->bool:
        self.time_spent_charging+=1
        self.battery = min(MAX_BATTERY,self.battery+ charging_speed*TICK_TIME_HOUR)            
        if(abs(self.battery-MAX_BATTERY)<0.1):
            self.state = 0
            self.charge_wait_end=self.sim_env.getTime()
            self.time_at_charger+=self.charge_wait_end-self.charge_wait_start
        return abs(self.battery-MAX_BATTERY)<0.01
    
    def render(self,canvas):
        canvas.create_oval(self.curr_x*X_RENDER_RATIO-self.size/2,self.curr_y*Y_RENDER_RATIO-self.size/2,self.curr_x*X_RENDER_RATIO+self.size/2,self.curr_y*Y_RENDER_RATIO+self.size/2,fill=self.color)
        if(self.state==3):
            canvas.create_text(self.curr_x*X_RENDER_RATIO,self.curr_y*Y_RENDER_RATIO-10,text=f"{self.passenger.getId()}")
        # if(self.state==3):
        #     canvas.create_oval(self.curr_x-self.pass_size/2,self.curr_y-self.pass_size/2,self.curr_x+self.pass_size/2,self.curr_y+self.pass_size/2,fill=self.pass_color)
        if(self.state==0):
            canvas.create_oval(self.dest_x*X_RENDER_RATIO-self.size/2,self.dest_y*Y_RENDER_RATIO-self.size/2,self.dest_x*X_RENDER_RATIO+self.size/2,self.dest_y*Y_RENDER_RATIO+self.size/2,fill=self.wait_color)

    def get_stats(self):
        stats =  [self.id,self.assigned_region,self.died,self.served_customers,self.time_at_charger,self.time_spent_charging]
        for distance in self.distance_stats:
            stats.append(distance)
        for time in self.time_stats:
            stats.append(time)
        return stats

    
    def get_battery(self)->int:
        return self.battery
    
    def getId(self):
        return self.id
    
    def goTo(self):
        

        if(self.battery-self.consumption>=0):
            del_x = self.dest_x - self.curr_x
            del_y = self.dest_y - self.curr_y

            angle = math.atan2(del_y,del_x)
            
            self.curr_x += math.cos(angle)*self.moving_speed
            self.curr_y += math.sin(angle)*self.moving_speed
            self.distance_stats[self.state] += self.moving_speed
            self.time_stats[self.state] += 1
            self.battery -= self.consumption*self.moving_speed
        else:
            self.died=True

    #def pickup(self):

    def generateLocation(self):
        return (random()+self.assigned_region%NUM_GRID_X)*BLOCK_WIDTH,(random()+self.assigned_region//NUM_GRID_X)*BLOCK_HEIGHT

    def finishCharging(self):
        state = 0

    def decideToCharge(self):
        if(self.battery<0.3*BATTERY_CAPACITY):
            return True
        
        if(self.sim_env.getWaitingUsers()<3 and self.battery<0.15*BATTERY_CAPACITY):
            return True
        
        return False
    
    #TODO: Make speed dependent on region
    #def getg

    #TODO Add regions
    def move(self):
        #best_charger=0
        if self.state != 1:
            if math.dist([self.curr_x,self.curr_y], [self.dest_x,self.dest_y])<self.moving_speed/2:
                match (self.state):
                    case 0:
                        self.curr_x,self.curr_y = self.dest_x,self.dest_y
                        self.dest_x,self.dest_y = self.generateLocation()
                        print("New Wait Spot")
                    case 2: #arrived at charger
                        #charging_stations = self.sim_env.get
                        self.charge_wait_start=self.sim_env.getTime()
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
                        self.served_customers+=1

                        self.passenger = self.sim_env.getUserById(self.closest_user)
                        self.passenger.getOnTaxi(self)
                        
                        self.curr_x,self.curr_y = self.dest_x,self.dest_y
                        self.dest_x,self.dest_y = self.passenger.dest_x,self.passenger.dest_y
                        self.state = 3
                        print("Picked up passenger")
            self.goTo()

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


            else: 
                #move to best area
                #check customer list for distance between customer and taxi
                users = self.sim_env.users
                closest_distance = CLOSEST_DISTANCE
                min_dist_to_taxi = MIN_DIST_TO_TAXI
                closest_user=0
                if(len(users)>0):
                    for i in range(len(users)):
                        if users[i].isAck()==False:
                            distance_to_u = math.dist([self.curr_x, self.curr_y],[users[i].start_x, users[i].start_y])

                            if(distance_to_u<closest_distance):
                                closest_distance = distance_to_u
                                closest_user = i
                                # print(distance_to_u)
                        

                    if(closest_distance<min_dist_to_taxi):
                        #go to user
                        self.dest_x = users[closest_user].start_x
                        self.dest_y = users[closest_user].start_y                    #calculate time to get to charger
                        self.sim_env.getUser(closest_user).ackUser()
                        self.closest_user=self.sim_env.getUser(closest_user).getId()

                        print("going to passenger")
                        self.state = 4

                        #on the user side, set to picked up and record start time

                
    
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

    def __init__(self,sim_env,id,init_time,start_region =1,end_region = 1):
        self.id = id
        self.ack = False
        self.my_taxi=None
        self.ack = False
        self.sim_env = sim_env
        
        self.start_region = math.floor(random()*NUM_GRID_X*NUM_GRID_Y)
        self.end_region = math.floor(random()*NUM_GRID_X*NUM_GRID_Y)
        
        self.init_time = init_time
        
        # self.start_x,self.start_y =100,100
        # self.dest_x, self.dest_y = 400,100

        self.start_x,self.start_y =self.generateLocation(self.start_region)
        self.dest_x, self.dest_y = self.generateLocation(self.end_region)
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

    def generateLocation(self,region):
        return (random()+region%NUM_GRID_X)*BLOCK_WIDTH,(random()+region//NUM_GRID_X)*BLOCK_HEIGHT

    def dropOff(self):
        #picked up = false
        print("dropped")
        self.my_taxi = None
        wait_time = self.pickup_time - self.init_time
        travel_time = self.sim_env.getTime()-self.pickup_time
        distance_travelled = math.dist([self.start_x,self.start_y],[self.dest_x,self.dest_y])
        
        self.sim_env.record_user(self.id,wait_time,travel_time,distance_travelled,self.start_region,self.end_region)
        

    def isPassenger(self)->bool:
        return self.my_taxi != None
    def render(self,canvas):
        canvas.create_oval(self.dest_x*X_RENDER_RATIO-self.size/2,self.dest_y*Y_RENDER_RATIO-self.size/2,self.dest_x*X_RENDER_RATIO+self.size/2,self.dest_y*Y_RENDER_RATIO+self.size/2,fill="pink")
        canvas.create_text(self.dest_x*X_RENDER_RATIO,self.dest_y*Y_RENDER_RATIO-2*self.size,text=f"{self.id}")
        if(self.isPassenger()==True):
            canvas.create_oval(self.my_taxi.curr_x*X_RENDER_RATIO-self.size/2,self.my_taxi.curr_y*Y_RENDER_RATIO-self.size/2,self.my_taxi.curr_x*X_RENDER_RATIO+self.size/2,self.my_taxi.curr_y*Y_RENDER_RATIO+self.size/2,fill=self.color)
        else:
            canvas.create_oval(self.start_x*X_RENDER_RATIO-self.size/2,self.start_y*Y_RENDER_RATIO-self.size/2,self.start_x*X_RENDER_RATIO+self.size/2,self.start_y*Y_RENDER_RATIO+self.size/2,fill="black")
            canvas.create_text(self.start_x*X_RENDER_RATIO,self.start_y*Y_RENDER_RATIO-2*self.size,text=f"{self.id}")



env = Sim_env(NUM_TAXIS,render=RENDER,sim_time=TOTAL_TICS)


while env.getTime()<env.sim_time:
    # if(env.getTime() % 100 ==0):
    #     env.printSystemState()
    env.simloop()
    env.passTime()

env.record_stats()
