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
import time

# Define file name
filename = 'streets_to_run.osm'

# Parse the smaller OSM file
# Used in building the route
start = time.time()
tree = ET.parse(filename)
root = tree.getroot()
end = time.time()
# print end-start

# Parse the bigger OSM file
# Used in creating the final visulazations
start = time.time()
tree2 = ET.parse('map')
root2 = tree2.getroot()
end = time.time()
# print end-start

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
			# if verbose:
				# print coordinate
			intersection_coordinates.append(coordinate)

	if nodes_or_coords == 'nodes':
		return intersections
	else:
		return intersection_coordinates

start = time.time()
test = extract_intersections()
end = time.time()
print end-start

''' Below chuncks of code used for writing project document '''

# test = extract_intersections(verbose=False)
# with open ('intersections.csv', 'wb') as csvfile:
# 	routewriter = csv.writer(csvfile)
# 	routewriter.writerow(["LAT", "LON"])
# 	for el in test:
# 		the_coords = get_node_geocoords(el)
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


def get_node_geocoords(node_id):
	''' parses osm file and returns lat lon coords
		example input = '66566291'
		example output = '-71.0727793,42.4436791' '''

	if node_id in list_of_coords.keys():
		node_coords = list_of_coords[node_id]
	else:
		for node in root.findall(".//node[@id='"+node_id+"']"):
			node_coords = node.get('lon') + ',' + node.get('lat')
		list_of_coords[node_id] = node_coords

	return node_coords	


'''
start = time.time()
test = get_node_geocoords('66566291')
end = time.time()
print end-start
0.05
'''

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

	if '{}, {}'.format(end_coords, start_coords) in distances_path.keys():
		return distances_path['{}, {}'.format(end_coords, start_coords)]

	# include steps between node (just in case, probably not used)
	url = 'http://127.0.0.1:5000/route/v1/walking/{};{}?steps=true'.format(end_coords, start_coords)

	# make request to server and translate response to json
	r = requests.get(url)
	data = r.json()

	# parse distance between nodes and convert to miles
	# meters = data['routes'][0]['legs'][0]['steps'][0]['distance'] # fucked up
	meters = data['routes'][0]['distance']
	miles = meters * 0.000621371 # 1 meter is 0.000621371 miles

	distances_path['{}, {}'.format(end_coords, start_coords)] = miles

	return miles

'''
start = time.time()
test = route_distance_between_nodes('-71.0727793,42.4436791', '-71.0721040,42.4436421')
end = time.time()
print end-start
0.005
'''

def get_coords_in_route(final_details):
	''' After algorithm runs and you have list of intersection nodes
	    for the route, this function will take that list as an input
	    and return a full list of geo coords for mapping. '''

	temp_nodes = []

	for i in range(len(final_details)-1):
		t2 = get_node_geocoords(final_details[i+1])
		t1 = get_node_geocoords(final_details[i])

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


# So we don't have to run the extraction multiple times,
# declare the list of intersection nodes as global variable
intersection_nodes = extract_intersections(verbose=False)

def get_next_nodes_2(current_location):

	if current_location in neighbor_nodes.keys():
		next_options = neighbor_nodes[start_location]

		return next_options
	else:
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

'''
start = time.time()
test = get_next_nodes_2('66566291')
end = time.time()
print end-start
0.01
'''

r_base = 1000

def get_reward(node1, node2):
	''' Using 2 nodes, determine reward of moving between them
		if run on trail, reward + x
		if run past natural scene (water), reward + x
		if run past historic site, reward + x '''

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
				new_tag_list.append(oldtag.get('v'))
			keywords = ['natural', 'waterway', 'bicycle', 'foot', 'checkpoint', 'mountain_pass', 'historic',
					    'path', 'hiking', 'unpaved', 'footway']
			count = 0
			for el in new_tag_list:
				if el in keywords:
					count += 1
			reward = reward + (r_base * count)

			return reward

	return 0

'''
start = time.time()
test = get_reward('66566291', '66557255')
end = time.time()
print end-start
0.013
'''


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


