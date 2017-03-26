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
		    '(P,Q)':0.0,'(Q,R)':0.0,'(R,S)':200.0,'(S,T)':200,
		    '(U,V)':0.0,'(V,W)':0.0,'(W,X)':0.0,'(X,Y)':0.0,
			'(B,A)':0.0,'(C,B)':0.0,'(D,C)':0.0,'(E,D)':0.0,
		    '(G,F)':0.0,'(H,G)':0.0,'(I,H)':0.0,'(J,I)':0.0,
		    '(L,K)':0.0,'(M,L)':0.0,'(N,M)':0.0,'(O,N)':0.0,
		    '(Q,P)':0.0,'(R,Q)':0.0,'(S,R)':200.0,'(T,S)':200,
		    '(V,U)':0.0,'(W,V)':0.0,'(X,W)':0.0,'(Y,X)':0.0,
		    '(A,F)':0.0,'(F,K)':0.0,'(K,P)':0.0,'(P,U)':200,
		    '(B,G)':0.0,'(G,L)':200,'(L,Q)':0.0,'(Q,V)':0.0,
		    '(C,H)':0.0,'(H,M)':0.0,'(M,R)':0.0,'(R,V)':0.0,
		    '(D,I)':0.0,'(I,N)':0.0,'(N,S)':0.0,'(S,X)':0.0,
		    '(E,J)':0.0,'(J,O)':200,'(O,T)':0.0,'(T,Y)':0.0,
		    '(F,A)':0.0,'(K,F)':0.0,'(P,K)':0.0,'(U,P)':200,
		    '(G,B)':0.0,'(L,G)':200,'(Q,L)':0.0,'(V,Q)':0.0,
		    '(H,C)':0.0,'(M,H)':0.0,'(R,M)':0.0,'(V,R)':0.0,
		    '(I,D)':0.0,'(N,I)':0.0,'(S,N)':0.0,'(X,S)':0.0,
		    '(J,E)':0.0,'(O,J)':200,'(T,O)':0.0,'(Y,T)':0.0}

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
n_trials = 100000

for i in range(n_trials):

	# define start location
	start_location = 'I'
	previous_location = None
	current_location = start_location

	# define strt mileage and target mileage
	mileage = 0
	target_mileage = 2

	print 'Start location is ' + str(start_location)
	print 'Start mileage is ' + str(mileage)
	print 'Target mileage is ' + str(target_mileage)

	# make initial random move
	initial_move = random.choice([ k for k,v in distance.items() if '('+current_location in k ])
	current_location = initial_move[3]

	print 'Initial move from ' + str(start_location) + ' to ' + str(current_location)

	while start_location != current_location:

		# identify valid moves
		valid_moves = [ k for k,v in distance.items() if '('+current_location in k ]
		valid_moves = [el for el in valid_moves if el[3] != previous_location]

		print 'The set of valid moves from current position are:'
		print valid_moves

		# create state if doesn't exist
		for state in valid_moves:
			if state not in Q.keys():
				Q[state] = 0.0

		# select next move
		rvalue = random.random()

		print 'The rvalue is ' + str(rvalue)

		if mileage > 0.49 * target_mileage:
			print 'Mileage is in high zone: ' + str(mileage > 0.49 * target_mileage)
			points = [i[3] for i in valid_moves]
			holdme = {}

			for k,v in fromstart.iteritems():
				for el in points:
					if k==el:
						holdme[k]=v

			action = '('+current_location+','+min(holdme, key=holdme.get)+')'
			print action

		else:

			if rvalue < epsilon:
				print 'Exploiting...'
				action = [k for k,v in Q.iteritems() if v == max(Q.values()) and k in valid_moves]
				if len(action) == 0:
					action = random.choice(valid_moves)
					print 'Found no q values'
					print 'Action to be taken is: '
					print action
				elif len(action) > 1:
					action = random.choice(action)
					print 'Found multple max q values'
					print 'Action to be taken is: '
					print action
				else:
					action = action[0]

			else:
				action = random.choice(valid_moves)
				print 'Epsilon > rvalue.. exploring. Taking random action'
				print 'The action is: '
				print action


		# identify next moves
		next_moves = [ k for k,v in distance.items() if action[3]+',' in k ]
		print 'The next moves from action movement are'
		print next_moves

		# create state if doesnt exist
		for state in next_moves:
			if state not in Q.keys():
				Q[state] = 0.0

		# get max q-value in next moves
		maxQ_next = [v for k,v in Q.iteritems() if v == max(Q.values()) and k in next_moves]
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

		# update q-table
		Q[action] = Q[action] + alpha * (rewards[action] + gamma * maxQ_next - Q[action])

		# increment mileage
		mileage += distance[action]
		print 'Total miles after movement are: ' + str(mileage)

		previous_location = action[1]
		current_location = action[3]

		print 'Previous state now: ' + str(previous_location)
		print 'Current location now: ' + str(current_location)

