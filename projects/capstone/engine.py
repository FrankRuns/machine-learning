#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
docker run -t -i -p 5000:5000 -v $(pwd):/data osrm/osrm-backend osrm-routed /data/massachusetts-latest.osrm
'''

import random # to support explore/exploit decision
import requests # to call routing service
import json # to parse response from routing service
import xml.etree.cElementTree as ET # to parse OSM file
import time # to clock total time of algorithm
import pickle # to write and read distances between nodes during building
import os.path # to write and read distances between nodes during building
import math # various mathematical functions (math.cos for decaying epsilon)
import csv # to read geo path into csv file to be read into r
import numpy # to get range of mileage

# Define file name
filename = 'streets_to_run.osm'

# Parse the smaller OSM file
# Used in building the route
tree = ET.parse(filename)
root = tree.getroot()

# Parse the bigger OSM file
# Used in creating the final visulazations
tree2 = ET.parse('map')
root2 = tree2.getroot()

''' Define all required functions '''

def extract_intersections(nodes_or_coords='nodes', verbose=True):
	''' Create a list of all intersections in OSM file.
		Use only intersections when running q-learning - much faster '''

	counter = {}
	for child in root:
		if child.tag == 'way':
			for item in child:
				if item.tag == 'nd':
					nd_ref = item.attrib['ref']
					if not nd_ref in counter:
						counter[nd_ref] = 0
					counter[nd_ref] += 1

	intersections = filter(lambda x: counter[x] > 1, counter)

	intersection_coordinates = []
	for child in root:
		if child.tag == 'node' and child.attrib['id'] in intersections:
			coordinate = child.attrib['lat'] + ',' + child.attrib['lon']
			if verbose:
				print coordinate
			intersection_coordinates.append(coordinate)

	if nodes_or_coords == 'nodes':
		return intersections
	else:
		return intersection_coordinates

''' Below chuncks of code used for writing project document '''

# test = extract_intersections(verbose=False)
# with open ('intersections.csv', 'wb') as csvfile:
# 	routewriter = csv.writer(csvfile)
# 	routewriter.writerow(["LAT", "LON"])
# 	for el in test:
# 		the_coords = get_geocoords(el)
# 		temp = the_coords.split(',')
# 		routewriter.writerow([temp[1], temp[0]])

# def all_node_coords():
# 	coords_list = []
# 	for el in root.iter('node'):
# 		coords_list.append('{},{}'.format(el.get('lat'),el.get('lon')))

# 	return coords_list

# vis_coords_list = all_node_coords()
# with open ('all_nodes.csv', 'wb') as csvfile:
# 	routewriter = csv.writer(csvfile)
# 	routewriter.writerow(["LAT", "LON"])
# 	for el in vis_coords_list:
# 		temp = el.split(',')
# 		routewriter.writerow([temp[0], temp[1]])


def get_geocoords(nodeid):
	''' parses osm file and returns lat lon coords
		example input = '66566291'
		example output = '-71.0727793,42.4436791' '''

	for node in root.findall(".//node[@id='"+nodeid+"']"):
		return node.get('lon') + ',' + node.get('lat')


def get_geocoords_final_path(node_path):
	''' used to get geo coords of final path 
	    note that we use root2 map '''
	path_nodes = []
	all_nodes_data = root2.findall("node")
	all_nodes = [x.get('id') for x in root2.findall("node")]

	for el in [str(x) for x in node_path]:
		if el in all_nodes:
			all_nodes_idx = [x.get('id') for x in all_nodes_data].index(el)
			the_coords = str(all_nodes_data[all_nodes_idx].get('lon')+','+all_nodes_data[all_nodes_idx].get('lat'))
			path_nodes.append(the_coords)

	return path_nodes


def route_distance_between_nodes(end_coords, start_coords):
	''' node inputs are stings of longitude / latitude geo coords
		example node1 = '-71.0727793,42.4436791'
		example node2 = '-71.0721040,42.4436421' '''

	# include steps between node (just in case, probably not used)
	url = 'http://127.0.0.1:5000/route/v1/walking/{};{}?steps=true'.format(end_coords, start_coords)

	# make request to server and translate response to json
	r = requests.get(url)
	data = r.json()

	# parse distance between nodes and convert to miles
	# meters = data['routes'][0]['legs'][0]['steps'][0]['distance'] # fucked up
	meters = data['routes'][0]['distance']
	miles = meters * 0.000621371 # 1 meter is 0.000621371 miles

	return miles


def get_coords_in_route(final_details):
	''' After algorithm runs and you have list of intersection nodes
	    for the route, this function will take that list as an input
	    and return a full list of geo coords for mapping. '''

	temp_nodes = []

	for i in range(len(final_details)-1):
		print(i)
		t2 = get_geocoords(final_details[i+1])
		t1 = get_geocoords(final_details[i])

		url = 'http://127.0.0.1:5000/route/v1/walking/{};{}?steps=true&annotations=nodes'.format(t1,t2)
		r = requests.get(url)
		data = r.json()

		if i == len(final_details):
			node_list = [str(x) for x in data['routes'][0]['legs'][0]['annotation']['nodes']]
		else:
			node_list = [str(x) for x in data['routes'][0]['legs'][0]['annotation']['nodes'][:-1]]

		if len(temp_nodes) == 0:
			temp_nodes = node_list
		else:
			temp_nodes.extend(node_list)

	temp_nodes.append(final_details[-1])

	temp_coords = get_geocoords_final_path(temp_nodes)

	return temp_coords


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


def filter_list(list1, list2):
	''' Identifies elements of list1 that are also in list 2.
		Used in get_next_nodes_2. '''

	templist = []
	for el in list1:
		if el in list2:
			templist.append(el)
	return templist

''' I think the below function is now obsolete '''

# def get_next_nodes(current_node):
# 	''' Iterates through osm and finds all possible next moves
# 		used to produce list of next options from current point '''

