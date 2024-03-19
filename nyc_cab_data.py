import pyarrow.parquet as pq
import pandas as pd
import numpy as np
from datetime import datetime as dt
import matplotlib.pyplot as plt



trips = pq.read_table('yellow_tripdata_2023-01.parquet')
trips = trips.to_pandas()
trips = trips[['PULocationID','DOLocationID','tpep_pickup_datetime']]

manhattan_regions = pd.read_csv('taxi_zone_lookup.csv')[['LocationID','Borough']]
manhattan_regions= manhattan_regions.loc[manhattan_regions['Borough'] == 'Manhattan']

mapped_regions= pd.read_csv('RegionMapping.csv')
mapped_regions['Taxi Zones']


trips = trips.loc[trips['PULocationID'].isin(mapped_regions['Taxi Zones']) & trips['DOLocationID'].isin(mapped_regions['Taxi Zones'])]


print(trips.head(100000))
# counts = np.zeros((24,1))
# labels = range(24)
trips['tpep_pickup_datetime'] = trips['tpep_pickup_datetime'].dt.hour
def gen_user(i):
	
	return trips.iloc[i]['PULocationID'],trips.iloc[i]['DOLocationID']
# print(trips.head)
# for time in trips['tpep_pickup_datetime']:
#     counts[time]+=1
# fig,ax = plt.subplots()
# ax.plot(counts)
# ax.title("Number of ta")
# plt.show()
# # for a in [1,5,10,20]:
# #     print(f"\n{trips['PULocationID'][a]} {trips['DOLocationID'][a}")



