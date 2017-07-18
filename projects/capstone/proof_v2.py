#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
https://github.com/Project-OSRM/osrm-backend

wget http://download.geofabrik.de/north-america/us/massachusetts-latest.osm.pbf

# make sure to use walking profile (foot.lua) when extracting...

docker run -t -v $(pwd):/data osrm/osrm-backend osrm-extract -p /opt/foot.lua /data/massachusetts-latest.osm.pbf

docker run -t -v $(pwd):/data osrm/osrm-backend osrm-contract /data/massachusetts-latest.osrm

docker run -t -i -p 5000:5000 -v $(pwd):/data osrm/osrm-backend osrm-routed /data/massachusetts-latest.osrm
'''

# import requests
# import json
# url = "http://127.0.0.1:5000/route/v1/driving/-71.086331,42.430601;-71.074382,42.426597?steps=false"
# url = "http://127.0.0.1:5000/route/v1/driving/-71.0727793,42.4436791;-71.0721040,42.4436421?steps=true"
# url = "http://127.0.0.1:5000/route/v1/walking/-71.08459,42.443095;-71.0721040,42.4436421?steps=true"
# url = "http://127.0.0.1:5000/route/v1/driving/13.388860,52.517037;13.385983,52.496891?steps=false"
#url = "http://127.0.0.1:5000/route/v1/walking/-71.0727793,42.4436791;-71.0731084,42.4436979?steps=true"
# r = requests.get(url)
# data = r.json()
# data['routes'][0]['legs'][0]['steps']


# start_location = '-71.0721040,42.4436421'

# nodes = []
# for node in root.findall('node'):
# 	nodes.append(node.get('id'))

# this has to be a dict becuase way too slow to iterate over 10,000 values
# nodes = nodes[0:10000]

# for every node, this table will tell us next possible nodes
# relationships = {}
# for way in root.findall('way'):
# 	temp_nodes = []
# 	for nd in way.findall('nd'):
# 		temp_nodes.append(nd.get('ref'))
# 	for node in nodes: # example node is 61432827
# 		if node in temp_nodes:
# 			for el in temp_nodes:
# 				if temp_nodes.index(node) == len(temp_nodes)-1:
# 					continue
# 				else:
# 					next_node = temp_nodes[temp_nodes.index(node)+1]
# 			if len(way.findall('tag')) > 0:
# 				for tag in way.findall('tag'):
# 					if tag.get('k') in ['natural']:
# 						relationships[node+'_'+next_node] = tag.get('k')
# 					else:
# 						relationships[node+'_'+next_node] = 'no_relevant_tags'
# 			else:
# 				relationships[node+'_'+next_node] = 'no_relevant_tags'

import random
import requests
import json
import xml.etree.cElementTree as ET 
import time
import pickle
import os.path
import math

'''
filter osm to only streets / paths
put file in same directory as osmfilter tool and
use ./osmfilter <filename> --keep="highway" >streets_only.osm.
For example, if your file is called the_map.osm you put
this in the command line
./osmfilter the_map.osm --keep="highway" >streets_only.osm

