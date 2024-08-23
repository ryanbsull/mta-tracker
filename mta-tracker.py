from google.transit import gtfs_realtime_pb2
import protobuf_to_dict
import time
import requests
import json

feed = {}
subway_data = {}
rt_data = {}
JZ_API="https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz"
M_API="https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm"

with open('stations.json', 'r') as f:
    station_data = json.load(f)

feed["JZ"] = gtfs_realtime_pb2.FeedMessage()
feed["M"] = gtfs_realtime_pb2.FeedMessage()
feed["JZ"].ParseFromString(requests.get(JZ_API).content)
feed["M"].ParseFromString(requests.get(M_API).content)

subway_data["JZ"] = protobuf_to_dict.protobuf_to_dict(feed["JZ"])
subway_data["M"] = protobuf_to_dict.protobuf_to_dict(feed["M"])
rt_data["JZ"] = subway_data["JZ"]["entity"]
rt_data["M"] = subway_data["M"]["entity"]

def closest_trains(lines, station, num=5):
    ret = []
    current_time = int(time.time())
    for line in lines:
        for train in line:
            if "trip_update" in train and "stop_time_update" in train["trip_update"]:
                for stop in train["trip_update"]["stop_time_update"]:
                    if station in stop["stop_id"]:
                        arrival_time = stop["arrival"]["time"]
                        train_data = {}
                        train_data["train"] = train["trip_update"]["trip"]["route_id"]
                        train_data["time_to_arrival"] = int(arrival_time - current_time)
                        train_data["arrival"] = time.strftime("%I:%M %p", time.localtime(arrival_time))
                        if train_data["time_to_arrival"] > 0:
                            ret.append(train_data)

    ret = sorted(ret, key=lambda t: t["time_to_arrival"])
    return ret[:num-1]

print(closest_trains(rt_data.values(), 'M11'))