def increment_mileage(mileage, first_location, second_location):

	''' example inputs 
		mileage is numeric: 2.0
		first_location is a osm node id: '23455643'
		second_location is a osm node id: '12199942'
	'''

	if first_location in list_of_coords.keys():
		first_coords = list_of_coords[first_location]
	else:
		first_coords = get_node_geocoords(first_location)
		list_of_coords[first_location] = first_coords

	if second_location in list_of_coords.keys():
		second_coords = list_of_coords[second_location]
	else:
		second_coords = get_node_geocoords(second_location)
		list_of_coords[second_location] = second_coords

	coords_path = '{},{}'.format(first_coords, second_coords)
	coords_pathr = '{},{}'.format(second_coords, first_coords)

	if coords_path in distances_path.keys():
		mileage += distances_path[coords_path]
	else:
		distance = route_distance_between_nodes(first_coords, second_coords)
		mileage += distance
		distances_path[coords_path] = distance
		distances_path[coords_pathr] = distance

	return mileage


def get_next_states(next_options, where_you_are, where_you_were, coords_where_you_are, path_type, growth_factor):

	if path_type == 'path_wise':

		next_states = [] # now interpret from nodes into states
		for el in next_options:
			super_temp_coords = get_node_geocoords(el)

			# if '{}, {}'.format(super_temp_coords, start_coords) in distances_path.keys():
			# 	super_temp_radius_distance = distances_path['{}, {}'.format(super_temp_coords, start_coords)]
			# else:
			# 	super_temp_radius_distance = route_distance_between_nodes(super_temp_coords, start_coords)
			# 	distances_path['{}, {}'.format(super_temp_coords, start_coords)] = super_temp_radius_distance

			if '{}, {}'.format(super_temp_coords, start_coords) in distances_crow.keys():
				super_temp_radius_distance = distances_crow['{}, {}'.format(super_temp_coords, start_coords)]
			else:
				super_temp_radius_distance = crow_distance_between_nodes(super_temp_coords, start_coords)
				distances_crow['{}, {}'.format(super_temp_coords, start_coords)] = super_temp_radius_distance

			if '{}, {}'.format(coords_where_you_are, super_temp_coords) in distances_path.keys():
				super_temp_duration_distance = distances_path['{}, {}'.format(coords_where_you_are, super_temp_coords)]
			else:
				super_temp_duration_distance = route_distance_between_nodes(coords_where_you_are, super_temp_coords)
				distances_path['{}, {}'.format(coords_where_you_are, super_temp_coords)] = super_temp_duration_distance

			super_temp_mileage = mileage + super_temp_duration_distance
			
			if super_temp_radius_distance > factor_radius * target_mileage or super_temp_mileage > factor_duration * target_mileage:
				next_duration = 'high'
			else:
				next_duration = 'low'

			temp_state = '{}_{}_{}_{}'.format(where_you_are, where_you_were, el, next_duration)
			next_states.append(temp_state)

	else:

		next_states = [] # now interpret from nodes into states
		for el in next_options:
			super_temp_coords = get_node_geocoords(el)

			if '{}, {}'.format(super_temp_coords, start_coords) in distances_crow.keys():
				super_temp_radius_distance = distances_crow['{}, {}'.format(super_temp_coords, start_coords)]
			else:
				if path_type == 'path_wise':
					super_temp_radius_distance = route_distance_between_nodes(super_temp_coords, start_coords)
				else:
					super_temp_radius_distance = crow_distance_between_nodes(super_temp_coords, start_coords) * growth_factor
				distances_crow['{}, {}'.format(super_temp_coords, start_coords)] = super_temp_radius_distance
			
			if '{}, {}'.format(coords_where_you_are, super_temp_coords) in distances_crow.keys():
				super_temp_duration_distance = distances_crow['{}, {}'.format(coords_where_you_are, super_temp_coords)]
			else:
				if path_type == 'path_wise':
					super_temp_duration_distance = route_distance_between_nodes(coords_where_you_are, super_temp_coords)
				else:
					super_temp_duration_distance = crow_distance_between_nodes(coords_where_you_are, super_temp_coords) * growth_factor
				distances_crow['{}, {}'.format(coords_where_you_are, super_temp_coords)] = super_temp_duration_distance

			super_temp_mileage = mileage + super_temp_duration_distance
			
			if super_temp_radius_distance > factor_radius * target_mileage or super_temp_mileage > factor_duration * target_mileage:
				next_duration = 'high'
			else:
				next_duration = 'low'

			temp_state = '{}_{}_{}_{}'.format(where_you_are, where_you_were, el, next_duration)
			next_states.append(temp_state)

	return next_states


