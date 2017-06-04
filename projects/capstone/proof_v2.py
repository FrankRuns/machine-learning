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

# create a function that gives lat lon coordinates
# input = node id, returns lat lon tuple
# def get_coords(node_id):
# 	for el in root.findall(".//node[@id='"+node_id+"']"):
# 		return el.get('lat'), el.get('lon')





# build it

# 1. define several start parameters:
#	 start location, previous location = None, empty list for places you've been
# 	 start mileage = 0 and duration = low
# 2. create a temp copy of the master Q table - replace only if mileage within 'range'
# 3. determine valid moves from initial location and store to list
# 4. determine distance from start location to each valid move - this will allow algorithm to learn how to loop
# 5. generate random value to determine explore / exploit decision
# 6. if exploring, choose random move from valid moves list
# 7. if exploiting, choose move from valid moves list (A) where the next move (B) from 
#	 from move B has the highest q value
# 8. reward based on A) tag associated with that path and B) duration trade-off which 
# 	 means furthest point chosen when duration is low receives high reward
# 9. if furthest point from origin is chose in low duration state, increase reward. if
# 	 if agent returns to node it came from, decrement reward 
# 7. update temp q table with new q-value for that action (action == initial move)
# 8. increment mileage of run. 





# given a single node, how long will it take to
# A. find possible nodes from that node and
# B. the distance between each next node and the origin point and
# B. the distance between that node and each next node

# start_node = '66566291'
# start_location = '-71.0721040,42.4436421'

import random
import requests
import json
import xml.etree.cElementTree as ET 

# Define file name
filename = 'map'
# filename = 'massachusetts-latest.osm.pbf'

tree = ET.parse(filename)
root = tree.getroot()

debug = True

def get_geocoords(nodeid):
	'''
	parses osm file and returns lat lon coords
	example input = '66566291'
	example output = '-71.0727793,42.4436791'
	'''

	for node in root.findall(".//node[@id='"+nodeid+"']"):
		return node.get('lon') + ',' + node.get('lat')


def distance_between_nodes(start_coords, end_coords):
	'''
	node inputs are stings of longitude / latitude geo coords
	example node1 = '-71.0727793,42.4436791'
	example node2 = '-71.0721040,42.4436421'
	'''

	# include steps between node (just in case, probably not used)
	url = 'http://127.0.0.1:5000/route/v1/walking/{};{}?steps=true'.format(start_coords, end_coords)

	# make request to server and translate response to json
	r = requests.get(url)
	data = r.json()

	# parse distance between nodes and convert to miles
	meters = data['routes'][0]['legs'][0]['steps'][0]['distance']
	miles = meters * 0.000621371 # 1 meter is 0.000621371 miles

	return miles

def get_next_nodes(current_node):
	'''
	iterates through osm and finds all possible next moves
	used to produce list of next options from current point
	'''

	# list where all next nodes will be stored
	next_nodes = []

	# iterate through each way in the map file
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
	'''
	using 2 nodes, determine reward of moving between them
	if run on trail, reward + 5
	if run past natural scene (water), reward + 5
	if run past historic site, reward + 5
	http://wiki.openstreetmap.org/wiki/Key:historic
	'''

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
				reward += 5

	return reward


# create fake data and test the shit out of this function
# Q = {}
# for i in range(10):
# 	rvalue = random.random()
# 	epsilon = 0.6
# 	moves = random.sample(nodes,3)
# 	Q = {}
# 	tmp_states = '{}_{}_{}'.format(random.choice(nodes),random.choice(nodes),'low')
# 	result = choose_next_node(rvalue, epsilon, moves, Q, tmp_states)
# 	Q[result] = 0
# 	print Q
# 	print result

