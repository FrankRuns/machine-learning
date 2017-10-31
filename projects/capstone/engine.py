#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
docker run -t -i -p 5000:5000 -v $(pwd):/data osrm/osrm-backend osrm-routed /data/massachusetts-latest.osrm
docker run -t -i -p 5000:5000 -v $(pwd):/data osrm/osrm-backend osrm-routed /data/new-york-latest.osrm    # testing ny
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
# filename = 'ny_streets.osm' # testing ny

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
# tree2 = ET.parse('raw_ny_osm') # testing ny
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

''' Above chuncks of code used for writing project document '''


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


#########################################################
### Functions to determine distance from origin START ###
#########################################################

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

#######################################################
### Functions to determine distance from origin END ###
#######################################################


##########################################
### Functions to plot final path START ###
##########################################

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

########################################
### Functions to plot final path END ###
########################################


def filter_list(list1, list2):
	''' Identifies elements of list1 that are also in list 2.
		Used in get_next_nodes. '''

	templist = []
	for el in list1:
		if el in list2:
			templist.append(el)
	return templist


# So we don't have to run the extraction multiple times,
# declare the list of intersection nodes as global variable
intersection_nodes = extract_intersections(verbose=False)

def get_next_nodes(current_location):

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
			# reward = reward + (r_base * count)
			if count > 0:
				reward = 30000

			return reward

	return 0


def choose_next_node(rval, eps, moves, Q, tmp_states):
	''' Determine next node based on explore / exploit decision
		if exploiting, use Q values to make next choice '''

	if rval < eps:
		# numpy.random.seed(trial)
		movement = numpy.random.choice(moves)
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
				# numpy.random.seed(trial)
				movement = numpy.random.choice(moves)
		else:
			# numpy.random.seed(trial)
			movement = numpy.random.choice(moves)

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


def get_next_states(next_options, where_you_are, where_you_were, coords_where_you_are):

	next_states = []
	for el in next_options:
		super_temp_coords = get_node_geocoords(el)

		if '{}, {}'.format(coords_where_you_are, super_temp_coords) in distances_path.keys():
			super_temp_duration_distance = distances_path['{}, {}'.format(coords_where_you_are, super_temp_coords)]
		else:
			super_temp_duration_distance = route_distance_between_nodes(coords_where_you_are, super_temp_coords)
			distances_path['{}, {}'.format(coords_where_you_are, super_temp_coords)] = super_temp_duration_distance

		super_temp_mileage = mileage + super_temp_duration_distance

		# if super_temp_mileage >= factor_duration * target_mileage:
		# 	next_duration = 'high'
		# else:
		# 	next_duration = 'low'

		next_duration = numpy.random.choice(['low','high'])	

		# next_duration = duration

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


def determine_duration(duration, mileage, target_mileage, factor_duration, crow_duration):

	# between 0.5 miles and 0.75 miles runner should not be near origin
	# if they are, increase duration factor to engourage moveing away from origin
	# if crow_duration <= 0.25 and mileage > target_mileage * 0.5:
	# 	temp_duration = factor_duration * 1.3
	# else:
	# 	temp_duration = factor_duration * 1.0

	temp_duration = factor_duration

	if mileage > temp_duration * target_mileage:
		new_duration = 'high'
	else:
		new_duration = 'low'

	# print 'Temp duration = {}, duration = {}'.format(temp_duration, new_duration)

	return new_duration


def get_close_far(path_type, next_options, previous_location):

	if len(next_options) > 1:
		next_options_san_prev = [i for i in next_options if i != previous_location]
	else:
		next_options_san_prev = next_options

	if path_type == 'path_wise':

		holdme = {}
		for option in next_options_san_prev:
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
		for option in next_options_san_prev:
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

# if os.path.exists('distances_crow.txt'):
# 	with open("distances_crow.txt", "rb") as f:
# 		distances_crow = pickle.load(f)
# else:
# 	distances_crow = {}

# if os.path.exists('distances_path.txt'):
# 	with open("distances_path.txt", "rb") as f:
# 		distances_path = pickle.load(f)
# else:
# 	distances_path = {}

distances_crow = {}
distances_path = {}
neighbor_nodes = {}
rewards = {}
list_of_coords = {}

# define a list to capture Q tables
list_of_Qs = []

# define paramters
errors = [] # stores error in event call to routing service fails
start_location = '66572004' # stone place, melrose
# start_location = '213774020' # 40.87651, -73.31783 # Jeanne Pl. E. Northport NY NEEDS TO START AT INTERSECTION
q_initialization_value = 0
# target_mileage = 2.0
gamma = 0.30
alpha = 0.80
n_trials = 100
target_mileage = 3.0

# define reward structure
r_back = 50000
# r_finish = 10000
# r_low = 30000
# r_high = 45000

''' Run similation '''

start_run = time.time()