def get_max_q(next_states):

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

	return maxQ_next

def get_average_q(next_states):

	if len(Q) > 0: # and determine max Q if it exists
		found_states = []
		for el in next_states:
			if el in Q.keys():
				found_states.append(el)
		if len(found_states) > 0:
			holder = []
			for key, value in Q.iteritems():
				if key in found_states:
					holder.append(value)
			average_q = numpy.mean(holder)
		else:
			average_q = 0
	else:
		average_q = 0

	return average_q



def determine_duration(duration, mileage, target_mileage, current_coords, start_coords, path_type, growth_factor):

	if duration == 'high':
		return 'high'

	if path_type == 'path_wise':

		if '{}, {}'.format(current_coords, start_coords) in distances_path.keys():
			distance_from_origin = distances_path['{}, {}'.format(current_coords, start_coords)]
		else:
			distance_from_origin = route_distance_between_nodes(current_coords, start_coords)
			distances_path['{}, {}'.format(current_coords, start_coords)] = distance_from_origin
		
		if distance_from_origin > factor_radius * target_mileage or mileage > factor_duration * target_mileage:
			new_duration = 'high'
		else:
			new_duration = 'low'

		return new_duration

	else:

		if '{}, {}'.format(current_coords, start_coords) in distances_crow.keys():
			distance_from_origin = distances_crow['{}, {}'.format(current_coords, start_coords)]
		else:
			distance_from_origin = crow_distance_between_nodes(current_coords, start_coords) * growth_factor
			distances_crow['{}, {}'.format(current_coords, start_coords)] = distance_from_origin
		
		if distance_from_origin > factor_radius * target_mileage or mileage > factor_duration * target_mileage:
			new_duration = 'high'
		else:
			new_duration = 'low'

		return new_duration


def get_close_far(path_type, next_options):

	if path_type == 'path_wise':

		holdme = {}
		for option in next_options:
			# get geocoords of each next move
			if option in list_of_coords.keys():
				temp_coords = list_of_coords[option]
			else:
				temp_coords = get_node_geocoords(option)
				list_of_coords[option] = temp_coords
			# get distance from next move to start location
			temp_path = '{}_{}'.format(temp_coords, start_coords)
			if temp_path in distances_path.keys():
				temp_miles = distances_path[temp_path]
				# print "Skipping API - determining closest / furthest point"
			else:
				try:
					# print "Calling API !!!!!!"
					temp_miles = route_distance_between_nodes(temp_coords, start_coords)
					distances_path['{}_{}'.format(temp_coords, start_coords)] = temp_miles
				except:
					errors.append('Connection Error')
					temp_miles = 0
			holdme[option] = temp_miles

	else:

		holdme = {}
		for option in next_options:
			# get geocoords of each next move
			if option in list_of_coords.keys():
				temp_coords = list_of_coords[option]
			else:
				temp_coords = nodeid_to_coords(option)
				list_of_coords[option] = temp_coords
			# get distance from next move to start location
			temp_path = '{}_{}'.format(temp_coords, start_coords)
			temp_miles = crow_distance_between_nodes(temp_coords, start_coords)
			distances_crow['{}_{}'.format(temp_coords, start_coords)] = temp_miles
			holdme[option] = temp_miles

	closest_point = min(holdme, key=holdme.get)
	furthest_point = max(holdme, key=holdme.get)

	if closest_point == furthest_point:
		closest_point = None
		furthest_point = None

	return {'closest_point': closest_point, 'furthest_point': furthest_point}