print 'Resulting Q-table: '
print Q

#test = {'(O,T)': 0.00313640069610549, '(U,P)': 200.0, '(L,G)': 200.0, '(V,Q)': 1.2981476270970358e-10, '(N,S)': 297.8190233508492, '(H,C)': 0.0, '(Q,P)': 1.3684254950392006e-115, '(P,U)': 0.0, '(Q,V)': 1.3282333754079405e-18, '(M,R)': 0.02067947032571482, '(T,Y)': 0.01414766296826167, '(V,W)': 1.4266898904483478e-92, '(G,L)': 200.0, '(M,L)': 3.5598507010100266e-304, '(S,T)': 200.0, '(J,I)': 0.0, '(R,Q)': 2.0676376944575918e-07, '(X,S)': 2.0683453071109354e-22, '(H,I)': 0.0, '(S,N)': 2.1743652498398335e-74, '(G,H)': 0.0, '(M,H)': 0.0, '(B,C)': 0.0, '(Y,X)': 1.5688240338706893e-06, '(Q,L)': 2.5541511294441646e-39, '(I,N)': 0.0, '(F,K)': 1.4362586723102698e-100, '(H,M)': 1.293937805209649e-60, '(K,P)': 1.3026117475074714e-07, '(J,E)': 1.5916201353553828e-260, '(B,G)': 0.0, '(I,D)': 0.0, '(C,H)': 0.0, '(G,F)': 2.0435339227284122e-266, '(W,V)': 1.3773235198058856e-07, '(H,G)': 0.0, '(I,J)': 0.0, '(R,S)': 221.16422031612944, '(B,A)': 0.0, '(O,J)': 450.48374362843526, '(E,J)': 306.7094515682158, '(W,X)': 1.6092802199598202e-78, '(G,B)': 1.590375210404927e-216, '(N,O)': 3.255052591617052e-126, '(V,R)': 2.1868072814832473, '(N,I)': 0.0, '(Y,T)': 14.690126904934147, '(V,U)': 1.400000000000008e-17, '(T,O)': 2.2885582101813725e-21, '(D,E)': 1.3103163393016799e-28, '(K,L)': 3.4626007044946214e-105, '(D,C)': 0.0, '(J,O)': 228.6840399314628, '(Q,R)': 2.053867155616228, '(C,B)': 0.0, '(C,D)': 0.0, '(N,M)': 1.3028066305200318e-06, '(P,K)': 2.1814384438316224e-79, '(X,Y)': 0.14147663192603743, '(R,M)': 2.016871474802673e-11, '(F,G)': 0.0, '(F,A)': 0.0, '(K,F)': 1.4863624115113834e-75, '(O,N)': 2.1641995957984266e-105, '(M,N)': 1.3457300532654003e-24, '(P,Q)': 2.083094498474631e-09, '(R,V)': 1.377323519807203e-25, '(T,S)': 200.02978191291567, '(D,I)': 0.0, '(S,X)': 1.4133549854690937e-08, '(E,D)': 0.0, '(S,R)': 227.2728575097604, '(X,W)': 1.2853062076111308e-90, '(I,H)': 0.0, '(L,Q)': 1.6467975040854503e-56, '(U,V)': 0.0, '(A,B)': 1.432770459824261e-215, '(L,M)': 1.2939784691817897e-100, '(L,K)': 1.5942471262641942e-238, '(A,F)': 1.509825142920776e-267}