below you'll need to be in the same directory where streets.osm
is located
'''



# Define file name
filename = 'streets.osm'
# filename = 'massachusetts-latest.osm.pbf'


tree = ET.parse(filename)
root = tree.getroot()


def get_geocoords(nodeid):
	''' parses osm file and returns lat lon coords
		example input = '66566291'
		example output = '-71.0727793,42.4436791' '''

	for node in root.findall(".//node[@id='"+nodeid+"']"):
		return node.get('lon') + ',' + node.get('lat')


def route_distance_between_nodes(start_coords, end_coords):
	''' node inputs are stings of longitude / latitude geo coords
		example node1 = '-71.0727793,42.4436791'
		example node2 = '-71.0721040,42.4436421' '''

	# include steps between node (just in case, probably not used)
	url = 'http://127.0.0.1:5000/route/v1/walking/{};{}?steps=true'.format(start_coords, end_coords)

	# make request to server and translate response to json
	r = requests.get(url)
	data = r.json()

	# parse distance between nodes and convert to miles
	meters = data['routes'][0]['legs'][0]['steps'][0]['distance']
	miles = meters * 0.000621371 # 1 meter is 0.000621371 miles

	return miles


def deg_2_rad(deg):
	''' Faster than calling routing service 
	    input = degrees, output = radians '''

	return (deg * math.pi) / 180


def crow_distance_between_nodes(start_coords, end_coords):
	''' node inputs are stings of longitude / latitude geo coords
		example node1 = '-71.0727793,42.4436791'
		example node2 = '-71.0721040,42.4436421' '''

	lat1 = float(start_coords.split(',')[1])
	lat2 = float(end_coords.split(',')[1])
	lon1 = float(start_coords.split(',')[0])
	lon2 = float(end_coords.split(',')[0])

	inner = math.cos(deg_2_rad(90-lat1)) * math.cos(deg_2_rad(90-lat2)) + math.sin(deg_2_rad(90-lat1)) * math.sin(deg_2_rad(90-lat2)) * math.cos(deg_2_rad(lon1-lon2))

	return math.acos(inner) * 3958.786

def get_next_nodes(current_node):
	''' Iterates through osm and finds all possible next moves
		used to produce list of next options from current point '''

	# list where all next nodes will be stored
	next_nodes = []

	# iterate through each way in the map file
	# way must be a road or trail (i.e. you can't run through a building)
	# in osm data, buildings are also captured as waypoints
	for way in root.findall('way'):
		# for each way in map file, iterate thorugh each node on that way
		for node in way.findall('nd'):
			# if the node of interest is in that way go deeper
			if node.get('ref')==current_node:
				# temp store the nodes on this way as a list
				tempway = way.findall('nd')
				# iterate through node list
				for subnode in tempway:
					# if the node during iteration is the curent node...
					if subnode.get('ref') == current_node:
						# grab it's index
						idx = tempway.index(subnode)
						# if first node in way, only take node that comes after
						if idx == 0:
							next_nodes.append(tempway[idx+1].get('ref'))
						# if not first node in way, take prior and after node
						if idx > 0 and idx < len(tempway)-1:
							next_nodes.append(tempway[idx+1].get('ref'))
							next_nodes.append(tempway[idx-1].get('ref'))
						# if last node in way, only take node prior
						if idx == len(tempway)-1:
							next_nodes.append(tempway[idx-1].get('ref'))

	return list(set(next_nodes))

def get_reward(node1, node2):
	''' Using 2 nodes, determine reward of moving between them
		if run on trail, reward + 5
		if run past natural scene (water), reward + 5
		if run past historic site, reward + 5
		http://wiki.openstreetmap.org/wiki/Key:historic '''

	reward = 0

	for way in root.findall('way'):
		tempway = way.findall('nd')
		newway = []
		for node in tempway:
			newway.append(node.get('ref'))
		if node1 in newway and node2 in newway:
			taglist = way.findall('tag')
			new_tag_list = []
			for oldtag in taglist:
				new_tag_list.append(oldtag.get('k'))
			keywords = ['natural', 'waterway', 'bicycle', 'foot', 'checkpoint', 'mountain_pass', 'historic']
			if any(word in keywords for word in new_tag_list):
				# TODO: if way has 2 things, double up reward
				# reward += 25
				reward += 0

	return reward

def choose_next_node(rval, eps, moves, Q, tmp_states):
	''' Determine next node based on explore / exploit decision
		if exploiting, use Q values to make next choice '''

	if rval < eps:
		movement = random.choice(moves)
	else:
	# pick next move that has the highest Q value
	# look at each next move and see which of them are in big Qtable
	# of the ones that are in it, pick the one with the highest Q value
		if len(Q) > 0:
			found_states = []
			for el in tmp_states:
				if el in Q.keys():
					found_states.append(el)
			movement = { k: Q[k] for k in found_states }
			# TODO: what if all values are 0?
			movement = { k for k,v in movement.iteritems() if v == max(movement.values()) }
			if len(movement) == 1:
				movement = list(movement)[0].split('_')[2]
			else:
				movement = random.choice(moves)
		else:
			movement = random.choice(moves)

	return movement

