import sys
import pandas as pd
import pylast
import numpy as np
import time
from common import utils

arg = sys.argv[1]
print(arg[::-1])

def parse_track_json(track_dict, a_track):

    try:
        track_dict["playback_date"].append(a_track.playback_date)
    except:
        track_dict["playback_date"].append(np.nan)
    try:
        track_dict["unix_timestamp"].append(a_track.timestamp)
    except:
        track_dict["unix_timestamp"].append(np.nan)
    try:
        track_dict["title"].append(a_track.track.title)
    except:
        track_dict["title"].append(np.nan)
    try:
        track_dict["artist"].append(str(a_track.track.artist))
    except:
        track_dict["artist"].append(np.nan)
    try:
        track_dict["album"].append(a_track.album)
    except:
        track_dict["album"].append(np.nan)
    try:
        track_dict["duration"].append(a_track.track.get_duration())
    except:
        track_dict["duration"].append(np.nan)

    return(track_dict)

def query_track_data(config_path):

    config_dict = utils.read_yaml("common/config.yaml")

    username = config_dict["pylast"]["credentials"]["username"]
    password = config_dict["pylast"]["credentials"]["password"]
    api_key = config_dict["pylast"]["credentials"]["api_key"]
    api_secret = config_dict["pylast"]["credentials"]["api_secret"]

    start_date = config_dict["pylast"]["params"]["start_date"]
    end_date = config_dict["pylast"]["params"]["end_date"]
    print(start_date)
    print(end_date)

    track_logs_file = config_dict["file_output"]["track_logs_file"]

    password_hash = pylast.md5(password)

    network = pylast.LastFMNetwork(api_key=api_key, api_secret=api_secret, username=username, password_hash=password_hash)
    user = network.get_authenticated_user()

    start_date = utils.str_to_date(start_date)
    end_date = utils.str_to_date(end_date)

    unixtime_start = time.mktime(start_date.timetuple())
    unixtime_end = time.mktime(end_date.timetuple())

    print("Getting recent tracks, this might take some time")
    tracks = user.get_recent_tracks(time_from=unixtime_start, time_to=unixtime_end, limit=None, cacheable=True)

    track_dict = {}
    track_dict["playback_date"] = []
    track_dict["unix_timestamp"] = []
    track_dict["title"] = []
    track_dict["artist"] = []
    track_dict["album"] = []
    track_dict["duration"] = []

    amount_of_tracks = len(tracks)
    print("Getting {0} tracks".format(amount_of_tracks))
    counter = 100
    for index, a_track in enumerate(tracks):
        if counter == index:
            print("Got {0}/{1}".format(counter, amount_of_tracks))
            counter = counter + 100
        track_dict = parse_track_json(track_dict, a_track)

    df = pd.DataFrame.from_dict(track_dict)

    print("Writing to {0}".format(track_logs_file))
    df.to_csv(track_logs_file, index=False)

    return(df)

if __name__== "__main__":
  query_track_data(arg)