# 	# list where all next nodes will be stored
# 	next_nodes = []

# 	# iterate through each way in the map file
# 	# way must be a road or trail (i.e. you can't run through a building)
# 	# in osm data, buildings are also captured as waypoints (and I filtered that out of the datafile)
# 	for way in root.findall('way'):
# 		# for each way in map file, iterate thorugh each node on that way
# 		for node in way.findall('nd'):
# 			# if the node of interest is in that way go deeper
# 			if node.get('ref')==current_node:
# 				# temp store the nodes on this way as a list
# 				tempway = way.findall('nd')
# 				# iterate through node list
# 				for subnode in tempway:
# 					# if the node during iteration is the curent node...
# 					if subnode.get('ref') == current_node:
# 						# grab it's index
# 						idx = tempway.index(subnode)
# 						# if first node in way, only take node that comes after
# 						if idx == 0:
# 							next_nodes.append(tempway[idx+1].get('ref'))
# 						# if not first node in way, take prior and after node
# 						if idx > 0 and idx < len(tempway)-1:
# 							next_nodes.append(tempway[idx+1].get('ref'))
# 							next_nodes.append(tempway[idx-1].get('ref'))
# 						# if last node in way, only take node prior
# 						if idx == len(tempway)-1:
# 							next_nodes.append(tempway[idx-1].get('ref'))

# 	return list(set(next_nodes))


# So we don't have to run the extraction multiple times,
# declare the list of intersection nodes as global variable
intersection_nodes = extract_intersections(verbose=False)

def get_next_nodes_2(current_location):

	next_nodes = []

	for way in root.findall('way'):
		point_list = [el.get('ref') for el in way.findall('nd')]
		if current_location in point_list:
			tempway = filter_list(point_list, intersection_nodes)
			if len(tempway) > 1:
				idx = tempway.index(current_location)
				if idx == 0:
					next_nodes.append(tempway[idx+1])
				elif idx == len(tempway) - 1:
					next_nodes.append(tempway[idx-1])
				else:
					next_nodes.append(tempway[idx-1])
					next_nodes.append(tempway[idx+1])

	return list(set(next_nodes))

r_base = 1000

def get_reward(node1, node2):
	''' Using 2 nodes, determine reward of moving between them
		if run on trail, reward + x
		if run past natural scene (water), reward + x
		if run past historic site, reward + x '''

	reward = 0
	# print 'Nodes are {}, {}'.format(node1, node2)

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
				new_tag_list.append(oldtag.get('v'))
			keywords = ['natural', 'waterway', 'bicycle', 'foot', 'checkpoint', 'mountain_pass', 'historic',
					    'path', 'hiking', 'unpaved', 'footway']
			count = 0
			for el in new_tag_list:
				if el in keywords:
					count += 1
			# print '{}: {}'.format('Count of rewards present', count)
			reward = reward + (r_base * count)
			print 'Base Reward: {}'.format(reward)

			return reward

	return 0


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

''' If data point exists, don't call function again, call from dictionary '''

if os.path.exists('distances.txt'):
	with open("distances.txt", "rb") as f:
		distances = pickle.load(f)
