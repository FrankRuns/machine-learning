import random

# create q-table to store state-policy pairs
Q = {}

# create matrix of distances between nodes
distance = {'(A,B)':1,'(B,C)':1,'(C,D)':1,'(D,E)':1,
		    '(F,G)':1,'(G,H)':1,'(H,I)':1,'(I,J)':1,
		    '(K,L)':1,'(L,M)':1,'(M,N)':1,'(N,O)':1,
		    '(P,Q)':1,'(Q,R)':1,'(R,S)':1,'(S,T)':1,
		    '(U,V)':1,'(V,W)':1,'(W,X)':1,'(X,Y)':1,
			'(B,A)':1,'(C,B)':1,'(D,C)':1,'(E,D)':1,
		    '(G,F)':1,'(H,G)':1,'(I,H)':1,'(J,I)':1,
		    '(L,K)':1,'(M,L)':1,'(N,M)':1,'(O,N)':1,
		    '(Q,P)':1,'(R,Q)':1,'(S,R)':1,'(T,S)':1,
		    '(V,U)':1,'(W,V)':1,'(X,W)':1,'(Y,X)':1,
		    '(A,F)':1,'(F,K)':1,'(K,P)':1,'(P,U)':1,
		    '(B,G)':1,'(G,L)':1,'(L,Q)':1,'(Q,V)':1,
		    '(C,H)':1,'(H,M)':1,'(M,R)':1,'(R,W)':1,
		    '(D,I)':1,'(I,N)':1,'(N,S)':1,'(S,X)':1,
		    '(E,J)':1,'(J,O)':1,'(O,T)':1,'(T,Y)':1,
		    '(F,A)':1,'(K,F)':1,'(P,K)':1,'(U,P)':1,
		    '(G,B)':1,'(L,G)':1,'(Q,L)':1,'(V,Q)':1,
		    '(H,C)':1,'(M,H)':1,'(R,M)':1,'(W,R)':1,
		    '(I,D)':1,'(N,I)':1,'(S,N)':1,'(X,S)':1,
		    '(J,E)':1,'(O,J)':1,'(T,O)':1,'(Y,T)':1}

# create matrix of rewards for actions between nodes
rewards =  {'(A,B)':0.0,'(B,C)':0.0,'(C,D)':0.0,'(D,E)':0.0,
		    '(F,G)':0.0,'(G,H)':0.0,'(H,I)':0.0,'(I,J)':0.0,
		    '(K,L)':0.0,'(L,M)':0.0,'(M,N)':0.0,'(N,O)':0.0,
		    '(P,Q)':0.0,'(Q,R)':0.0,'(R,S)':20.0,'(S,T)':20.0,
		    '(U,V)':0.0,'(V,W)':0.0,'(W,X)':0.0,'(X,Y)':0.0,
			'(B,A)':0.0,'(C,B)':0.0,'(D,C)':0.0,'(E,D)':0.0,
		    '(G,F)':0.0,'(H,G)':0.0,'(I,H)':0.0,'(J,I)':0.0,
		    '(L,K)':0.0,'(M,L)':0.0,'(N,M)':0.0,'(O,N)':0.0,
		    '(Q,P)':0.0,'(R,Q)':0.0,'(S,R)':20.0,'(T,S)':20.0,
		    '(V,U)':0.0,'(W,V)':0.0,'(X,W)':0.0,'(Y,X)':0.0,
		    '(A,F)':0.0,'(F,K)':0.0,'(K,P)':0.0,'(P,U)':20.0,
		    '(B,G)':0.0,'(G,L)':40.0,'(L,Q)':0.0,'(Q,V)':0.0,
		    '(C,H)':0.0,'(H,M)':0.0,'(M,R)':0.0,'(R,W)':0.0,
		    '(D,I)':0.0,'(I,N)':0.0,'(N,S)':0.0,'(S,X)':0.0,
		    '(E,J)':0.0,'(J,O)':5.0,'(O,T)':0.0,'(T,Y)':0.0,
		    '(F,A)':0.0,'(K,F)':0.0,'(P,K)':0.0,'(U,P)':20.0,
		    '(G,B)':0.0,'(L,G)':40.0,'(Q,L)':0.0,'(V,Q)':0.0,
		    '(H,C)':0.0,'(M,H)':0.0,'(R,M)':0.0,'(W,R)':0.0,
		    '(I,D)':0.0,'(N,I)':0.0,'(S,N)':0.0,'(X,S)':0.0,
		    '(J,E)':0.0,'(O,J)':20.0,'(T,O)':0.0,'(Y,T)':0.0}