''' If data point exists, don't call function again, call from dictionary '''

if os.path.exists('distances_crow.txt'):
	with open("distances_crow.txt", "rb") as f:
		distances_crow = pickle.load(f)
else:
	distances_crow = {}

if os.path.exists('distances_path.txt'):
	with open("distances_path.txt", "rb") as f:
		distances_path = pickle.load(f)
else:
	distances_path = {}

# distances_crow = {}
# distances_path = {}
neighbor_nodes = {}
rewards = {}
list_of_coords = {}

# create policy table
Q = {}

# define paramters
gamma = 0.5
# alpha = 0.5
factor_radius = 0.5
factor_duration = 0.6
base_target_mileage = 5.0
n_trials = int(base_target_mileage * 400)
errors = [] # stores error in event call to routing service fails
start_location = '66572004' # stone place, melrose
q_initialization_value = 0
growth_factor = 1.0 + ((base_target_mileage/2) * 0.0)
q_type = 'max'
next_step_duration_type = 'path_wise'
recalc_duration_type = 'path_wise'

# define reward structure
r_back = 20000
r_retrace = 0#5000
r_finish = 4000
r_low = 2000
r_high = 30000

''' Run similation '''

start_run = time.time()

for trial in range(n_trials):

	start = time.time()

	# target_milage_range = numpy.arange(base_target_mileage - 0.15, base_target_mileage + 0.15, 0.05)
	# target_mileage = random.choice(target_milage_range)

	target_mileage = base_target_mileage

	epsilon = math.cos(1.59/n_trials*trial)
	alpha = ((-1.0*trial) + n_trials) / (n_trials + 1)

	''' Define start node, coords for 
	start location and an empty list to store traveled
	paths. If start coords not stored, call get_node_geocoords '''

	start_coords = get_node_geocoords(start_location)

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

	next_options = get_next_nodes_2(start_location)

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
		the path (in either direction) and state. State =
		current position, where you were, where youre going, duration '''

	state = '{}_{}_{}_{}'.format(start_location, None, initial_move, \
		duration)	
	path = '{}_{}'.format(start_location, initial_move)

	''' Add state to tempQ table if it doesn't exist '''
	if not state in Q.keys():
		Q[state] = q_initialization_value

	''' Get base reward for chosen move '''

	temp_reward = get_reward(start_location, initial_move)

	''' Based on chosen move, increment mileage.
	    Function below will find distance between
	    coords (path wise), store those distances in distances
	    dictionary and return the new incremented mileage. '''

	mileage = increment_mileage(mileage, start_location, initial_move)

	''' Determine Q value '''

	''' This section determins the Q value of the moves that
	follow the one just chosen. For example if you chose A-B and
	from B you can go from B-C or B-D and the Q values are 0 and
	10 respectively... the max Q value will be 10. This will be
	used to update the Q value for our current state '''

	next_options = get_next_nodes_2(initial_move)

	''' For next options determine their states
	    Depending upon mileage change from immediate
	    move and the move thereafter, the state may change.
	    Hence, we need to determine the duration not just
	    currently, but also after we make the impending move.
	    Note that if you use path_wise or crow_wise it will nearly
	    always be the same. Crow is faster so crow it. '''

	initial_move_coords = get_node_geocoords(initial_move)
	next_states = get_next_states(next_options, initial_move, start_location, initial_move_coords, next_step_duration_type, growth_factor)

	''' For next states, determine either
		next max q or average q '''

	if q_type == 'max':
		future_q_value = get_max_q(next_states)
	else:
		future_q_value = get_average_q(next_states)

	Q[state] = Q[state] + alpha * (temp_reward + gamma \
		* future_q_value - Q[state])

	''' Add chosen path to traveled list (in both directions) '''
	traveled.append(start_location)
	traveled.append(initial_move)

	''' Add paths to path list '''
	pathed.append(path)

	current_location = initial_move
	previous_location = start_location

	count = 0
	while start_location != current_location:

		''' Determine duration of run at this point and
			the closest and furthest next point from the start '''

		if count == 0:
			duration = determine_duration(duration, mileage, target_mileage, initial_move_coords, start_coords, recalc_duration_type, growth_factor)
		else:
			previous_location_coords = get_node_geocoords(previous_location)
			duration = determine_duration(duration, mileage, target_mileage, current_location_coords, previous_location_coords, recalc_duration_type, growth_factor)

		''' Determine closest and furthest point from start location '''

		# close_and_far = get_close_far(close_and_far_duration_type, next_options)
		close_and_far_path = get_close_far('path_wise', next_options)
		close_and_far_crow = get_close_far('crow_wise', next_options)

		''' Define random value for explore / exploit decision '''

		rvalue = random.random()

		''' Based on current location, next options, and 
		current mileage. This is used to determine where to
		go next '''

		''' Choose next move '''

		next_move = choose_next_node(rvalue, epsilon, next_options, \
			Q, next_states)

		''' Update current and previous location while restating
		the path (in either direction) and state '''

		state = '{}_{}_{}_{}'.format(current_location, previous_location, next_move, \
			duration)	
		path = '{}_{}'.format(current_location, next_move)

		''' Add state to tempQ table if it doesn't exist '''
		if not state in Q.keys():
			Q[state] = q_initialization_value

		''' Get base reward for chosen move '''

		temp_reward = get_reward(current_location, next_move)

		''' Get adjusted reward if going back or retracing steps '''

		# state_parts = state.split('_')
		# if state_parts[1] == state_parts[2]:
		# 	temp_reward -= r_back # dont go back to where you just were

		state_parts = state.split('_')
		if state_parts[1] != state_parts[2]:
			temp_reward += r_back # dont go back to where you just were

		# if next_move == start_location:
		# 	if duration == 'high':
		# 		temp_reward += r_finish
		# 	if duration == 'low':
		# 		temp_reward -= r_finish

		if next_move == start_location:
			if duration == 'high':
				temp_reward += r_finish
			# if duration == 'low':
			# 	temp_reward -= r_finish

		# if duration == 'low':
		# 	# if next_move == close_and_far['furthest_point'] and next_move != close_and_far['closest_point']:
		# 	# 	temp_reward += r_low
		# 	if next_move != close_and_far['closest_point']:
		# 		temp_reward += r_low
		# if duration == 'high':
		# 	# if next_move == close_and_far['closest_point'] and next_move != close_and_far['furthest_point']:
		# 	# 	temp_reward += r_high
		# 	if next_move != close_and_far['furthest_point']:
		# 		temp_reward += r_high
		
