import random

Q = {}

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

fromstart = {'A':1.00,'B':0.75,'C':0.50,'D':0.25,
		     'E':0.50,'F':0.75,'G':0.50,'H':0.25,
		     'I':0.00,'J':0.25,'K':1.00,'L':0.75,
		     'M':0.50,'N':0.25,'O':0.50,'P':1.25,
		     'Q':1.00,'R':0.75,'S':0.50,'T':0.75,
		     'U':1.50,'V':1.25,'W':1.00,'X':0.75,
		     'Y':1.00}

# define parameters
gamma = 0.7
alpha = 0.9
epsilon = 0.6

# set number of trials
n_trials = 1000

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

	# make initial random move
	initial_move = random.choice([ k for k,v in distance.items() if '('+start_location in k ])
	previous_location = initial_move[1]
	current_location = initial_move[3]

	# create state if doesn't exist
	state = initial_move + ' ' + str(False)
	if state not in Q.keys():
		Q[state] = 0.0

	# identify next moves from initial move
	next_moves = [k for k,v in distance.items() if current_location+',' in k]
	next_moves = [el for el in next_moves if el[3] != previous_location]
	print 'The next moves from action movement are'
	print next_moves

	# create state if doesnt exist
	for move in next_moves:
		fstate = move + ' ' + str(False)
		if fstate not in Q.keys():
			Q[fstate] = 0.0

	# get max q-value in next moves
	maxQ_next = [v for k,v in Q.iteritems() if v == max(Q.values()) and k[:5] in next_moves]
	print 'Initial max q value is: '
	print maxQ_next
	if len(maxQ_next) == 0:
		print 'no max qs found'
		maxQ_next = 0
		print 'Revised max q value is: '
		print maxQ_next
	elif len(maxQ_next) > 1:
		print 'more than 1 max q found'
		maxQ_next = random.choice(maxQ_next)
		print 'Revised max q value is: '
		print maxQ_next
	else:
		maxQ_next = maxQ_next[0]
		print 'One max q value found: '
		print maxQ_next	

	# update q-table on initial move
	Q[state] = Q[state] + alpha * (rewards[initial_move] + gamma * maxQ_next - Q[state])

	# increment mileage
	mileage += distance[initial_move]
	print 'Total miles after initial movement are: ' + str(mileage)

	print 'Initial move from ' + str(start_location) + ' to ' + str(current_location)

	while start_location != current_location:

		# identify valid moves
		valid_moves = [ k for k,v in distance.items() if '('+current_location in k ]
		valid_moves = [el for el in valid_moves if el[3] != previous_location]

		print 'The set of valid moves from current position are:'
		print valid_moves

		# determine state of duration and closest / furthest valid moves from origin
		duration = mileage > 0.49 * target_mileage
		print 'Mileage is in high zone: ' + str(mileage > 0.49 * target_mileage)
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
			if state not in Q.keys():
				Q[state] = 0.0

		# select next move
		rvalue = random.random()

		print 'The rvalue is ' + str(rvalue)

		if rvalue < epsilon:
			print 'Exploiting...'
			action = [k for k,v in Q.iteritems() if v == max(Q.values()) and k[:5] in valid_moves]
			print 'ACTION!!!!!!! is: '
			print action
			if len(action) == 0:
				action = random.choice(valid_moves)
				print 'Found no q values'
				print 'Action to be taken is: '
				print action
			elif len(action) > 1:
				action = random.choice(action)
				action = action[:5]
				print 'Found multple max q values'
				print 'Action to be taken is: '
				print action[:5]
			else:
				action = action[0][:5]

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

		# create state if doesnt exist
		for move in next_moves:
			fstate = move + ' ' + str(duration)
			if fstate not in Q.keys():
				Q[fstate] = 0.0

		# get max q-value in next moves
		maxQ_next = [v for k,v in Q.iteritems() if v == max(Q.values()) and k[:5] in next_moves]
		print 'Initial max q value is: '
		print maxQ_next
		if len(maxQ_next) == 0:
			print 'no max qs found'
			maxQ_next = 0
			print 'Revised max q value is: '
			print maxQ_next
		elif len(maxQ_next) > 1:
			print 'more than 1 max q found'
			maxQ_next = random.choice(maxQ_next)
			print 'Revised max q value is: '
			print maxQ_next
		else:
			maxQ_next = maxQ_next[0]
			print 'One max q value found: '
			print maxQ_next

		# adjust reward structure based on state of distance from start location
		if duration is True:
			if action[3] == closest_point:
				temp_reward = rewards[action] + 4
			elif action[3] == furthest_point:
				temp_reward = rewards[action] - 4
			else:
				temp_reward = rewards[action] 
		else:
			if action[3] == closest_point:
				temp_reward = rewards[action] - 4
			elif action[3] == furthest_point:
				temp_reward = rewards[action] + 4
			else:
				temp_reward = rewards[action] 

		# update q-table
		Q[state] = Q[state] + alpha * (temp_reward + gamma * maxQ_next - Q[state])

		# increment mileage
		mileage += distance[action]
		print 'Total miles after movement are: ' + str(mileage)

		previous_location = action[1]
		current_location = action[3]

		print 'Previous state now: ' + str(previous_location)
		print 'Current location now: ' + str(current_location)