# create matrix of distance from every node to the start/end location
# pathwise - in order to tally total miles run
fromstart_pathwise = {'A':4.0,'B':3.0,'C':2.0,'D':1.0,
		              'E':2.0,'F':3.0,'G':2.0,'H':1.0,
		              'I':0.0,'J':1.0,'K':4.0,'L':3.0,
		              'M':2.0,'N':1.0,'O':2.0,'P':5.0,
		              'Q':4.0,'R':3.0,'S':2.0,'T':3.0,
		              'U':6.0,'V':5.0,'W':4.0,'X':3.0,
		              'Y':4.0}

# create matrix of distance from every node to the start/end location
# as the crow flys - more informitive especially in grid scenario
fromstart_crow = {'A':3.16,'B':2.23,'C':1.41,'D':1.00,
		          'E':1.41,'F':3.00,'G':2.00,'H':1.00,
		          'I':0.00,'J':1.00,'K':3.16,'L':2.23,
		          'M':1.41,'N':1.00,'O':1.41,'P':3.61,
		          'Q':2.83,'R':2.23,'S':2.00,'T':2.23,
		          'U':4.24,'V':3.61,'W':3.16,'X':3.00,
		          'Y':3.16}

# for reference, this is the grid of nodes layout
# A F K P U
# B G L Q V
# C H M R W
# D I N S X
# E J O T Y

# Note to self
# For a 8 mile run, I beleive the optimal path is
# ['I','J','O','T','S','R','M','H','I']

# define tuning parameters
gamma = 0.6
alpha = 0.7
epsilon = 0.8
factor = 0.5

# define other parameters
target_mileage = 8

# set number of trials
n_trials = 10000
count = 0

# add next_move state to q-table
def add_next_move(next_moves_list, prev_move, the_duration):
	for move in next_moves_list:
		fstate = move + ' ' + prev_move + ' ' + str(the_duration)
		if fstate not in qtemp.keys():
			qtemp[fstate] = 0.0	

def get_max_q(qtemp_list, next_moves_list):
	maxQ_next = dict((k,v) for k,v in qtemp_list.iteritems() if k[:5] in next_moves_list)
	maxQ_next = [v for k,v in maxQ_next.iteritems() if v == max(maxQ_next.values())][0]	

	return maxQ_next

