from google.transit import gtfs_realtime_pb2
import protobuf_to_dict
import time
import requests
import json
import tkinter as tk

JZ_API="https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz"  # J,Z trains API endpoint
M_API="https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm" # M train API endpoint
app = tk.Tk()                                                                   # Tkinter application init

def closest_trains(lines, station, num=3):
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
                        train_data["direction"] = stop["stop_id"][len(station):]
                        if train_data["time_to_arrival"] > 0:
                            ret.append(train_data)

    ret = sorted(ret, key=lambda t: t["time_to_arrival"])
    return ret[:num-1]

def get_screen_dimensions():
    return {"width": app.winfo_screenwidth(), "height": app.winfo_screenheight()}

def create_labels(trains, screen):
    num_trains = len(trains)
    for train in trains:
        entry = tk.Label(text="{} : {} minutes".format(train["train"], int(train["time_to_arrival"] / 60)),
                        background="#cbcfca", width=screen["width"], height=5)#int(screen["height"]/num_trains))
        entry.pack()

def display_trains(train_list, direction, line=None):
    """
    1. Get number of trains [n] going in the direction we want (N/S) that match the line we want (if line == None then ignore)
    2. Get screen dimensions (height [h] most important*)
    3. Split screen into [x] number of rows so that each row is at least MIN_HEIGHT
    4. Row will display:
        TRAIN LETTER / ICON | MINUTES TO ARRIVAL
    """
    trains = [t for t in train_list if t["direction"] == direction and line == None or t["train"] == line]
    num_train = len(trains)
    screen = get_screen_dimensions()
    create_labels(trains, screen)
    app.mainloop()

def main():
    feed = {}
    subway_data = {}
    rt_data = {}

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
    print(closest_trains(rt_data.values(), 'M11', 15))
    display_trains(closest_trains(rt_data.values(), 'M11', 15), 'S')

if __name__ == '__main__':
    main()
