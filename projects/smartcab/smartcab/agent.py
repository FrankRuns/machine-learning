import random
import math
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """ An agent that learns to drive in the Smartcab world.
        This is the object you will be modifying. """ 

    def __init__(self, env, learning=True, epsilon=0.97, alpha=0.97):
        super(LearningAgent, self).__init__(env)     # Set the agent in the evironment 
        self.planner = RoutePlanner(self.env, self)  # Create a route planner
        self.valid_actions = self.env.valid_actions  # The set of valid actions

        # Set parameters of the learning agent
        self.learning = learning # Whether the agent is expected to learn
        self.Q = dict()          # Create a Q-table which will be a dictionary of tuples
        self.epsilon = epsilon   # Random exploration factor
        self.alpha = alpha       # Learning factor

        ###########
        ## TO DO ##
        ###########
        # Set any additional class parameters as needed

        self.n_trials=1

    def reset(self, destination=None, testing=False):
        """ The reset function is called at the beginning of each trial.
            'testing' is set to True if testing trials are being used
            once training trials have completed. """

        # Select the destination as the new location to route to
        self.planner.route_to(destination)
        
        ########### 
        ## TO DO ##
        ###########
        # Update epsilon using a decay function of your choice
        # Update additional class parameters as needed
        # If 'testing' is True, set epsilon and alpha to 0

        if testing==True:
            self.epsilon = 0.0
            self.alpha = 0.0
        else:
            self.epsilon = math.pow(0.97, 0.1*self.n_trials)
            #self.alpha = math.pow(0.97, 0.02*self.n_trials) # if not D and A, go back to 0.05

            #self.epsilon = math.cos(0.9*self.n_trials/500)
            #self.alpha = math.cos(0.9*self.n_trials/1500)

            # self.epsilon = 1/(math.pow(self.n_trials,1/1.6))
            # self.alpha = self.alpha * 0.95
            
            # self.epsilon = 1/math.pow(self.n_trials,2)
            # self.epsilon = math.exp(-self.alpha*self.n_trials)
            # self.epsilon = math.cos(self.alpha*self.n_trials)
            # self.epsilon = self.epsilon * math.cos(self.n_trials)
        self.n_trials += 1

        return None

    def build_state(self):
        """ The build_state function is called when the agent requests data from the 
            environment. The next waypoint, the intersection inputs, and the deadline 
            are all features available to the agent. """

        # Collect data about the environment
        waypoint = self.planner.next_waypoint() # The next waypoint 
        inputs = self.env.sense(self)           # Visual input - intersection light and traffic
        deadline = self.env.get_deadline(self)  # Remaining deadline

        ########### 
        ## TO DO ##
        ###########
        # Set 'state' as a tuple of relevant data for the agent        
        state = (waypoint, inputs['light'], inputs['left'], inputs['right'], inputs['oncoming'])
        state = [str(el) for el in state]

        return state


    def get_maxQ(self, state):
        """ The get_max_Q function is called when the agent is asked to find the
            maximum Q-value of all actions based on the 'state' the smartcab is in. """

        ########### 
        ## TO DO ##
        ###########
        # Calculate the maximum Q-value of all actions for a given state

        # make state usable
        kurrent_state = ''.join(state)
 
        # bizarre code behavior.. sometimes createQ doesn't run
        # in the event, I create the key in Q
        # holder = {'left' : 0.0, 'right' : 0.0, 'forward' : 0.0, None : 0.0}
        holder = {'left' : 0.0, 'right' : 0.0, 'forward' : 0.0, None : 0.0}
        # someone mentioned initializing Qval to 20...

        # find largest q-val for this state
        # actually need the key for the largest value - used in choose_action
        # help from http://stackoverflow.com/questions/268272/getting-key-with-maximum-value-in-dictionary
        if kurrent_state not in self.Q.keys():
            self.Q[kurrent_state] = holder
            # maxQ = max(self.Q[kurrent_state], key=self.Q[kurrent_state].get)
            maxQ = [key for key,val in self.Q[kurrent_state].iteritems() if val == max(self.Q[kurrent_state].values())]
            if len(maxQ)>1:
            	maxQ = [random.choice(maxQ)]
        else:
            # maxQ = max(self.Q[kurrent_state], key=self.Q[kurrent_state].get)
            maxQ = [key for key,val in self.Q[kurrent_state].iteritems() if val == max(self.Q[kurrent_state].values())]
            if len(maxQ)>1:
            	maxQ = [random.choice(maxQ)]

        return maxQ[0]


    def createQ(self, state):
        """ The createQ function is called when a state is generated by the agent. """

        ########### 
        ## TO DO ##
        ###########
        # When learning, check if the 'state' is not in the Q-table
        # If it is not, create a new dictionary for that state
        #   Then, for each action available, set the initial Q-value to 0.0

        kurrent_state = ''.join(state)
        best_action = self.choose_action(state)

        # holder = {'left' : 0.0, 'right' : 0.0, 'forward' : 0.0, None : 0.0}
        holder = {'left' : 0.0, 'right' : 0.0, 'forward' : 0.0, None : 0.0}
        # someone mentioned initializing Qval to 20...

        if kurrent_state not in self.Q.keys():
            self.Q[kurrent_state] = holder

        return self.Q


    def choose_action(self, state):
        """ The choose_action function is called when the agent is asked to choose
            which action to take, based on the 'state' the smartcab is in. """

        # Set the agent state and default action
        self.state = state
        self.next_waypoint = self.planner.next_waypoint()

        ########### 
        ## TO DO ##
        ###########
        # When not learning, choose a random action
        # When learning, choose a random action with 'epsilon' probability
        #   Otherwise, choose an action with the highest Q-value for the current state
 
        # action = random.choice(self.env.valid_actions)

        rvalue = random.random()
        if rvalue < self.epsilon:
            #action = random.choice(self.env.valid_actions)
            action = self.next_waypoint
        else:
            action = self.get_maxQ(state)

        return action


    def learn(self, state, action, reward):
        """ The learn function is called after the agent completes an action and
            receives an award. This function does not consider future rewards 
            when conducting learning. """

        ########### 
        ## TO DO ##
        ###########
        # When learning, implement the value iteration update rule
        #   Use only the learning rate 'alpha' (do not use the discount factor 'gamma')

        kurrent_state = ''.join(state)
        best_action = self.choose_action(state)   

        # self.Q[kurrent_state][best_action] = self.alpha * (reward - self.Q[kurrent_state][best_action])
        # self.Q[kurrent_state][best_action] = self.Q[kurrent_state][best_action] + (self.alpha * reward)
        self.Q[kurrent_state][best_action] = self.Q[kurrent_state][best_action] + self.alpha * (reward - self.Q[kurrent_state][best_action])

        return


    def update(self):
        """ The update function is called when a time step is completed in the 
            environment for a given trial. This function will build the agent
            state, choose an action, receive a reward, and learn if enabled. """

        state = self.build_state()          # Get current state
        self.createQ(state)                 # Create 'state' in Q-table
        action = self.choose_action(state)  # Choose an action
        reward = self.env.act(self, action) # Receive a reward
        self.learn(state, action, reward)   # Q-learn

        return
        