for i in range(8):

	# create policy table
	Q = {}

	for trial in range(n_trials):

		''' Epsilon must decay in order to find final path '''

		epsilon = math.cos(1.59/n_trials*trial)

		''' Define start node, coords for 
		    start location '''

		start_coords = get_node_geocoords(start_location)

		''' Define miles, initial duration
		    Duration is low if <factor_duration through target miles '''

		mileage = 0
		duration = 'low'
		pathed = []

		''' From start location, where can we go next? 
		    Save next possible nodes to a list. This is used to 
		    determine where to go next '''

		next_options = get_next_nodes(start_location)

		''' Based on start location, next options, and 
		    current mileage. This is used to determine where to
		    go next '''

		temp_states = []
		for el in next_options:
			temp_state = '{}_{}_{}_{}'.format(start_location, None, el, duration)
			temp_states.append(temp_state)

		''' Define random value for explore / exploit decision '''

		rvalue = numpy.random.rand(1)[0]

		''' Choose next move '''

		initial_move = choose_next_node(rvalue, epsilon, next_options, \
			Q, temp_states)

		''' Create path and append to pathed list '''
		path = '{}_{}_{}'.format(start_location, None, initial_move)
		pathed.append(path)

		''' Update state. State = current position, where you were, 
	        where youre going, duration '''

		state = '{}_{}_{}_{}'.format(start_location, None, initial_move, \
			duration)	

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

		next_options = get_next_nodes(initial_move)

		''' For next options determine their states
		    Depending upon mileage change from immediate
		    move and the move thereafter, the state may change.
		    Hence, we need to determine the duration not just
		    currently, but also after we make the impending move.
		    Note that if you use path_wise or crow_wise it will nearly
		    always be the same. Crow is faster so crow it. '''

		initial_move_coords = get_node_geocoords(initial_move)
		next_states = get_next_states(next_options, initial_move, start_location, initial_move_coords)

		''' For next states, determine either
			next max q and update policy table '''

		future_q_value = get_max_q(next_states)

		Q[state] = Q[state] + alpha * (temp_reward + gamma \
			* future_q_value - Q[state])

		''' Update current location '''

		current_location = initial_move
		previous_location = start_location

		count = 0
		while start_location != current_location:

			''' Determine duration '''
			# duration = determine_duration(duration, mileage, target_mileage, factor_duration)
			# if mileage > factor_duration * target_mileage:
			# 	duration = 'high'
			# else:
			# 	duration = 'low'	

			duration = numpy.random.choice(['low','high'])		

			''' Determine closest and furthest point from start location '''

			close_and_far_path = get_close_far('path_wise', next_options, previous_location)
			close_and_far_crow = get_close_far('crow_wise', next_options, previous_location)

			''' Define random value for explore / exploit decision '''

			rvalue = numpy.random.rand(1)[0]

			''' Choose next move. Based on current location,
			    next options, and current mileage. This is used
			    to determine where to go next '''

			next_move = choose_next_node(rvalue, epsilon, next_options, \
				Q, next_states)

			''' Create path and append to pathed list '''
			path = '{}_{}_{}'.format(current_location, previous_location, next_move)

			''' Update current and previous location while restating
			    the path (in either direction) and state '''

			state = '{}_{}_{}_{}'.format(current_location, previous_location, next_move, \
				duration)

			''' Add state to tempQ table if it doesn't exist '''
			if not state in Q.keys():
				Q[state] = q_initialization_value

			''' Get base reward for chosen move '''

			temp_reward = get_reward(current_location, next_move)
			if path in pathed:
				temp_reward = temp_reward/pathed.count(path)

			''' Get adjusted reward if going back or retracing steps '''

			# Don't go backwards
			state_parts = state.split('_')
			if state_parts[1] == state_parts[2]:
				temp_reward -= r_back

			# if next_move == start_location:
			# 	if duration == 'high':
			# 		temp_reward += r_finish

			# If in first part of run, don't move closer to origin
			if duration == 'low':
				if next_move == close_and_far_path['closest_point'] and \
				next_move == close_and_far_crow['closest_point']:
					temp_reward -= 2000

			# if in first part of run move further from origin
			if duration == 'low':
				if next_move == close_and_far_path['furthest_point'] and \
				next_move == close_and_far_crow['furthest_point']:
					temp_reward += 2000

			# in in later stages of run move closer to origin
			if duration == 'high':
				if next_move == close_and_far_path['closest_point']:# or \
				# next_move == close_and_far_path['closest_point']:
					temp_reward += 9000 

			''' Based on chosen move, increment mileage '''

			mileage = increment_mileage(mileage, current_location, next_move)

			''' The trick here is to repeat and replace the variable 
			    name 'next_options' so that you don't have to run this 
			    code again later on in this while loop '''

			previous_location = current_location
			current_location = next_move

			next_options = get_next_nodes(current_location)

			''' For next options determine their states
			    Depending upon mileage change from immediate
			    move and the move thereafter, the state may change.
			    Hence, we need to determine the duration not just
			    currently, but also after we make the impending move. '''

			current_location_coords = get_node_geocoords(current_location)
			next_states = get_next_states(next_options, current_location, previous_location, \
				current_location_coords)	

			''' For next states, determine either
				next max q and update policy table '''

			future_q_value = get_max_q(next_states)
			if path in pathed:
				future_q_value = future_q_value/pathed.count(path)			

			Q[state] = Q[state] + alpha * (temp_reward + gamma \
				* future_q_value - Q[state])

			''' Add path to list of previously traveled paths '''
			pathed.append(path)

			crow_distance = crow_distance_between_nodes(current_location_coords, start_coords)
			# crow_duration = crow_distance / target_mileage
			print 'Crow dristance: {}'.format(crow_distance)

			if crow_distance > ( target_mileage / 2.0 ) * 1.5:
				break

			if current_location == start_location:
				break

			count += 1

			if count > 100 * target_mileage:
				break

		if trial % 100 == 0 and trial != 0:
			time.sleep(5) # give me a break..

		print 'Session: {}, trial: {}, duration: {}'.format(i, trial, duration)

	list_of_Qs.append(Q)