#################

		if duration == 'low':
			if next_move == close_and_far_crow['furthest_point'] or next_move == close_and_far_path['furthest_point']:
				temp_reward += r_low

		if duration == 'high':
			if next_move == close_and_far_crow['closest_point'] or next_move == close_and_far_path['closest_point']:
				temp_reward += r_high


		''' Based on chosen move, increment mileage '''

		mileage = increment_mileage(mileage, current_location, next_move)

		''' Update retrace here '''

		# if duration == 'high':
		# 	retrace_duration = 'high'
		# else:
		# 	retrace_duration = 'low'
		# else:
		# 	distance_from_origin = route_distance_between_nodes(get_node_geocoords(next_move), start_coords)
		# 	if distance_from_origin > target_mileage * factor_radius or mileage > target_mileage * factor_duration:
		# 		retrace_duration = 'high'
		# 	else:
		# 		retrace_duration = 'low'

		# if next_move in traveled and path not in pathed and retrace_duration == 'low':
		# 	temp_reward -= r_retrace

		# if next_move in traveled and retrace_duration == 'low':
		# 	temp_reward -= r_retrace

		''' This section determins the Q value of the moves that
		follow the one just chosen. For example if you chose A-B and
		from B you can go from B-C or B-D and the Q values are 0 and
		10 respectively... the max Q value will be 10. This will be
		used to update the Q value for our current state '''

		''' The trick here is to repeat and replace the variable 
		    name 'next_options' so that you don't have to run this 
		    code again later on in this while loop '''

		previous_location = current_location
		current_location = next_move

		next_options = get_next_nodes_2(current_location)

		''' For next options determine their states
		    Depending upon mileage change from immediate
		    move and the move thereafter, the state may change.
		    Hence, we need to determine the duration not just
		    currently, but also after we make the impending move. '''

		current_location_coords = get_node_geocoords(current_location)
		next_states = get_next_states(next_options, current_location, previous_location, current_location_coords, next_step_duration_type, growth_factor)	

		''' For next states, determine either
			next max q or average q '''

		if q_type == 'max':
			future_q_value = get_max_q(next_states)
		else:
			future_q_value = get_average_q(next_states)

		Q[state] = Q[state] + alpha * (temp_reward + gamma \
			* future_q_value - Q[state])

		''' Add chosen path to traveled list (in both directions) '''
		traveled.append(current_location)

		''' Add paths to path list '''
		pathed.append(path)

		if mileage > target_mileage * 1.1: # need to give it a chance to learn in high duration states
			break

		if current_location == start_location:
			break

		count += 1

	end = time.time()

	print 'Trial #: {}, Time Elapsed: {}'.format(trial, str(end-start))

	if trial % 100 == 0 and trial != 0:
		time.sleep(20) # give me a break..