def run():
    """ Driving function for running the simulation. 
        Press ESC to close the simulation, or [SPACE] to pause the simulation. """

    ##############
    # Create the environment
    # Flags:
    #   verbose     - set to True to display additional output from the simulation
    #   num_dummies - discrete number of dummy agents in the environment, default is 100
    #   grid_size   - discrete number of intersections (columns, rows), default is (8, 6)
    env = Environment()
    
    ##############
    # Create the driving agent
    # Flags:
    #   learning   - set to True to force the driving agent to use Q-learning
    #    * epsilon - continuous value for the exploration factor, default is 1
    #    * alpha   - continuous value for the learning rate, default is 0.5
    agent = env.create_agent(LearningAgent)
    
    ##############
    # Follow the driving agent
    # Flags:
    #   enforce_deadline - set to True to enforce a deadline metric
    env.set_primary_agent(agent, enforce_deadline=True) 
        # 'enforce_deadline' - Set this to True to force the driving agent to capture whether it reaches the destination in time.

    ##############
    # Create the simulation
    # Flags:
    #   update_delay - continuous time (in seconds) between actions, default is 2.0 seconds
    #   display      - set to False to disable the GUI if PyGame is enabled
    #   log_metrics  - set to True to log trial and simulation results to /logs
    #   optimized    - set to True to change the default log file name
    sim = Simulator(env, update_delay=0.01, display=False, log_metrics=True, optimized=True)
        # 'update_delay' - Set this to a small value (such as 0.01) to reduce the time between steps in each trial.
        # 'log_metrics' - Set this to True to log the simluation results as a .csv file in /logs/. 

    ##############
    # Run the simulator
    # Flags:
    #   tolerance  - epsilon tolerance before beginning testing, default is 0.05 
    #   n_test     - discrete number of testing trials to perform, default is 0
    sim.run(n_test=20, tolerance=0.0001) # 'n_test' - Set this to '10' to perform 10 testing trials


if __name__ == '__main__':
    run()