print 'Resulting Q-table: '
print Q
'''
# next step
# state doesn't incorporate previous state
# when action is to go to previous state you should receive a negative reward
# in doing this, it would mean optimal policy never retraces it's steps... I think

test = {'(B,C) False': 0.0, '(S,N) False': 0.0, '(I,D) False': 0.0, '(N,M) True': -0.36396396363995986, '(Q,P) False': 0.0, '(X,S) False': 0.0, '(B,G) True': 3.9999603600036, '(L,M) False': 0.0, '(I,N) False': 0.0, '(R,Q) False': 0.0, '(O,J) False': 0.9999, '(J,O) False': 5.360360000000001, '(C,D) True': 0.036000000360003614, '(C,B) True': -3.999999999999996, '(M,H) True': 3.999999999999996, '(D,C) False': -3.207999279207276, '(Y,X) False': 0.0, '(G,L) False': 0.0, '(C,D) False': -3.996, '(X,S) True': 4.007371097400249, '(S,N) True': 4.0, '(L,K) False': 0.0, '(K,P) False': 0.0, '(L,Q) False': 3.96, '(C,B) False': 3.9999999996, '(L,G) False': 0.9, '(V,R) False': 0.0, '(Q,L) True': 3.6003603996360365, '(W,X) False': 0.0, '(O,N) True': 0.03636000003600032, '(S,X) True': 3.465535092345954, '(G,B) True': -3.999279927928, '(W,X) True': 4.000000000006988, '(I,D) True': 0.0, '(M,R) False': 3.9996, '(G,F) False': 0.0, '(O,T) True': -4.0, '(J,O) True': 0.999999999, '(M,L) False': 0.0, '(A,F) False': 0.0, '(I,J) True': 0.0, '(G,B) False': -3.996, '(X,W) True': -3.639996003996, '(W,V) True': 4.0, '(O,J) True': 9.0, '(R,V) True': -4.0, '(H,I) True': 3.999999999999996, '(M,N) False': 0.0, '(Q,L) False': 0.0, '(O,N) False': -3.9999995999999998, '(Q,R) True': 4.0, '(M,H) False': -3.96, '(V,U) False': 0.0, '(R,S) False': 0.99, '(K,F) False': 0.0, '(G,H) True': 4.0, '(B,A) True': -4.0, '(Y,T) True': 11.368860937099129, '(F,A) True': -3.2727272799992737, '(F,G) True': 4.0, '(L,G) True': 8.996000000000004, '(T,Y) True': -3.9927358744971064, '(X,Y) False': 5.017057587720082, '(R,S) True': 16.79240276086624, '(I,N) True': 0.0, '(F,G) False': 0.0, '(O,T) False': 4.0001156974474075, '(K,L) True': 4.0, '(V,Q) False': 0.0, '(X,Y) True': 4.773575723908475, '(V,U) True': -4.0, '(N,I) True': 4.0, '(H,G) False': 0.0, '(J,I) False': -3.99999996, '(Q,V) True': -0.003600360036360002, '(Q,P) True': -4.0, '(H,M) True': -0.003960000039639637, '(I,H) False': 0.0, '(K,P) True': -4.0, '(Q,V) False': 0.0, '(H,C) True': -3.99999999999996, '(P,U) True': 1.0, '(E,J) False': -3.999999999996, '(N,S) False': 4.512402767423625, '(N,I) False': -3.996, '(A,B) False': 0.0, '(D,I) True': 4.0, '(T,S) False': 0.999999, '(V,W) True': 6.991053515178095e-11, '(S,R) True': 1.396399649717388, '(U,P) True': 9.0, '(Y,X) True': 4.747462612259178, '(X,W) False': 0.0, '(P,Q) True': 4.0, '(A,B) True': 4.0, '(F,K) True': -0.3963636003996034, '(E,D) True': 4.000000005833589, '(S,T) True': 12.368893270195597, '(W,V) False': 0.0, '(T,O) True': 3.636396036003636, '(H,G) True': 0.0, '(I,H) True': 0.0, '(Y,T) False': 0.0, '(R,M) False': 0.0, '(E,D) False': -3.99999999999996, '(J,I) True': 3.99999999999996, '(S,X) False': -3.96, '(R,V) False': 3.996, '(N,O) False': 1.0853570699999966e-08, '(D,C) True': -3.99996, '(N,M) False': 0.0, '(D,I) False': -3.99999996, '(A,F) True': 4.0, '(S,T) False': 4.9995, '(F,A) False': -3.96, '(H,C) False': -3.9999999996, '(N,S) True': -3.999999999999994, '(P,K) True': 3.6000000036399635, '(J,E) True': -3.999999937214935, '(H,I) False': -3.9996, '(B,A) False': 3.9999995999999998, '(H,M) False': 0.00035999999999999964, '(V,R) True': 4.0, '(E,J) True': 4.000000000000923, '(Q,R) False': 0.0, '(K,F) True': 0.3603600036039598, '(V,Q) True': 0.39603632007920764, '(C,H) False': -3.999996, '(L,Q) True': -4.0, '(M,R) True': -3.9990279007813783, '(M,N) True': 0.0036003600003636296, '(T,Y) False': 4.7695592467835475, '(G,H) False': 0.0, '(V,W) False': 0.0, '(C,H) True': 3.99999999999996, '(L,M) True': 4.0, '(T,O) False': -3.6, '(U,V) True': 4.0, '(B,C) True': 4.0, '(T,S) True': 9.00093646741917, '(D,E) True': -3.999999999916258, '(G,F) True': 0.0, '(G,L) True': 4.639963639963959, '(L,K) True': -3.636363963960396, '(D,E) False': 0.03600071211277561, '(R,Q) True': -3.636396003960364, '(B,G) False': -3.999996, '(J,E) False': -3.999999993114128, '(F,K) False': 0.0, '(K,L) False': 0.0, '(S,R) False': 4.99995, '(M,L) True': -0.0003996363600363602, '(R,M) True': 3.6363960036000003, '(I,J) False': 9.015079113539532e-20, '(N,O) True': 1.085357069999992e-17}
I - J... 0.25
J - O... 0.50
O - T... 0.75
T - Y... 1.00
Y - X... 1.25
X - S... 1.50
S - T... 1.75
T - O... 2.00
O - J... 2.25
J - I... 2.50
'''