end_run = time.time()

print 'Total Run Time: {}'.format(str(end_run-start_run))

#Write new distances into file
with open("distances_crow.txt", "wb") as f2:
	pickle.dump(distances_crow, f2)
with open("distances_path.txt", "wb") as f3:
	pickle.dump(distances_path, f3)

final_path = []
final_miles = []
def get_final_path(Q):

	print 'FINAL RUN. FINAL RUN. FINAL RUN. FINAL RUN.'
	
	duration = 'low'
	start_location = '66572004'
	previous_location = 'None'
	mileage = 0

	start_coords = get_node_geocoords(start_location)

	final_path.append(start_location)
	current_location = {k:v for k,v in Q.iteritems() if k.startswith(start_location) and k.split('_')[1] == previous_location and k.endswith(duration)}
	current_location = [k for k,v in current_location.iteritems() if v==max(current_location.values())]
	current_location = current_location[0].split('_')[2]
	final_path.append(current_location)

	current_location_coords = get_node_geocoords(current_location)
	mileage = increment_mileage(mileage, start_location, current_location)
	previous_location = start_location

	count = 0
	while current_location != start_location:

		if count == 0:
			duration = determine_duration(duration, mileage, base_target_mileage, current_location_coords, start_coords, recalc_duration_type, growth_factor)
		else:
			previous_location_coords = get_node_geocoords(previous_location)
			duration = determine_duration(duration, mileage, base_target_mileage, current_location_coords, previous_location_coords, recalc_duration_type, growth_factor)

		movement = {k:v for k,v in Q.iteritems() if k.startswith(current_location) and k.split('_')[1] == previous_location and k.endswith(duration)}
		movement = [k for k,v in movement.iteritems() if v==max(movement.values())]
		movement = movement[0].split('_')[2]
		final_path.append(movement)

		mileage = increment_mileage(mileage, current_location, movement)

		current_location = movement
		current_location_coords = get_node_geocoords(current_location)
		previous_location = final_path[len(final_path)-2]

		count += 1
		if mileage > base_target_mileage * 1.5:
			break

		final_miles.append(mileage)

	print 'Current duration: {}, Milgeage: {}, Target Mileage: {}, Duration type: {}, Growth Factor: {}'.format(duration, mileage, base_target_mileage, recalc_duration_type, growth_factor)

get_final_path(Q)


last_path = get_coords_in_route(final_path)
with open ('route.csv', 'wb') as csvfile:
	routewriter = csv.writer(csvfile)
	routewriter.writerow(["LAT", "LON"])
	for el in last_path:
		temp = el.split(',')
		routewriter.writerow([temp[1], temp[0]])






