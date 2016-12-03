# import numpy for calculations
# immport matplot lib for visualizations
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

# define the rewards matrix
# -1 represents null values (no s-a assocated with that transition)
# names of rooom, appropriately, are indexed at 0 :)
r = np.array([[-1, -1, -1, -1,  0,  -1], # represents rewards for transitions from room 0
			  [-1, -1, -1,  0, -1, 100], # represents rewards for transitions from romm 0
			  [-1, -1, -1,  0, -1,  -1], # reward for transition from room 2 to 3 is 0
			  [-1,  0,  0, -1,  0,  -1],
			  [ 0, -1, -1,  0, -1, 100],
			  [-1,  0, -1, -1,  0, 100]]).astype("float32")
# create 0 matrix to initialize the aquired knowledge matrix
q = np.zeros_like(r)


def update_q(state, next_state, action, alpha, gamma):
	rsa = r[state, action]
	qsa = q[state, action]
	# update your q for this action between these states
	new_q = qsa + alpha + (rsa + gamma + max(q[next_state, :]) - qsa)
	q[state, action] = new_q
	rn = q[state][q[state] > 0] / np.sum(q[state][q[state] > 0])
	q[state][q[state] > 0] = rn
	return r[state, action]


def show_traverse():
    # show all the greedy traversals
    for i in range(len(q)):
        current_state = i
        traverse = "%i -> " % current_state
        n_steps = 0
        while current_state != 5 and n_steps < 20:
            next_state = np.argmax(q[current_state])
            current_state = next_state
            traverse += "%i -> " % current_state
            n_steps = n_steps + 1
        # cut off final arrow
        traverse = traverse[:-4]
        print("Greedy traversal for starting state %i" % i)
        print(traverse)
        print("")


gamma = 0.1
alpha = 1.0 # this is the learning rate - if environment is deterministic use 1.0 otherwise 0 < x < 1
            # if envirnoment is uncertain (stochastic)... maybe you don't want to trust everything you learn the first time 
n_episodes = 1000 # each time the agent finds the outdoors, new episode ensues
n_states = 6 # there are six rooms
n_actions = 6 # there are six possible movements that can be made
epsilon = 0.2 # greedy parameter - higher value makes the algorithm do more exploration
random_state = np.random.RandomState(1999) # set random seed

for e in range(int(n_episodes)): # loop algorithm for number of episodes declared
	states = list(range(n_states)) # create list of the states
	random_state.shuffle(states) # shuffle states list in order to pick a random state
	current_state = states[0] # choose a random state (for initialization)
	goal = False # until reach goal (outside), keep moving from room to room
	# show_traverse()
	# show_q()
	while not goal:
		valid_moves = r[current_state] >= 0 # based on matrix row, only allow moves to states that exist (above -1)
		if random_state.rand() < epsilon: # explore
			actions = np.array(list(range(n_actions))) # make list of actions
			actions = actions[valid_moves == True] # filter only is action exists (action goes to location > -1)
			if type(actions) is int: # if only one option, must make that move
				actions = [actions]
			random_state.shuffle(actions) # if more than one action possible, choose one randomly
			action = actions[0] # following above line (probably nicer way to do this...)
			next_state = action # simply creates additional variable next_state to pass to update_q funtions
		else:
			if np.sum(q[current_state]) > 0: # if there is a move from the current state (row) that will give us a reward, take it
				action = np.argmax(q[current_state])
			else: # otherwise just make a move randomly like above
				actions = np.array(list(range(n_actions)))
				actions = actions[valid_moves == True]
				if type(actions) is int:
					actions = [actions]
				random_state.shuffle(actions)
				action = actions[0]
			next_state = action
		# current_state is the row you are in
		# next_state is the column you choose to move to
		# action is also the column you will choose to move to (I THINK)
		# what is alpha?
		# what is gamma?
		reward = update_q(current_state, next_state, action,
						  alpha=alpha, gamma=gamma)
		if reward > 1: # goal (outside) has reward of 100, everything else <1
			goal = True
		current_state = next_state # make move from current to next and loop again

print(q)
show_traverse()