# simulation
# each run will use an initial random move followed by a series of
# decisions between split points. Starting location is I. The 
# while loop will run until current location (after the initial 
# move) is equal to the start location. Use lots of print statements
# to understand what's going on.
for i in range(n_trials):

	# define start location
	start_location = 'I'
	previous_location = None
	traveled = []

	# define start mileage and target mileage
	mileage = 0
	duration = 'low'

	# create temporary q-table
	# at end of run if mileage = target mileage replace q-table with temp q-table
	# reason: if mileage != target mileage new knowledge is counter productive
	qtemp = Q.copy()

	# make initial random move - update previous and current location
	rvalue = random.random()
	valid_moves = [ k for k,v in distance.items() if '('+start_location in k ]
	if rvalue < epsilon:
		initial_move = random.choice(valid_moves)
	else:
		if len(qtemp) > 0:
			initial_move = dict((k,v) for k,v in qtemp.iteritems() if k[:5] in valid_moves)
			initial_move = [k for k,v in initial_move.iteritems() if v == max(initial_move.values())][0][:5]
		else:
			initial_move = random.choice(valid_moves)
	previous_location = initial_move[1]
	current_location = initial_move[3]

	# create state if doesn't exist
	state = initial_move + ' ' + str(None) + ' ' + str('low')
	# state = initial_move + ' ' + str('low')
	if state not in qtemp.keys():
		qtemp[state] = 0.0

	# add state to traveled paths
	traveled.append(''.join(sorted(state[1]+state[3])))

	# identify next moves from initial move
	next_moves = [k for k,v in distance.items() if current_location+',' in k]
	# next_moves = [el for el in next_moves if el[3] != previous_location]
	# next_moves = [el for el in next_moves if ''.join(sorted(el[1]+el[3])) not in traveled]

	# create 'next' states if they do not exist in q-table
	add_next_move(next_moves, traveled[len(traveled)-1], duration)

	# get max q-value in next moves
	maxQ_next = get_max_q(qtemp, next_moves)

	# update q-table on initial move
	qtemp[state] = qtemp[state] + alpha * (rewards[initial_move] + gamma * maxQ_next - qtemp[state])

	# increment mileage
	mileage += distance[initial_move]
	print 'Total miles after initial movement are: ' + str(mileage)

	while start_location != current_location:

		# identify valid moves
		valid_moves = [ k for k,v in distance.items() if '('+current_location in k ]
		# valid_moves = [el for el in valid_moves if el[3] != previous_location]
		# valid_moves = [el for el in valid_moves if ''.join(sorted(el[1]+el[3])) not in traveled]		

		print 'The set of valid moves from current position are:'
		print valid_moves

		# determine state of duration and closest / furthest valid moves from origin
		if mileage <= factor * target_mileage:
			duration = 'low'
		else:
			duration = 'high'
		print 'Duration = ' + str(duration)

		points = [i[3] for i in valid_moves]
		holdme = {}

		for k,v in fromstart_crow.iteritems():
			for el in points:
				if k==el:
					holdme[k]=v

		closest_point = min(holdme, key=holdme.get)
		furthest_point = max(holdme, key=holdme.get)

		# create state if doesn't exist
		add_next_move(valid_moves, traveled[len(traveled)-1], duration)

		# select next move
		rvalue = random.random()

		# if you exploit too much... you get stuck
		# sivers talks about quitting something you love so 
		# you have time to find other stuff that you love - this is that

		if rvalue < epsilon:
			# action = random.choice(valid_moves)
			rvalue2 = random.random()
			if rvalue2 < 0.1:
				action = random.choice(valid_moves)
			else:
				if duration == 'high':
					action = str('('+current_location+','+closest_point+')')
				else:
					action = str('('+current_location+','+furthest_point+')')
			print 'Epsilon > rvalue.. exploring. Taking random action'
			print 'The action is: '
			print action
		else:
			print 'Exploiting...'
			action = dict((k,v) for k,v in qtemp.iteritems() if k[:5] in valid_moves)
			action = [k for k,v in action.iteritems() if v == max(action.values())][0][:5]
			print 'ACTION!!!!!!! is: '
			print action

		# set state
		state = action + ' ' + traveled[len(traveled)-1] + ' ' + str(duration)

		# add state to traveled paths
		traveled.append(''.join(sorted(state[1]+state[3])))

		print 'TRAVELED'
		print traveled

		# identify next moves
		next_moves = [ k for k,v in distance.items() if action[3]+',' in k ]
		# next_moves = [el for el in next_moves if el[3] != previous_location]
		# next_moves = [el for el in next_moves if ''.join(sorted(el[1]+el[3])) not in traveled]

		# if len(next_moves) == 0:
		# 	loop = 'bad'
		# 	break

		# create 'next' states if they do not exist in q-table
		add_next_move(next_moves, traveled[len(traveled)-1], duration)

		# get max q-value in next moves
		maxQ_next = get_max_q(qtemp, next_moves)

		# adjust reward structure based on state of distance from start location
		if duration == 'low':
			if action[3] == furthest_point and action[3] != closest_point:
				temp_reward = rewards[action] + 5
			else:
				temp_reward = rewards[action]
		elif duration == 'high':
			if action[3] == closest_point and action[3] != furthest_point:
				temp_reward = rewards[action] + 15
			else:
				temp_reward = rewards[action]
		else:
			temp_reward = rewards[action]

		# in training you may have to let agent go backwards to teach it that going
		# backwards is bad

		if state[3] == state[6] or state[3] == state[7]:
			temp_reward = temp_reward - 100

		# update q-table
		qtemp[state] = qtemp[state] + alpha * (temp_reward + gamma * maxQ_next - qtemp[state])

		# increment mileage
		mileage += distance[action]
		print 'Total miles after movement are: ' + str(mileage)

		previous_location = action[1]
		current_location = action[3]

		print 'Previous state now: ' + str(previous_location)
		print 'Current location now: ' + str(current_location)

		loop = 'good'

	if mileage >= target_mileage - 1.0 and mileage <= target_mileage + 1.0:
		print "WITHIN TRGET RANGE!!!, WITHIN TRGET RANGE!!!, WITHIN TRGET RANGE!!!, WITHIN TRGET RANGE!!!, "
		Q = qtemp.copy()
		count += 1

print 'Count = '
print count
print 'Resulting Q-table: '
print Q

def tester(policy_dict):
	
	start_loc = 'I'
	mileage = 0
	duration = 'low'
	path = ['I']
	current_loc = 'I'
	counter = 0

	while path.count('I') < 2 and counter < 50: 
		
		if len(path) < 2:
			moves = dict((k,v) for k,v in policy_dict.iteritems() if k.startswith('('+current_loc) and str(None) in k and str(duration) in k)
		else:
			moves = dict((k,v) for k,v in policy_dict.iteritems() if k.startswith('('+current_loc) and ''.join(sorted(path[len(path)-2:])) in k[6:8] and str(duration) in k)
		next_move = [k[3] for k,v in moves.iteritems() if v == max(moves.values())][0]

		path.append(next_move)
		mileage += 1.0
		if mileage <= factor * target_mileage:
			duration = 'low'
		else:
			duration = 'high'
		current_loc = next_move
		counter += 1
		print path

	return path

tester(Q)