test2 = {'(B,C) False': -3.9999999999999996, '(U,P) True': 9.0, '(N,M) True': -3.9603996039999996, '(R,S) True': 9.0, '(X,S) False': 0.0, '(S,N) False': 0.0, '(L,M) False': -3.9999999996, '(D,C) True': -4.0, '(L,G) True': 5.367543825451849, '(O,J) False': 1.0000000000000007, '(Y,T) True': 4.0, '(C,D) True': 0.39960396036395984, '(C,B) True': -4.0, '(K,L) False': 0.0, '(M,H) True': 4.0, '(D,C) False': -3.9279200792720728, '(Y,X) False': 0.0, '(G,L) False': 5.691016583528285, '(C,D) False': -4.0, '(X,S) True': 4.0, '(S,N) True': 4.0, '(L,K) False': 0.0, '(K,P) False': 0.0, '(L,Q) False': 10.968517198861669, '(C,B) False': 4.0, '(L,G) False': 1.0007546938496452, '(V,R) False': 0.0, '(Q,L) True': 11.277885364693502, '(W,X) False': 0.0, '(O,N) True': 3.96000360039996, '(S,X) True': -3.999992799999928, '(G,B) True': -4.0, '(W,X) True': 4.0, '(I,D) True': 0.0, '(M,R) False': 4.00000005670567, '(G,F) False': 0.0, '(O,T) True': -4.0, '(J,O) True': 1.0000000000000075, '(M,L) False': 0.0, '(A,F) False': 0.0, '(I,J) True': 0.0, '(S,T) True': 5.0, '(X,W) True': -3.96036036360396, '(Y,X) True': 4.0, '(O,J) True': 9.000000000000002, '(R,V) True': -4.0, '(H,I) True': 4.0, '(M,N) False': -3.999999999299363, '(Q,P) False': 0.0, '(B,G) True': 3.6438678246724305, '(O,N) False': -4.0, '(Q,R) True': 4.0, '(M,H) False': -4.0, '(V,U) False': 0.0, '(R,S) False': 1.0, '(K,F) False': 0.0, '(G,H) True': 4.0, '(B,A) True': -4.0, '(J,O) False': 5.360000000000168, '(F,A) True': -3.9200792072792003, '(F,G) True': 4.000000000000001, '(R,Q) False': 0.0, '(T,Y) True': -4.0, '(X,Y) False': -3.9999999999917373, '(I,N) True': 0.0, '(F,G) False': 0.0, '(O,T) False': 4.0, '(V,Q) False': 0.0, '(X,Y) True': 3.920007999200008, '(V,U) True': -4.0, '(N,I) True': 4.0, '(H,G) False': 0.0, '(J,I) False': -4.0, '(Q,V) True': -3.999996360396, '(Q,P) True': -3.999999999201762, '(H,M) True': -0.3600360003995937, '(B,C) True': 4.0, '(K,P) True': -4.0, '(S,T) False': 5.0, '(H,C) True': -4.0, '(P,U) True': 1.0, '(G,B) False': -4.0, '(E,J) False': -3.9999999941623976, '(N,S) False': -3.279999992079999, '(N,I) False': -4.0, '(A,B) False': 0.0, '(F,K) False': 0.0, '(T,S) False': 1.0, '(V,W) True': 7.062026592236372e-48, '(W,V) True': 4.0, '(X,W) False': 0.0, '(P,Q) True': 4.0, '(A,B) True': 4.0, '(F,K) True': 6.919278287471245, '(E,D) True': 4.0, '(W,V) False': 0.0, '(T,O) True': 0.3963996360363997, '(H,G) True': 0.750386078746784, '(I,H) True': 0.0, '(Y,T) False': 0.0, '(K,L) True': 4.6989261738701895, '(N,O) True': 1.3278047757047202e-22, '(J,I) True': 4.0, '(S,X) False': -4.0, '(R,V) False': 4.000000000919569, '(S,R) True': 1.3999963963999638, '(I,N) False': 1.0379066734186704e-34, '(N,M) False': 7.757372014409638e-31, '(D,I) False': -4.0, '(A,F) True': 4.0, '(I,D) False': 6.644489384305004e-24, '(F,A) False': -3.9273541598174084, '(H,C) False': -3.999999999999928, '(N,S) True': -4.0, '(P,K) True': 10.922842320995114, '(J,E) True': -3.9999999999379607, '(H,I) False': -4.0, '(B,A) False': 4.0, '(Q,L) False': 0.0, '(H,M) False': 3.603600360039951e-08, '(V,R) True': 4.0, '(E,J) True': 4.0, '(Q,R) False': 0.0, '(K,F) True': 3.9603600008244793, '(V,Q) True': -0.039636399995640004, '(C,H) False': -4.0, '(L,Q) True': 3.105067779756906, '(M,R) True': -4.0, '(M,N) True': 3.96000000363599e-06, '(T,Y) False': 4.000000000000682, '(G,H) False': 0.0, '(V,W) False': 0.0, '(N,O) False': 1.4977008274439823e-15, '(C,H) True': 4.0, '(L,M) True': 4.0, '(T,O) False': -3.9998909530718216, '(U,V) True': 4.0, '(I,H) False': 6.492118633856549e-79, '(T,S) True': 9.0, '(D,E) True': -4.0, '(G,F) True': 7.845157686584239e-12, '(G,L) True': 1.406910890019724, '(L,K) True': 6.52327789294011, '(D,E) False': 0.36000396039601057, '(R,Q) True': -0.3603636000360364, '(B,G) False': -4.0, '(J,E) False': -3.927992728, '(D,I) True': 4.0, '(R,M) False': -3.99996, '(Q,V) False': 0.0, '(S,R) False': 5.0, '(M,L) True': -3.9996349572814225, '(R,M) True': 0.0036039960036359925, '(I,J) False': 1.3731558107045719e-30, '(E,D) False': -4.0}
I - D... 0.25
D - E... 0.50
E - J... 0.75
J - O... 1.00
O - N... 1.25
N - I... 1.50