else:
	distances = {}

# distances = {}
neighbor_nodes = {}
rewards = {}
list_of_coords = {}

# create policy table
Q = {}

# define paramters
gamma = 0.7
# alpha = 0.6
alpha = 0.5
factor_radius = 0.5 # err on the side of longer run
factor_duration = 0.85
base_target_mileage = 2.0 # maybe this should be variable..
n_trials = 200 # int(2.71828 ** (-0.153 * target_mileage) * 219.09 * target_mileage) # 400 for 2 miles
errors = [] # stores error in event call to routing service fails
rewards = []
start_location = '66572004' # stone place, melrose

r_back = 20000
r_retrace = 15000
# r_retrace_low = 0
# r_retrace_high = 0
r_finish = 100000000
r_low = 2000 # 0
r_high = 25000

''' Run similation '''

for trial in range(n_trials):

	target_milage_range = numpy.arange(base_target_mileage - 0, base_target_mileage + 0.5, 0.1)
	target_mileage = random.choice(target_milage_range)

	print(trial)
	epsilon = math.cos(1.59/n_trials*trial)
	alpha = math.cos(1.59/n_trials*trial)

	''' Define start node, coords for 
	start location and an empty list to store traveled
	paths. If start coords not stored, call get_geocoords '''

	if start_location in list_of_coords.keys():
		start_coords = list_of_coords[start_location]
	else:
		start_coords = get_geocoords(start_location)
		list_of_coords[start_location] = start_coords

	''' Define miles, initial duration, and list for
	visited locations
	Duration is low if <0.5 through target miles.
	Duration is high if >=0.5 through target miles '''

	mileage = 0
	duration = 'low'
	traveled = []
	pathed = []

	''' From start location, where can we go next? 
	Save next possible nodes to a list. This is used to 
	determine where to go next '''

	if start_location in neighbor_nodes.keys():
		next_options = neighbor_nodes[start_location]
	else:
		next_options = get_next_nodes_2(start_location)
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
		Q, temp_states)

	''' Update current and previous location while restating
	the path (in either direction) and state '''

	state = '{}_{}_{}_{}'.format(start_location, None, initial_move, \
		duration)	
	path = '{}_{}'.format(start_location, initial_move)

	''' Add state to tempQ table if it doesn't exist '''
	if not state in Q.keys():
		Q[state] = 0

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
		next_options = get_next_nodes_2(initial_move)
		neighbor_nodes[initial_move] = next_options

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

	coords_path = '{},{}'.format(start_coords, current_coords)
	coords_pathr = '{},{}'.format(current_coords, start_coords)

	if coords_path in distances.keys():
		mileage += distances[coords_path]
		print 'Skipping API'
	else:
		print "Calling API"
		distance = route_distance_between_nodes(start_coords, current_coords)
		mileage += distance
		distances[coords_path] = distance
		distances[coords_pathr] = distance

	next_states = [] # now interpret from nodes into states
	for el in next_options:
		super_temp_coords = get_geocoords(el)

		if '{}, {}'.format(super_temp_coords, start_coords) in distances.keys():
			super_temp_radius_distance = distances['{}, {}'.format(super_temp_coords, start_coords)]
			print "Skipping API - determining next options duration and state"
		else:
			print "Calling API"
			super_temp_radius_distance = route_distance_between_nodes(super_temp_coords, start_coords)
			distances['{}, {}'.format(super_temp_coords, start_coords)] = super_temp_radius_distance
		if '{}, {}'.format(current_coords, super_temp_coords) in distances.keys():
			super_temp_duration_distance = distances['{}, {}'.format(current_coords, super_temp_coords)]
		else:
			print "Calling API"
			super_temp_duration_distance = route_distance_between_nodes(current_coords, super_temp_coords)
			distances['{}, {}'.format(current_coords, super_temp_coords)] = super_temp_duration_distance

		super_temp_mileage = mileage + super_temp_duration_distance
		
		if super_temp_radius_distance > factor_radius * target_mileage or super_temp_mileage > factor_duration * target_mileage:
			next_duration = 'high'
		else:
			next_duration = 'low'	
		temp_state = '{}_{}_{}_{}'.format(initial_move, start_location, el, next_duration)
		next_states.append(temp_state)

	if len(Q) > 0: # and determine max Q if it exists
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

	Q[state] = Q[state] + alpha * (temp_reward + gamma \
		* maxQ_next - Q[state])

	# Q[state] = Q[state] + alpha * (temp_reward + gamma \
	# 	* maxQ_next)

	''' Add chosen path to traveled list (in both directions) and update location '''

	traveled.append(start_location)
	traveled.append(initial_move)
	pathed.append(path)

	current_location = initial_move
	previous_location = start_location

	count = 0
	miles = [mileage]
	journey = 1
	while start_location != current_location:

		''' Determine duration of run at this point and
			the closest and furthest next point from the start '''

		if '{}, {}'.format(current_coords, start_coords) in distances.keys():
			distance_from_origin = distances['{}, {}'.format(current_coords, start_coords)]
			print "Skipping API - determining duration"
		else:
			print "Calling API"
			distance_from_origin = route_distance_between_nodes(current_coords, start_coords)
			distances['{}, {}'.format(current_coords, start_coords)] = distance_from_origin
		if duration == 'low':
			if distance_from_origin > factor_radius * target_mileage or mileage > factor_duration * target_mileage:
				duration = 'high'

		# holdme = {}
		# for option in next_options:
		# 	# get geocoords of each next move
		# 	if option in list_of_coords.keys():
		# 		temp_coords = list_of_coords[option]
		# 	else:
		# 		temp_coords = get_geocoords(option)
		# 		list_of_coords[option] = temp_coords
		# 	# get distance from next move to start location
		# 	temp_path = '{}_{}'.format(temp_coords, start_coords)
		# 	if temp_path in distances.keys():
		# 		temp_miles = distances[temp_path]
		# 		print "Skipping API - determining closest / furthest point"
		# 	else:
		# 		try:
		# 			print "Calling API !!!!!!"
		# 			temp_miles = route_distance_between_nodes(temp_coords, start_coords)
		# 			distances['{}_{}'.format(temp_coords, start_coords)] = temp_miles
		# 		except:
		# 			errors.append('Connection Error')
		# 			temp_miles = 0
		# 	holdme[option] = temp_miles

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
			temp_miles = crow_distance_between_nodes(temp_coords, start_coords)
			holdme[option] = temp_miles

		closest_point = min(holdme, key=holdme.get)
		furthest_point = max(holdme, key=holdme.get)

		if closest_point == furthest_point:
			closest_point = None
			furthest_point = None
			print "Closest point is NONE"

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
			Q, temp_states)

		''' Update current and previous location while restating
		the path (in either direction) and state '''

		state = '{}_{}_{}_{}'.format(current_location, previous_location, next_move, \
			duration)	
		path = '{}_{}'.format(current_location, next_move)

		''' Add state to tempQ table if it doesn't exist '''
		if not state in Q.keys():
			Q[state] = 0

		''' Get base reward for chosen move '''

		temp_reward = get_reward(current_location, next_move)
		rewards.append(temp_reward)

		''' Get adjusted reward if retracing steps '''

		state_parts = state.split('_')
		if state_parts[1] == state_parts[2]:
			temp_reward -= r_back # dont go back to where you just were
		
		# if '{}_{}'.format(state_parts[0], state_parts[2]) in pathed:
		# 	temp_reward -= r_retrace

		# if '{}_{}'.format(state_parts[0], state_parts[2]) in pathed and state=='low':
		# 	temp_reward -= r_retrace_low
		# elif '{}_{}'.format(state_parts[0], state_parts[2]) in pathed and state=='high':
		# 	temp_reward -= r_retrace_high

		if next_move in traveled and path not in pathed and mileage < (mileage * factor_duration):
			temp_reward -= r_retrace

		previous_location = current_location
		current_location = next_move

		if duration == 'high':
			if current_location == start_coords:
				temp_reward += r_finish

		if duration == 'low':
			if current_location == furthest_point and current_location != closest_point:
				temp_reward += r_low
		if duration == 'high':
			if current_location == closest_point and current_location != furthest_point:
				temp_reward += r_high

		''' This section determins the Q value of the moves that
		follow the one just chosen. For example if you chose A-B and
		from B you can go from B-C or B-D and the Q values are 0 and
		10 respectively... the max Q value will be 10. This will be
		used to update the Q value for our current state '''

		if current_location in neighbor_nodes.keys():
			next_options = neighbor_nodes[current_location]
		else:
			next_options = get_next_nodes_2(current_location)
			neighbor_nodes[current_location] = next_options

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
			print "Skipping API"
		else:
			print "Calling API"
			distance = route_distance_between_nodes(previous_coords, current_coords)
			mileage += distance
			distances[coords_path] = distance
			distances[coords_pathr] = distance

		next_states = [] # now interpret from nodes into states
		for el in next_options:
			super_temp_coords = get_geocoords(el)

			if '{}, {}'.format(super_temp_coords, start_coords) in distances.keys():
				super_temp_radius_distance = distances['{}, {}'.format(super_temp_coords, start_coords)]
				print "Skipping API - determining next options duration and state"
			else:
				print "Calling API"
				super_temp_radius_distance = route_distance_between_nodes(super_temp_coords, start_coords)
				distances['{}, {}'.format(super_temp_coords, start_coords)] = super_temp_radius_distance
			if '{}, {}'.format(previous_coords, super_temp_coords) in distances.keys():
				super_temp_duration_distance = distances['{}, {}'.format(previous_coords, super_temp_coords)]
			else:
				print "Calling API"
				super_temp_duration_distance = route_distance_between_nodes(current_coords, super_temp_coords)
				distances['{}, {}'.format(previous_coords, super_temp_coords)] = super_temp_duration_distance

			super_temp_mileage = mileage + super_temp_duration_distance

			if super_temp_radius_distance > factor_radius * target_mileage or super_temp_mileage > factor_duration * target_mileage:
				next_duration = 'high'
			else:
				next_duration = 'low'	
			temp_state = '{}_{}_{}_{}'.format(current_location, previous_location, el, next_duration)
			next_states.append(temp_state)			

		if len(Q) > 0: # and determine max Q if it exists
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

		Q[state] = Q[state] + alpha * (temp_reward + gamma \
			* maxQ_next - Q[state])


		# Q[state] = Q[state] + alpha * (temp_reward + gamma \
		# 	* maxQ_next)

		''' Add chosen path to traveled list (in both directions) '''
		traveled.append(current_location)
		miles.append(mileage)

		''' Add paths to path list '''
		pathed.append(path)

		if mileage > target_mileage * 1.1: # need to give it a chance to learn in high duration states
			break

		if current_location == start_location:
			break

		count += 1

	if trial % 100 == 0 and trial != 0:
		time.sleep(15) # give me a break..