# start simulation

Q = {}

# https://stackoverflow.com/questions/82831/how-do-i-check-whether-a-file-exists-using-python

if os.path.exists('neighbors.txt'):
	with open("neighbors.txt", "rb") as f:
		neighbor_nodes = pickle.load(f)
else:
	neighbor_nodes = {}

if os.path.exists('rewards.txt'):
	with open("rewards.txt", "rb") as f:
		rewards = pickle.load(f)
else:
	rewards = {}

# if os.path.exists('distances.txt'):
# 	with open("distances.txt", "rb") as f:
# 		distances = pickle.load(f)
# else:
# 	distances = {}

distances = {}

if os.path.exists('listofcoords.txt'):
	with open("listofcoords.txt", "rb") as f:
		list_of_coords = pickle.load(f)
else:
	list_of_coords = {}

# neighbor_nodes = {}
# rewards = {}
# distances = {}
# list_of_coords = {}

# define paramters
# epsilon = 0.6 # hmm. shouldn't this decay?
gamma = 0.3
alpha = 1.0 # environment is deterministic
factor = 0.5 # hmm should this be 0.6 to err on side of longer?
target_mileage = 1.0
n_trials = 200
errors = []

start = time.time()

for trial in range(n_trials):

	print trial
	# epsilon = math.cos(0.2*trial)
	epsilon = 0.7
	print 'Epsilon: {}'.format(epsilon)

	''' Define start node, coords for 
	start location and an empty list to store traveled
	paths. If start coords not stored, call get_geocoords '''

	start_location = '66572004'
	if start_location in list_of_coords.keys():
		start_coords = list_of_coords[start_location]
	else:
		start_coords = get_geocoords(start_location)
		list_of_coords[start_location] = start_coords

	# current_location = '66572004' # stone place is the start node

	''' Define miles, initial duration, and list for
	visited locations
	Duration is low if <0.5 through target miles.
	Duration is high if >=0.5 through target miles '''

	mileage = 0
	duration = 'low'
	traveled = []
	pathed = []
	option_count_dict = {} # to adjust for dead ends

	''' Ignore information when we don't hit target
	mileage. Use temp Q for each run to do so '''

	tempQ = Q.copy()

	''' From start location, where can we go next? 
	Save next possible nodes to a list. This is used to 
	determine where to go next '''

	if start_location in neighbor_nodes.keys():
		next_options = neighbor_nodes[start_location]
	else:
		next_options = get_next_nodes(start_location)
		neighbor_nodes[start_location] = next_options

	''' Based on start location, next options, and 
	current mileage. This is used to determine where to
	go next '''

	temp_states = []
	for el in next_options:
		temp_state = '{}_{}_{}_{}'.format(start_location, None, el, duration)
		temp_states.append(temp_state)

	''' Define random value for explore / exploit decision '''

	rvalue = random.random()

	''' Choose next move '''

	initial_move = choose_next_node(rvalue, epsilon, next_options, \
		tempQ, temp_states)

	''' Update current and previous location while restating
	the path (in either direction) and state '''

	#where are you now?
	#where were you before?
	#where are you going next? 
	#how far through the run are you?

	state = '{}_{}_{}_{}'.format(start_location, None, initial_move, \
		duration)	
	path = '{}_{}'.format(start_location, initial_move)
	# pathr = '{}_{}'.format(initial_move, start_location)

	''' Add state to tempQ table if it doesn't exist '''
	if not state in tempQ.keys():
		tempQ[state] = 0

	''' Get base reward for chosen move '''

	temp_reward = get_reward(start_location, initial_move)

	''' This section determins the Q value of the moves that
	follow the one just chosen. For example if you chose A-B and
	from B you can go from B-C or B-D and the Q values are 0 and
	10 respectively... the max Q value will be 10. This will be
	used to update the Q value for our current state '''

	if initial_move in neighbor_nodes.keys():
		next_options = neighbor_nodes[initial_move]
	else:
		next_options = get_next_nodes(initial_move)
		neighbor_nodes[initial_move] = next_options

	next_states = [] # now interpret from nodes into states
	for el in next_options:
		temp_state = '{}_{}_{}_{}'.format(initial_move, start_location, el, duration)
		next_states.append(temp_state)

	if len(tempQ) > 0: # and determine max Q if it exists
		found_states = []
		for el in next_states:
			if el in Q.keys():
				found_states.append(el)
		maxQ_next = { k: Q[k] for k in found_states }
		if len(maxQ_next) > 0:
			maxQ_next = [ v for k,v in maxQ_next.iteritems() \
			if v == max(maxQ_next.values()) ][0]
		else:
			maxQ_next = 0
	else:
		maxQ_next = 0

	tempQ[state] = tempQ[state] + alpha * (temp_reward + gamma \
		* maxQ_next - tempQ[state])

	''' Add chosen path to traveled list (in both directions) '''

	traveled.append(start_location)
	traveled.append(initial_move)
	pathed.append(path)
	# pathed.append(pathr)

	''' Based on chosen move, increment mileage '''

	if start_location in list_of_coords.keys():
		start_coords = list_of_coords[start_location]
	else:
		start_coords = get_geocoords(start_location)
		list_of_coords[start_location] = start_coords

	if initial_move in list_of_coords.keys():
		current_coords = list_of_coords[initial_move]
	else:
		current_coords = get_geocoords(initial_move)
		list_of_coords[initial_move] = current_coords

	coords_path = '{}, {}'.format(start_coords, current_coords)
	coords_pathr = '{}, {}'.format(current_coords, start_coords)

	if coords_path in distances.keys():
		mileage += distances[coords_path] 
	elif coords_pathr in distances.keys():
		mileage += distances[coords_pathr]
	else:
		distance = crow_distance_between_nodes(start_coords, current_coords)
		mileage += distance
		distances[coords_path] = distance
		distances[coords_pathr] = distance

	current_location = initial_move
	previous_location = start_location

	count = 0
	while start_location != current_location:

		''' Determine duration of run at this point and
			the closest and furthest next point from the start '''

		if mileage <= factor * target_mileage:
			duration = 'low'
		else:
			duration = 'high'

		holdme = {}
		for option in next_options:
			# get geocoords of each next move
			if option in list_of_coords.keys():
				temp_coords = list_of_coords[option]
			else:
				temp_coords = get_geocoords(option)
				list_of_coords[option] = temp_coords
			# get distance from next move to start location
			temp_path = '{}_{}'.format(temp_coords, start_coords)
			if temp_path in distances.keys():
				temp_miles = distances[temp_path]
			else:
				try:
					temp_miles = route_distance_between_nodes(temp_coords, start_coords)
				except:
					errors.append('Connection Error')
					temp_miles = 0
				# '-71.0719384,42.445134' , '-71.072104,42.4436421'
			holdme[option] = temp_miles

		closest_point = min(holdme, key=holdme.get)
		furthest_point = max(holdme, key=holdme.get)

		if closest_point == furthest_point:
			closest_point = None
			furthest_point = None

		''' Based on current location, next options, and 
		current mileage. This is used to determine where to
		go next '''

		temp_states = []
		for el in next_options:
			temp_state = '{}_{}_{}_{}'.format(current_location, previous_location, el, duration)
			temp_states.append(temp_state)

		''' Define random value for explore / exploit decision '''

		rvalue = random.random()

		''' Choose next move '''

		next_move = choose_next_node(rvalue, epsilon, next_options, \
			tempQ, temp_states)

		''' Update current and previous location while restating
		the path (in either direction) and state '''

		state = '{}_{}_{}_{}'.format(current_location, previous_location, next_move, \
			duration)	
		path = '{}_{}'.format(current_location, next_move)
		# pathr = '{}_{}'.format(next_move, current_location)

		''' Add state to tempQ table if it doesn't exist '''
		if not state in tempQ.keys():
			tempQ[state] = 0

		''' Get base reward for chosen move '''

		temp_reward = get_reward(current_location, next_move)

		''' Get adjusted reward if retracing steps '''

		state_parts = state.split('_')
		if state_parts[1] == state_parts[2]:
			temp_reward -= 75 # dont go back to where you just were
		#elif '{}_{}'.format(state_parts[0], state_parts[2]) in pathed:
		#	temp_reward -= 50 

		previous_location = current_location
		current_location = next_move

		if duration == 'low':
			if current_location == furthest_point and current_location != closest_point:
				temp_reward += 25
		if duration == 'high':
			if current_location == closest_point and current_location != furthest_point:
				temp_reward += 150 # prevents us from getting 'stuck'

		''' This section determins the Q value of the moves that
		follow the one just chosen. For example if you chose A-B and
		from B you can go from B-C or B-D and the Q values are 0 and
		10 respectively... the max Q value will be 10. This will be
		used to update the Q value for our current state '''

		if current_location in neighbor_nodes.keys():
			next_options = neighbor_nodes[current_location]
		else:
			next_options = get_next_nodes(current_location)
			neighbor_nodes[current_location] = next_options

		next_states = [] # now interpret from nodes into states
		for el in next_options:
			temp_state = '{}_{}_{}_{}'.format(current_location, previous_location, el, duration)
			next_states.append(temp_state)

		if len(tempQ) > 0: # and determine max Q if it exists
			found_states = []
			for el in next_states:
				if el in Q.keys():
					found_states.append(el)
			maxQ_next = { k: Q[k] for k in found_states }
			if len(maxQ_next) > 0:
				maxQ_next = [ v for k,v in maxQ_next.iteritems() \
				if v == max(maxQ_next.values()) ][0]
			else:
				maxQ_next = 0
		else:
			maxQ_next = 0

		tempQ[state] = tempQ[state] + alpha * (temp_reward + gamma \
			* maxQ_next - tempQ[state])

		''' Based on chosen move, increment mileage '''

		if previous_location in list_of_coords.keys():
			previous_coords = list_of_coords[previous_location]
		else:
			previous_coords = get_geocoords(previous_location)
			list_of_coords[previous_location] = previous_coords

		if current_location in list_of_coords.keys():
			current_coords = list_of_coords[current_location]
		else:
			current_coords = get_geocoords(current_location)
			list_of_coords[current_location] = current_coords

		coords_path = '{}, {}'.format(previous_coords, current_coords)
		coords_pathr = '{}, {}'.format(current_coords, previous_coords)

		if coords_path in distances.keys():
			mileage += distances[coords_path]
		elif coords_pathr in distances.keys():
			mileage += distances[coords_pathr]
		else:
			distance = crow_distance_between_nodes(previous_coords, current_coords)
			mileage += distance
			distances[coords_path] = distance
			distances[coords_pathr] = distance

		''' Add chosen path to traveled list (in both directions) '''

		traveled.append(current_location)
		''' Add paths to path list '''

		pathed.append(path)
		# pathed.append(pathr)

		''' Increment count of nodes visited '''

		if mileage > target_mileage * 1.3:
			break

		if current_location == start_location:
			break

		count += 1
		print mileage
		print 'Move location to: {}'.format(current_location)
		print 'Count: {}'.format(count)

	Q = tempQ.copy()
	# if mileage >= target_mileage - 1.0 and mileage <= target_mileage + 1.0:
	# 	print "WITHIN TRGET RANGE!!!, WITHIN TRGET RANGE!!!, WITHIN TRGET RANGE!!!, WITHIN TRGET RANGE!!!, "
	# 	Q = tempQ.copy()

	if trial % 100 == 0 and trial != 0:
		time.sleep(30) # so I don't destroy my CPU

