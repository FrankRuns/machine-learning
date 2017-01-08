

r = np.array([[-10, -0.5,   0,  -1,  -1,  -1,  -1,  -1,  -1], # represents rewards for transitions from room 0
			  [  0,  -10,  -1, 0.2, 0.2,  -1,  -1,  -1,  -1], # represents rewards for transitions from romm 0
			  [  0,   -1, -10,  -1,  -1, 0.2, 0.2,  -1,  -1], # reward for transition from room 2 to 3 is 0
			  [ -1,  0.2,  -1, -10,  -1,  -1,  -1, 0.2,  -1],
			  [ -1,  0.2,  -1,  -1, -10, 0.4,  -1, 0.4,  -1],
			  [ -1,   -1, 0.2,  -1, 0.4, -10,  -1,  -1, 0.2],
			  [ -1,   -1, 0.2,  -1,  -1,  -1, -10,  -1, 0.2],
			  [ -1,   -1,  -1, 0.2, 0.4,  -1,  -1, -10,  -1],
			  [ -1,   -1,  -1,  -1,  -1, 0.2, 0.2,  -1, -10]]).astype("float32")


m = np.array([[  0,  0.5,   1,   0,   0,   0,   0,   0,   0], # represents rewards for transitions from room 0
			  [0.5,    0,   0, 0.5, 0.5,   0,   0,   0,   0], # represents rewards for transitions from romm 0
			  [  1,    0,   0,   0,   0, 0.5, 0.5,   0,   0], # reward for transition from room 2 to 3 is 0
			  [  0,  0.5,   0,   0,   0,   0,   0, 0.5,   0],
			  [  0,  0.5,   0,   0,   0,   1,   0, 0.5,   0],
			  [  0,    0, 0.5,   0,   1,   0,   0,   0, 0.5],
			  [  0,    0, 0.5,   0,   0,   0,   0,   0, 0.5],
			  [  0,    0,   0, 0.5, 0.5,   0,   0,   0,   0],
			  [  0,    0,   0,   0,   0, 0.5, 0.5,   0,   0]]).astype("float32")

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

gamma = 0.8
alpha = 1.0
eps = 0.2
random_state = np.random.RandomState(1999) # set random seed

start_state = [0, 0]
current_state = states[0] # choose a random state (for initialization)
goal = False


as you get closer to target mileage, longer trails headed away from origin should be rewarded
less than otherwise. 

		#        o     a    b    c    d    e    f    g    h    i
r = np.array([[ -1,    0, 0.5,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # o
			  [ -1,   -1,  -1,   1,   1,  -1,  -1,  -1,  -1,  -1], # a
			  [ -1,   -1,  -1,  -1,  -1,   1,   1,  -1,  -1,  -1], # b
			  [ -1,   -1,  -1,  -1,   1,  -1,  -1,   1,  -1,  -1], # c
			  [ -1,   -1,  -1,   1,  -1,   1,  -1,   1,  -1,  -1], # d
			  [ -1,   -1,  -1,  -1,   1,  -1,   1,  -1,   1,  -1], # e
			  [ -1,   -1,  -1,  -1,  -1,   1,  -1,  -1,   1,  -1], # f
			  [ -1,   -1,  -1,   1,  -1,  -1,  -1,  -1,  -1, 100], # g
			  [ -1,   -1,  -1,  -1,  -1,  -1,   1,  -1,  -1, 100]]).astype("float32")

m = np.array([[  0,  0.5,   1,   0,   0,   0,   0,   0,   0,   0], # o
			  [  0,    0,   0,0.25,0.35,   0,   0,   0,   0,   0], # a
			  [  0,    0,   0,   0,   0,0.35, 0.1,   0,   0,   0], # b
			  [  0,    0,   0,   0, 0.5,   0,   0,0.25,   0,   0], # c
			  [  0,    0,   0, 0.5,   0,0.75,   0,0.35,   0,   0], # d
			  [  0,    0,   0,   0,0.75,   0, 0.5,   0,0.35,   0], # e
			  [  0,    0,   0,   0,   0, 0.5,   0,   0, 0.1,   0], # f
			  [  0,    0,   0,0.25,   0,   0,   0,   0,   0, 0.5], # g
			  [  0,    0,   0,   0,   0,   0, 0.1,   0,   0,   1]]).astype("float32")

q = np.zeros_like(r)
