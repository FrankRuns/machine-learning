import random

# create q-table to store state-policy pairs
Q = {}

# create matrix of distances between nodes
distance = {'(A,B)':0.25,'(B,C)':0.25,'(C,D)':0.25,'(D,E)':0.25,
		    '(F,G)':0.25,'(G,H)':0.25,'(H,I)':0.25,'(I,J)':0.25,
		    '(K,L)':0.25,'(L,M)':0.25,'(M,N)':0.25,'(N,O)':0.25,
		    '(P,Q)':0.25,'(Q,R)':0.25,'(R,S)':0.25,'(S,T)':0.25,
		    '(U,V)':0.25,'(V,W)':0.25,'(W,X)':0.25,'(X,Y)':0.25,
			'(B,A)':0.25,'(C,B)':0.25,'(D,C)':0.25,'(E,D)':0.25,
		    '(G,F)':0.25,'(H,G)':0.25,'(I,H)':0.25,'(J,I)':0.25,
		    '(L,K)':0.25,'(M,L)':0.25,'(N,M)':0.25,'(O,N)':0.25,
		    '(Q,P)':0.25,'(R,Q)':0.25,'(S,R)':0.25,'(T,S)':0.25,
		    '(V,U)':0.25,'(W,V)':0.25,'(X,W)':0.25,'(Y,X)':0.25,
		    '(A,F)':0.25,'(F,K)':0.25,'(K,P)':0.25,'(P,U)':0.25,
		    '(B,G)':0.25,'(G,L)':0.25,'(L,Q)':0.25,'(Q,V)':0.25,
		    '(C,H)':0.25,'(H,M)':0.25,'(M,R)':0.25,'(R,V)':0.25,
		    '(D,I)':0.25,'(I,N)':0.25,'(N,S)':0.25,'(S,X)':0.25,
		    '(E,J)':0.25,'(J,O)':0.25,'(O,T)':0.25,'(T,Y)':0.25,
		    '(F,A)':0.25,'(K,F)':0.25,'(P,K)':0.25,'(U,P)':0.25,
		    '(G,B)':0.25,'(L,G)':0.25,'(Q,L)':0.25,'(V,Q)':0.25,
		    '(H,C)':0.25,'(M,H)':0.25,'(R,M)':0.25,'(V,R)':0.25,
		    '(I,D)':0.25,'(N,I)':0.25,'(S,N)':0.25,'(X,S)':0.25,
		    '(J,E)':0.25,'(O,J)':0.25,'(T,O)':0.25,'(Y,T)':0.25}

# create matrix of rewards for actions between nodes
rewards =  {'(A,B)':0.0,'(B,C)':0.0,'(C,D)':0.0,'(D,E)':0.0,
		    '(F,G)':0.0,'(G,H)':0.0,'(H,I)':0.0,'(I,J)':0.0,
		    '(K,L)':0.0,'(L,M)':0.0,'(M,N)':0.0,'(N,O)':0.0,
		    '(P,Q)':0.0,'(Q,R)':0.0,'(R,S)':5.0,'(S,T)':5.0,
		    '(U,V)':0.0,'(V,W)':0.0,'(W,X)':0.0,'(X,Y)':0.0,
			'(B,A)':0.0,'(C,B)':0.0,'(D,C)':0.0,'(E,D)':0.0,
		    '(G,F)':0.0,'(H,G)':0.0,'(I,H)':0.0,'(J,I)':0.0,
		    '(L,K)':0.0,'(M,L)':0.0,'(N,M)':0.0,'(O,N)':0.0,
		    '(Q,P)':0.0,'(R,Q)':0.0,'(S,R)':5.0,'(T,S)':5.0,
		    '(V,U)':0.0,'(W,V)':0.0,'(X,W)':0.0,'(Y,X)':0.0,
		    '(A,F)':0.0,'(F,K)':0.0,'(K,P)':0.0,'(P,U)':5.0,
		    '(B,G)':0.0,'(G,L)':5.0,'(L,Q)':0.0,'(Q,V)':0.0,
		    '(C,H)':0.0,'(H,M)':0.0,'(M,R)':0.0,'(R,V)':0.0,
		    '(D,I)':0.0,'(I,N)':0.0,'(N,S)':0.0,'(S,X)':0.0,
		    '(E,J)':0.0,'(J,O)':5.0,'(O,T)':0.0,'(T,Y)':0.0,
		    '(F,A)':0.0,'(K,F)':0.0,'(P,K)':0.0,'(U,P)':5.0,
		    '(G,B)':0.0,'(L,G)':5.0,'(Q,L)':0.0,'(V,Q)':0.0,
		    '(H,C)':0.0,'(M,H)':0.0,'(R,M)':0.0,'(V,R)':0.0,
		    '(I,D)':0.0,'(N,I)':0.0,'(S,N)':0.0,'(X,S)':0.0,
		    '(J,E)':0.0,'(O,J)':5.0,'(T,O)':0.0,'(Y,T)':0.0}