# Write new distances into file
with open("distances.txt", "wb") as f2:
	pickle.dump(distances, f2)


final_path = []
final_miles = []
def get_final_path(Q):

	print 'FINAL RUN. FINAL RUN. FINAL RUN. FINAL RUN.'
	
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

# {k:v for k,v in Q.iteritems() if k.startswith('616527347') and \
# k.split('_')[1] ==  '616527487' and \
# k.endswith('low')}

	if current_location in list_of_coords.keys():
		current_coords = list_of_coords[current_location]
	else:
		current_coords = get_geocoords(current_location)
		list_of_coords[current_location] = current_coords	

	distance = route_distance_between_nodes(start_coords, current_coords)

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
		
		distance = route_distance_between_nodes(current_coords, movement_coords)	

		current_location = movement
		current_coords = movement_coords

		mileage += distance

		# if mileage <= factor * target_mileage:
		# 	duration = 'low'
		# else:
		# 	duration = 'high'

		distance_from_origin = route_distance_between_nodes(current_coords, start_coords)
		if distance_from_origin > factor_radius * target_mileage or mileage > factor_duration * target_mileage:
			duration = 'high'

		previous_location = final_path[len(final_path)-2]

		count += 1
		if mileage > target_mileage * 1.5:
			break

		final_miles.append(mileage)

	print mileage

get_final_path(Q)

print 'Trials: {}, Alpha: {}, Gamma: {}, r_base: {}, r_back: {}, \
		r_retrace: {}, r_finish: {}, r_low: {}, r_high: {}'.format(n_trials, alpha, \
		gamma, r_base, r_back, r_retrace_high, r_finish, r_low, r_high)

# def get_final_geos(final_path):
# 	''' takes list of OSM nodes returns list of coordinates '''

# 	final_geo = []
# 	for el in final_path:
# 		if el in list_of_coords.keys():
# 			movement_coords = list_of_coords[el]
# 		else:
# 			movement_coords = get_geocoords(el)
# 			list_of_coords[el] = movement_coords	
# 		final_geo.append('{},{}'.format(movement_coords.split(',')[0], movement_coords.split(',')[1]))

# 	return final_geo

# last_path = get_final_geos(final_path)

last_path = get_coords_in_route(final_path)
with open ('route.csv', 'wb') as csvfile:
	routewriter = csv.writer(csvfile)
	routewriter.writerow(["LAT", "LON"])
	for el in last_path:
		temp = el.split(',')
		print temp
		routewriter.writerow([temp[1], temp[0]])