#http://www.gpsvisualizer.com/map_input

#http://overpass-api.de/api/map?bbox=-71.1717,42.4166,-71.0246,42.4926

end = time.time()

print (end - start)/60

with open("neighbors.txt", "wb") as f2:
	pickle.dump(neighbor_nodes, f2)

with open("rewards.txt", "wb") as f2:
	pickle.dump(rewards, f2)

with open("distances.txt", "wb") as f2:
	pickle.dump(distances, f2)

with open("listofcoords.txt", "wb") as f2:
	pickle.dump(list_of_coords, f2)

final_path = []
def get_final_path(Q):
	
	duration = 'low'
	start_location = '66572004'
	previous_location = 'None'
	mileage = 0

	if start_location in list_of_coords.keys():
		start_coords = list_of_coords[start_location]
	else:
		start_coords = get_geocoords(start_location)
		list_of_coords[start_location] = start_coords

	final_path.append(start_location)
	current_location = {k:v for k,v in Q.iteritems() if k.startswith(start_location) and k.split('_')[1] == previous_location and k.endswith(duration)}
	current_location = [k for k,v in current_location.iteritems() if v==max(current_location.values())]
	current_location = current_location[0].split('_')[2]
	final_path.append(current_location)

	if current_location in list_of_coords.keys():
		current_coords = list_of_coords[current_location]
	else:
		current_coords = get_geocoords(current_location)
		list_of_coords[current_location] = current_coords	

	distance = crow_distance_between_nodes(start_coords, current_coords)

	mileage += distance

	previous_location = start_location

	count = 0
	while current_location != start_location:
		movement = {k:v for k,v in Q.iteritems() if k.startswith(current_location) and k.split('_')[1] == previous_location and k.endswith(duration)}
		movement = [k for k,v in movement.iteritems() if v==max(movement.values())]
		movement = movement[0].split('_')[2]
		final_path.append(movement)

		if movement in list_of_coords.keys():
			movement_coords = list_of_coords[movement]
		else:
			movement_coords = get_geocoords(movement)
			list_of_coords[movement] = movement_coords	

		distance = crow_distance_between_nodes(current_coords, movement_coords)		

		current_location = movement
		current_coords = movement_coords

		mileage += distance

		if mileage <= factor * target_mileage:
			duration = 'low'
		else:
			duration = 'high'

		previous_location = final_path[len(final_path)-2]

		count += 1
		if mileage > target_mileage:
			break

		print mileage
		print duration

get_final_path(Q)
print final_path

def get_final_geos(final_path):
	''' takes list of OSM nodes returns list of coordinates '''

	final_geo = []
	for el in final_path:
		if el in list_of_coords.keys():
			movement_coords = list_of_coords[el]
		else:
			movement_coords = get_geocoords(el)
			list_of_coords[el] = movement_coords	
		final_geo.append('{},{}'.format(movement_coords.split(',')[1], movement_coords.split(',')[0]))

	return final_geo

FINAL_GEO = get_final_geos(final_path)

import csv
with open ('route.csv', 'wb') as csvfile:
	routewriter = csv.writer(csvfile)
	routewriter.writerow(["LAT", "LON"])
	for el in FINAL_GEO:
		temp = el.split(',')
		routewriter.writerow([temp[0], temp[1]])

# # http://www.gpsvisualizer.com/map_input
# # https://www.darrinward.com/lat-long/?id=3060847
# https://arxiv.org/pdf/0903.4930.pdf

# crow distance good for incrementing distance between points... not for determining closest and furthestest next point

# how to plot route in r
# https://www.visualcinnamon.com/2014/03/running-paths-in-amsterdam-step-2.html
# https://www.darrinward.com/lat-long/?id=3141130