# create matrix of distance from every node to the start/end location
fromstart = {'A':1.00,'B':0.75,'C':0.50,'D':0.25,
		     'E':0.50,'F':0.75,'G':0.50,'H':0.25,
		     'I':0.00,'J':0.25,'K':1.00,'L':0.75,
		     'M':0.50,'N':0.25,'O':0.50,'P':1.25,
		     'Q':1.00,'R':0.75,'S':0.50,'T':0.75,
		     'U':1.50,'V':1.25,'W':1.00,'X':0.75,
		     'Y':1.00}

# for reference, this is the grid of nodes layout
# A F K P U
# B G L Q V
# C H M R W
# D I N S X
# E J O T Y

# Note to self
# For a 2 mile run, I beleive the optimal path is
# ['I','J','O','T','S','R','M','H','I']

# define tuning parameters
gamma = 0.7
alpha = 1.0
epsilon = 0.7
dfactor_low = 0.33
dfactor_high = 0.66

# set number of trials
n_trials = 5000

# use count to collect number of instances mileage = target mileage
count = 0

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

	# define start mileage and target mileage
	mileage = 0
	target_mileage = 2

	print 'Start location is ' + str(start_location)
	print 'Start mileage is ' + str(mileage)
	print 'Target mileage is ' + str(target_mileage)

	# create temporary q-table
	# at end of run if mileage = target mileage replace q-table with temp q-table
	# reason: if mileage != target mileage new knowledge is counter productive
	qtemp = Q.copy()

	# make initial random move - update previous and current location
	initial_move = random.choice([ k for k,v in distance.items() if '('+start_location in k ])
	previous_location = initial_move[1]
	current_location = initial_move[3]

	# create state if doesn't exist
	state = initial_move + ' ' + str('low')
	if state not in qtemp.keys():
		qtemp[state] = 0.0

	# identify next moves from initial move
	next_moves = [k for k,v in distance.items() if current_location+',' in k]
	next_moves = [el for el in next_moves if el[3] != previous_location]
	print 'The next moves from action movement are'
	print next_moves

	# create 'next' states if they do not exist in q-table
	for move in next_moves:
		fstate = move + ' ' + str('low')
		if fstate not in qtemp.keys():
			qtemp[fstate] = 0.0

	# get max q-value in next moves
	maxQ_next = dict((k,v) for k,v in qtemp.iteritems() if k[:5] in next_moves)
	maxQ_next = [v for k,v in maxQ_next.iteritems() if v == max(maxQ_next.values())][0]
	print 'Initial max q value is: '
	print maxQ_next

	# update q-table on initial move
	qtemp[state] = qtemp[state] + alpha * (rewards[initial_move] + gamma * maxQ_next - qtemp[state])

	# increment mileage
	mileage += distance[initial_move]
	print 'Total miles after initial movement are: ' + str(mileage)

	while start_location != current_location:

		# identify valid moves
		valid_moves = [ k for k,v in distance.items() if '('+current_location in k ]
		valid_moves = [el for el in valid_moves if el[3] != previous_location]

		print 'The set of valid moves from current position are:'
		print valid_moves

		# determine state of duration and closest / furthest valid moves from origin
		if mileage < dfactor_low * target_mileage:
			duration = 'low'
		elif mileage > dfactor_high * target_mileage:
			duration = 'high'
		else:
			duration = 'medium'
		print 'Duration = ' + str(duration)

		points = [i[3] for i in valid_moves]
		holdme = {}

		for k,v in fromstart.iteritems():
			for el in points:
				if k==el:
					holdme[k]=v

		closest_point = min(holdme, key=holdme.get)
		furthest_point = max(holdme, key=holdme.get)

		# create state if doesn't exist
		for move in valid_moves:
			state = move + ' ' + str(duration)
			if state not in qtemp.keys():
				qtemp[state] = 0.0

		# select next move
		rvalue = random.random()

		if rvalue < epsilon:
			print 'Exploiting...'
			action = dict((k,v) for k,v in qtemp.iteritems() if k[:5] in valid_moves)
			action = [k for k,v in action.iteritems() if v == max(action.values())][0][:5]
			print 'ACTION!!!!!!! is: '
			print action
		else:
			action = random.choice(valid_moves)
			print 'Epsilon > rvalue.. exploring. Taking random action'
			print 'The action is: '
			print action

		# set state
		state = action + ' ' + str(duration)

		# identify next moves
		next_moves = [ k for k,v in distance.items() if action[3]+',' in k ]
		next_moves = [el for el in next_moves if el[3] != previous_location]
		print 'The next moves from action movement are'
		print next_moves

		# create 'next' states if they do not exist in q-table
		for move in next_moves:
			fstate = move + ' ' + str(duration)
			if fstate not in qtemp.keys():
				qtemp[fstate] = 0.0

		# get max q-value in next moves
		# maxQ_next = [v for k,v in qtemp.iteritems() if v == max(qtemp.values()) and k[:5] in next_moves]
		maxQ_next = dict((k,v) for k,v in qtemp.iteritems() if k[:5] in next_moves)
		maxQ_next = [v for k,v in maxQ_next.iteritems() if v == max(maxQ_next.values())][0]
		print 'Initial max q value is: '
		print maxQ_next

		# adjust reward structure based on state of distance from start location
		if duration == 'low':
			if action[3] == furthest_point:
				temp_reward = rewards[action] + 200
			else:
				temp_reward = rewards[action]
		elif duration == 'high':
			if action[3] == closest_point:
				temp_reward = rewards[action] + 200
			else:
				temp_reward = rewards[action]
		else:
			temp_reward = rewards[action]

		# update q-table
		qtemp[state] = qtemp[state] + alpha * (temp_reward + gamma * maxQ_next - qtemp[state])

		# increment mileage
		mileage += distance[action]
		print 'Total miles after movement are: ' + str(mileage)

		previous_location = action[1]
		current_location = action[3]

		print 'Previous state now: ' + str(previous_location)
		print 'Current location now: ' + str(current_location)

	if mileage >= target_mileage - 0.26 and mileage <= target_mileage + 0.26:
		print "WITHIN TRGET RANGE!!!, WITHIN TRGET RANGE!!!, WITHIN TRGET RANGE!!!, WITHIN TRGET RANGE!!!, "
		Q = qtemp.copy()
		count += 1

	Q = qtemp.copy()

print 'Count = '
print count
print 'Resulting Q-table: '
print Q

def tester(policy_dict):
	
	start_loc = 'I'
	mileage = 0
	target_mileage = 2
	duration = 'low'
	path = ['I']
	current_loc = 'I'
	counter = 0

	while path.count('I') < 2 and counter < 50: 
		
		moves = dict((k,v) for k,v in policy_dict.iteritems() if k.startswith('('+current_loc) and str(duration) in k)
		next_move = [k[3] for k,v in moves.iteritems() if v == max(moves.values())][0]

		path.append(next_move)
		mileage += 0.25
		if mileage < dfactor_low * target_mileage:
			duration = 'low'
		elif mileage > dfactor_high * target_mileage:
			duration = 'high'
		else:
			duration = 'medium'
		current_loc = next_move
		counter += 1
		print path

	return path

tester(Q)