def choose_next_node(rval, eps, moves, Q, tmp_states):
	'''
	determine next node based on explore / exploit decision
	if exploiting, use Q values to make next choice
	'''
	if rval < eps:
		movement = random.choice(moves)
	else:
	# pick next move that has the highest Q value
	# look at each next move and see which of them are in big Qtable
	# of the ones that are in it, pick the one with the highest Q value
		if len(Q) > 0:
			print 'DANGER ZONE I THINK'
			found_states = []
			for el in tmp_states:
				if el in Q.keys():
					found_states.append(el)
			movement = { k: Q[k] for k in found_states }
			print 'movement first: {}'.format(movement)
			# TODO: what if all values are 0?
			movement = { k for k,v in movement.iteritems() if v == max(movement.values()) }
			print 'movement second: {}'.format(movement)
			if len(movement) == 1:
				movement = list(movement)[0].split('_')[1]
			else:
				movement = random.choice(moves)
		else:
			movement = random.choice(moves)

	return movement

# rvalue = 0.8
# epsilon = 0.6
# moves = ['66550453', '1915819596', '66566291']
# tmp_states = ['1915819599_66550453_low', '1915819599_1915819596_low', '1915819599_66566291_low']

# result = choose_next_node(rvalue, epsilon, moves, Q, tmp_states)
# Q[result] = 0
# print Q
# print result


# def add_state_to_qtable(state, qtable):
# 	'''
# 	create a function to add a state to
# 	check if state exists and if not, add
# 	it to the q-table
# 	'''

# 	# check if state exists in qtable
# 	state_exists = state in qtable.keys()

# 	# if state does not exist, add it to qtable
# 	if state_exists == False:
# 		qtable[state] = 0

# 	# return qtable
# 	return qtable


# # test get_geocoords function
# for i in range(20):
# 	test_node = random.choice(nodes)
# 	test_result = get_geocoords(test_node)
# 	test_type = type(test_result)
# 	print '{} and {} and {}'.format(test_node, test_result, test_type)

# # test get next node function
# for i in range(20):
# 	test_node = random.choice(nodes)
# 	test_result = get_next_nodes(test_node)
# 	test_type = type(test_result)
# 	print '{} and {} and {}'.format(test_node, test_result, test_type)


# start simulation

Q = {}

# define paramters
epsilon = 0.6
gamma = 0.6
alpha = 0.7
factor = 0.5
target_mileage = 2.0
n_trials = 20

