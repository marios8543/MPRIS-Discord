print("MPRIS-compatible Discord Rich Presence by marios8543 \n")

from mpris2 import get_players_uri,Player
from dbus.mainloop.glib import DBusGMainLoop
import dbus
import pypresence
from time import sleep

dbus_loop = DBusGMainLoop()
bus = dbus.SystemBus(mainloop=dbus_loop)

rpc = pypresence.Presence("508273804720734209")
def rpc_connect():
    while True:
        try:
            rpc.connect()
        except Exception:
            print("Discord RPC failed to connect. Retrying after 5 seconds")
            sleep(5)
        else:
            break
rpc_connect()

player_assets = ['amarok','kodi','smplayer','spotify']
player_statuses = ['playing','paused']
current = {"status":"","title":"","artist":"","album":"","player":"player"}

def get_active_player():
    plids = reversed(list(get_players_uri()))
    player = None
    ps = None
    for i in list(plids):
        p = Player(dbus_interface_info={'dbus_uri':i})
        try:
            ps = p.PlaybackStatus
        except Exception as e:
            print(str(e))
            continue
        else:
            if ps == "Playing" or ps == "Paused":
                player = p
                if i.lower().split(".")[-1] in player_assets:
                    current['player'] = i.lower().split(".")[-1]
                else:
                    current['player'] = 'player'
                break
    return player

def update_track(p):
    if not p:
        return 0
    meta = p.Metadata
    updated = 0
    if str(meta['xesam:title'])!=current['title']:
        updated+=1
        current['title'] = str(meta['xesam:title'])
    if str(meta['xesam:artist'][0])!=current['artist']:
        updated+=1
        current['artist'] = str(meta['xesam:artist'][0])
    if str(meta['xesam:album'])!=current['album']:
        updated+=1
        current['album'] = str(meta['xesam:album'])
    if (p.PlaybackStatus).lower() != current['status']:
        updated+=1
        current['status'] = (p.PlaybackStatus).lower()
    return updated

def update_presence():
    p = get_active_player()
    u = update_track(p)
    if current['status'] not in player_statuses:
        current['status'] = 'unknown'
    if u>0:
        try:
            rpc.update(
                details="{} - {}".format(current['artist'],current['title']),
                state=current['album'],
                large_image=current['player'],
                small_image=current['status'],
                small_text=current['status'].capitalize(),
                large_text=current['player'].capitalize()
                )
        except Exception:
            rpc_connect()
    sleep(5)

update_presence()
while True:
    update_presence()
