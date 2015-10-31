#Author Dylan Rush
#data created Oct 30 2015
#weighted queue test



import operator
import random

#we need to import the list of songs for testing

f = open('songs.txt','r')

songlist = []
#add song to the list of songs
for line in f:
    line = line.strip('\n')
    temp_list = line.split(',')


    song ={
        "name": temp_list[0],
        "artist":temp_list[1],
        "length":temp_list[2],

    }

    songlist.append(song)

#now we need to make a queue with activities for the party

activity_queue = []
for i in range(1,400):
    #generate a random number for what song to choose
    num = random.randint(1,len(songlist)-1)

    entry = {
        'name' : songlist[num]['name'],
        'artist' : songlist[num]['artist'],
        'duration' : songlist[num]['length'],
        'date_sub' : random.randint(1,50000),

    }
    activity_queue.append(entry)

sorted_activity_queue = sorted(activity_queue,key = operator.itemgetter('name','date_sub'))
#print the current activity queue
for a in sorted_activity_queue:
    print a["name"],a['date_sub']


#One of them is the maximum time between votes to be considered consecutive
max_time_apart = 5000 #this is in seconds

#this one is for the time frame before the end of the current song
max_before_start = 2000 #this is in miliseconds
#this is the threshold minimum number of consecutive songs
min_consect_songs = 3
#variable to keep track of the total number of consecutive songs
consect_songs = 0
#for the consecutive songs the buff is .1 %
consect_buff = 1.001

#for the before the end of the current song buff its .5%
before_buff = 1.005

dummy_entry ={
    'name' :'',
    'artist' :'',
    'duration' :'',
    'date_sub' : 0,
}
queue = []

def find_index(dicts, key, value):
    class Null: pass
    for i, d in enumerate(dicts):
        if d.get(key, Null) == value:
            return i


for entry in sorted_activity_queue:
    if not any(d['name'] == entry['name'] for d in queue):
        consect_songs = 0
        pre_entry = dummy_entry
        song_pos = {
            'name' : entry['name'],
            'weight' : 1,
        }
        queue.append(song_pos)
        pos = queue.index(song_pos)
    else:
        pos = find_index(queue,'name',entry['name'])


        if consect_songs > min_consect_songs:
                  queue[pos]["weight"] *= consect_buff
        if (entry['date_sub'] - pre_entry['date_sub']) < max_time_apart:
                  consect_songs += 1
        else:
                  consect_songs = 0
        if entry['date_sub'] - 500000 < max_before_start:
                  queue[pos]['weight'] *= before_buff
        pre_entry = entry





sorted_queue = sorted(queue, key = operator.itemgetter('weight'))

for songs in sorted_queue:
    print songs['name'],songs['weight']