end_run = time.time()
print 'Total Run Time: {}'.format(str(end_run-start_run))

# combine all Q tables into master Q table taking the form {'key': [value1, value2, etc.]}
from collections import defaultdict
master_Q = defaultdict(list)
for el in list_of_Qs:
	for key, value in el.iteritems():
		master_Q[key].append(value)

# take the average of all values of each key in master table
for key, value in master_Q.iteritems():
	master_Q[key] = numpy.mean(value)

# #Write new distances into file
# with open("distances_crow.txt", "wb") as f2:
# 	pickle.dump(distances_crow, f2)
# with open("distances_path.txt", "wb") as f3:
# 	pickle.dump(distances_path, f3)

''' Policy is determined, see where it runs you '''

factor_duration = 0.7
final_path = []
final_miles = []

def get_final_path(Q, target_mileage):

	print 'FINAL RUN. FINAL RUN. FINAL RUN. FINAL RUN.'
	
	duration = 'low'
	previous_location = 'None'
	mileage = 0

	start_coords = get_node_geocoords(start_location)

	final_path.append(start_location)

	current_location = {k:v for k,v in Q.iteritems() if k.startswith(start_location) and \
		k.split('_')[1] == previous_location and k.endswith(duration)}
	current_location = [k for k,v in current_location.iteritems() if v==max(current_location.values())]
	current_location = current_location[0].split('_')[2]

	final_path.append(current_location)

	current_location_coords = get_node_geocoords(current_location)
	mileage = increment_mileage(mileage, start_location, current_location)
	previous_location = start_location

	count = 0
	while current_location != start_location:

		crow_distance = crow_distance_between_nodes(current_location_coords, start_coords)
		crow_duration = crow_distance / target_mileage

		''' Determine duration '''
		duration = determine_duration(duration, mileage, target_mileage, factor_duration, crow_duration)

		movement = {k:v for k,v in Q.iteritems() if k.startswith(current_location) and \
			k.split('_')[1] == previous_location and k.endswith(duration)}
		movement = [k for k,v in movement.iteritems() if v==max(movement.values())]
		movement = movement[0].split('_')[2]

		final_path.append(movement)

		mileage = increment_mileage(mileage, current_location, movement)

		current_location = movement
		current_location_coords = get_node_geocoords(current_location)
		previous_location = final_path[len(final_path)-2]

		count += 1

		if mileage > target_mileage * 1.5:
			break

		final_miles.append(mileage)

	print mileage
	return (mileage, final_path)

get_final_path(master_Q, target_mileage)

last_path = get_coords_in_route(final_path)
with open ('route.csv', 'wb') as csvfile:
	routewriter = csv.writer(csvfile)
	routewriter.writerow(["LAT", "LON"])
	for el in last_path:
		temp = el.split(',')
		routewriter.writerow([temp[1], temp[0]])

#############

# all_runs = {}
# for rund in [0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,5.5,6.0]:

# 	final_path = []
# 	final_miles = []

# 	temp_final = get_final_path(master_Q, rund)
# 	all_runs[temp_final[0]] = temp_final[1]

# for k,v in all_runs.iteritems():
# 	print k

''' Write final path coordinates to csv to visualize '''



# last_path = get_coords_in_route(all_runs[2.877569101])
# with open ('route.csv', 'wb') as csvfile:
# 	routewriter = csv.writer(csvfile)
# 	routewriter.writerow(["LAT", "LON"])
# 	for el in last_path:
# 		temp = el.split(',')
# 		routewriter.writerow([temp[1], temp[0]])