for trial in range(n_trials):

	print 'NEW RUN'

	# define start node, previous node, and empty list to store traveled paths
	start_location = '66566291' 
	start_coords = get_geocoords(start_location)
	current_location = '66566291' # stone place # this is the start node
	traveled = []

	# define miles and initial duration
	mileage = 0
	duration = 'low'

	# create temporary q-table
	tempQ = Q.copy()

	# define possible next nodes
	next_options = get_next_nodes(current_location)

	# add list of possible states
	temp_states = []
	for el in next_options:
		temp_state = '{}_{}_{}'.format(current_location, el, duration)
		temp_states.append(temp_state)

	# define random value for explore / exploit decision
	rvalue = random.random()

	# if debug == True:
	# 	print '--START DECIPHER NEXT NODE--'
	# 	print 'rvalue: {}'.format(rvalue)
	# 	print 'epsilon: {}'.format(epsilon)
	# 	print 'next_options: {}'.format(next_options)
	# 	print 'Q: {}'.format(Q)
	# 	print 'temp_states: {}'.format(temp_states)
	# 	print '--END DECIPHER NEXT NODE--'

	# choose move
	print 'next_options: {}'.format(next_options)
	print 'temp_states: {}'.format(temp_states)
	initial_move = choose_next_node(rvalue, epsilon, next_options, tempQ, temp_states)

	# if debug == True:
	# 	print 'Initial move: {}'.format(initial_move)

	# update current and previous location
	previous_location = current_location
	print 'initial_move: {}'.format(initial_move)
	current_location = initial_move
	# if type(initial_move) == set:
	# 	current_location = list(initial_move)[0]
	# else:
	# 	current_location = initial_move

	path = '{}_{}'.format(previous_location, current_location)
	pathr = '{}_{}'.format(current_location, previous_location)
	state = '{}_{}_{}'.format(previous_location, current_location, duration)

	# get base reward
	temp_reward = get_reward(previous_location, current_location)

	# get adjusted reward
	if path in traveled:
		temp_reward -= 10

	# determine next maxQ
	next_options = get_next_nodes(current_location)
	next_states = []
	for el in next_options:
		temp_state = '{}_{}_{}'.format(current_location, el, duration)
		next_states.append(temp_state)

	if len(tempQ) > 0:
		found_states = []
		for el in next_states:
			if el in Q.keys():
				found_states.append(el)
		maxQ_next = { k: Q[k] for k in found_states }
		if len(maxQ_next) > 0:
			maxQ_next = [ v for k,v in maxQ_next.iteritems() if v == max(maxQ_next.values()) ][0]
		else:
			maxQ_next = 0
	else:
		maxQ_next = 0

	# add state to tempQ table if it doesn't exist
	if not state in tempQ.keys():
		tempQ[state] = 0

	# update Q values
	# qtemp[state] = qtemp[state] + alpha * (rewards[initial_move] + gamma * maxQ_next - qtemp[state])
	tempQ[state] = tempQ[state] + alpha * (temp_reward + gamma * maxQ_next - tempQ[state])

	# add chosen path to traveled list
	traveled.append(path)
	traveled.append(pathr)

	# if debug == True:
	# 	print 'Start location: {}'.format(start_location)
	# 	print 'Previous location: {}'.format(previous_location)
	# 	print 'Current location: '.format(current_location)

	# increment mileage
	print 'previous_location: {}'.format(previous_location)
	previous_coords = get_geocoords(previous_location)
	print 'current_location: {}'.format(current_location)
	current_coords = get_geocoords(current_location)
	mileage += distance_between_nodes(previous_coords, current_coords)

	# if debug == True:
	# 	print 'Traveled nodes: {}'.format(traveled)
	# 	print 'Mileage: {}'.format(mileage)

	print "STARTING WHILE LOOP..."
	count = 0
	while start_location != current_location:

		# define possible next nodes
		# don't need this because already exists above
		# next_options = get_next_nodes(current_location)

		# if debug == True:
		# 	print 'Move number: {}'.format(count)
		# 	print 'Current location: {}'.format(current_location)
		# 	print 'Next possible locations: {}'.format(next_options)

		# determine duration (high or low) and determine the 
		# closest and furthest point from start_location 
		# in list of next options
		if mileage <= factor * target_mileage:
			duration = 'low'
		else:
			duration = 'high'

		holdme = {}
		for option in next_options:
			temp_coords = get_geocoords(option)
			temp_miles = distance_between_nodes(start_coords, temp_coords)
			holdme[option] = temp_miles

		closest_point = min(holdme, key=holdme.get)
		furthest_point = max(holdme, key=holdme.get)

		if closest_point == furthest_point:
			closest_point = None
			furthest_point = None

		# if debug == True:
		# 	print 'Closest point: {}'.format(closest_point)
		# 	print 'Furthest point: {}'.format(furthest_point)

		# add list of possible states
		temp_states = []
		for el in next_options:
			temp_state = '{}_{}_{}'.format(current_location, el, duration)
			temp_states.append(temp_state)

		# define random value for explore / exploit decision
		rvalue = random.random()

		# if debug == True:
		# 	print '--START DECIPHER NEXT NODE--'
		# 	print 'rvalue: {}'.format(rvalue)
		# 	print 'epsilon: {}'.format(epsilon)
		# 	print 'next_options: {}'.format(next_options)
		# 	print 'Q: {}'.format(Q)
		# 	print 'temp_states: {}'.format(temp_states)
		# 	print '--END DECIPHER NEXT NODE--'

		# choose next node
		print 'next_options: {}'.format(next_options)
		print 'temp_state: {}'.format(temp_states)
		next_move = choose_next_node(rvalue, epsilon, next_options, tempQ, temp_states)

		# if debug == True:
		# 	print 'Next move: {}'.format(next_move)

		# update current and previous location
		previous_location = current_location
		print 'next_move: {}'.format(next_move)
		current_location = next_move
		# if type(next_move) == set:
		# 	current_location = list(next_move)[0]
		# else:
		# 	current_location = next_move
		path = '{}_{}'.format(previous_location, current_location)
		pathr = '{}_{}'.format(current_location, previous_location)
		state = '{}_{}_{}'.format(previous_location, current_location, duration)

		# get base reward
		temp_reward = get_reward(previous_location, current_location)

		# get adjusted reward
		if path in traveled:
			temp_reward -= 10

		if current_location == closest_point and duration == 'low':
			temp_reward -= 20
		if current_location == furthest_point and duration == 'high':
			temp_reward -= 20

		# determine next maxQ
		next_options = get_next_nodes(current_location)
		next_states = []
		for el in next_options:
			temp_state = '{}_{}_{}'.format(current_location, el, duration)
			next_states.append(temp_state)

		if len(tempQ) > 0:
			found_states = []
			for el in next_states:
				if el in tempQ.keys():
					found_states.append(el)
			maxQ_next = { k: tempQ[k] for k in found_states }
			if len(maxQ_next) > 0:
				maxQ_next = [ v for k,v in maxQ_next.iteritems() if v == max(maxQ_next.values()) ][0]
			else:
				maxQ_next = 0
		else:
			maxQ_next = 0

		# add state to tempQ table if it doesn't exist
		if not state in tempQ.keys():
			tempQ[state] = 0

		# update Q value
		tempQ[state] = tempQ[state] + alpha * (temp_reward + gamma * maxQ_next - tempQ[state])

		# add chosen path to traveled list
		traveled.append(path)
		traveled.append(pathr)

		# if debug == True:
		# 	print 'Previous location: {}'.format(previous_location)
		# 	print 'Current location: {}'.format(current_location)

		# increment mileage
		print 'previous: {}'.format(previous_location)
		previous_coords = get_geocoords(previous_location)
		print 'current: {}'.format(current_location)
		current_coords = get_geocoords(current_location)
		# if debug == True:
		# 	print 'Previous coords: {}'.format(previous_coords)
		# 	print 'Current coords: {}'.format(current_coords)
		mileage += distance_between_nodes(previous_coords, current_coords)

		count += 1
		if count > 100:
			break
		print 'Miles: {}'.format(mileage)
		print 'Count: {}'.format(count)

	Q = tempQ.copy()
	# if mileage >= target_mileage - 1.0 and mileage <= target_mileage + 1.0:
	# 	print "WITHIN TRGET RANGE!!!, WITHIN TRGET RANGE!!!, WITHIN TRGET RANGE!!!, WITHIN TRGET RANGE!!!, "
	# 	Q = tempQ.copy()

#http://www.gpsvisualizer.com/map_input

final_path = []
def tester(Q):
	duration = 'low'
	start_location = '66566291'
	final_path.append(start_location)
	current_location = {k:v for k,v in Q.iteritems() if k.startswith(start_location) and k.endswith(duration)}
	current_location = [k for k,v in current_location.iteritems() if v==max(current_location.values())]
	current_location = current_location[0].split('_')[1]
	distance = distance_between_nodes(start_location, current_location)
	count = 0
	while current_location != start_location:
		movement = {k:v for k,v in Q.iteritems() if k.startswith(current_location)}
		movement = [k for k,v in movement.iteritems() if v==max(movement.values())]
		movement = movement[0].split('_')[1]
		final_path.append(movement)
		current_location = movement
		count += 1
		if count > 50:
			break

tester(Q)
print final_path

final_geo = []
for el in final_path:
	coords = get_geocoords(el)
	final_geo.append('{},{}'.format(coords.split(',')[1], coords.split(',')[0]))
