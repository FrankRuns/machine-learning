# Machine Learning Engineer Nanodegree
## Capstone Proposal
Frank Corrigan
March 18, 2017

## Proposal

### Domain Background
_(approx. 1-2 paragraphs)_

Approximately 17 million individuals in the US (according to 2015 data) identify themselves as runners -- folks that have participated in an organized running race. This cohort is continuously searching for recommendations on how to run faster, who to run with, and where to find more enjoyable runs. That final question is the topic of focus in this capstone project. A particularly common method of deciding where to run is to ask other runners. Recently, websites such as Strava or MapMyRun have made the answer to this question more shareable. Any runner can throw a GPS-enabled watch on their arm, go for a run, upload the data to their site of choice, and other runners and view what routes other runners are running most often. The most popular routes are regarded as the best routes to run. 

However, not every runner enjoys the same scenery or can take the time to commute to those best run locations. It would be advantagous if we could find the best or optimal run according to personal taste directly from where we are staying or living. Since time is finite and exploration of the options for running routes seems infinite, machine learning can assist in determining these optimal paths. The problem of considering which route to take is not unique to runners and running paths - optimal path finding problems exist and have been studied in depth in a variety of fields including naval ship ocean traversal, automobile navigation through road networks, logistics (recall the infamous traveling salesman problem), and even in a related activity, cycling. An optimal path, depending upon it's application, could mean the shortest path, the most fuel efficient path, or the fastest path. Each of these fields lends information for how to think about determing the best running route from an individuals current location. 

Leigh M. Chinitz had a similar idea many years ago. In 2004, he registered a US patent on a algorithm that created closed loops for cyclers. The website that leverages this alogorithm, RouteLoops.com, askes the user for a starting location and target mileage and creates a looped route the cycler can follow. Additionally, there are some high level preferences you can select such as road selection type. This research is helpful in understanding a good method for creating loops from the same start and end location. However, RouteLoops isn't helpful for runners that like to be on trails and want to see beautiful things as their endorphins run wild. 

On a personal note, I've been a competitve runner for many years through high school, college, and ever since. When I moved up to Melrose, MA -- 10 miles outside Boston -- a few months ago I was delighted and overwhelmed by the numerous options of trails I could explore. I do love exploration, but as I worked through Udacity's Smartcab Reinforcement Learning project I began to realize that running a new trail system and finding the best loops is very similar to the q-learning algorithm I was creating to teach a car to drive. I wondered if my computer could help me find the best trails in a much timelier fashion than just running every day. From years of expereince, I have good intuition for what consitutes a good trail or a good run. If I can map a reward system to attributed of the trail system, we can use simulation and reinforecment learning to determine the best routes even before lacing up our sneakers. 

http://www.runningusa.org/statistics
http://users.iems.northwestern.edu/~dolira/dolinskaya_dissertation.pdf
https://en.wikipedia.org/wiki/Travelling_salesman_problem
http://patft.uspto.gov/netacgi/nph-Parser?u=%2Fnetahtml%2Fsrchnum.htm&Sect1=PTO1&Sect2=HITOFF&p=1&r=1&l=50&f=G&d=PALL&s1=7162363.PN.&OS=PN/7162363&RS=PN/7162363

### Problem Statement
_(approx. 1 paragraph)_

The problem statement in it's simplest form is "tell me the best (or optimal) running route from my current location." A runner wants to run the best runs as soon as possible, but it takes time to learn where they are and what your surroundings have to offer. Where are the trails or bike paths that will allow me to enjoy nature or avoid intersections and getting hit by cars? Where are the enormous uphills that I'd like to avoid today? Are there historical structures are tourist attractions that I'd like to run past and see in this area? Is the neighborhood safe for me to run through? Are there restrooms or water fountains I can pass along the way? Each one of these questions, in total, is a piece of this problem.

A 10 mile run could have dozens of different split point descisions that need to be made. If a runner ran a trail system 1000 times, they'd be able to pin point the most rewarding runs given the characteristics of that area. However, 1000 runs could take several years! The goal is to speed up this learning process for each individual runner. Applying reinforecment learning this problem will allow the runner to know the optimal decision at each split point in order to maximize the utility of a running loop based on a desired target mileage number. We can measure that by A) plotting on a map what the algorithm suggests as the best path and B) inspecting each decision at different points with knowledge of what lies ahead in that best path. If this works for me -- in the MIddlesex Fells Reservation -- it should work anywhere we can obtain map data for.

### Datasets and Inputs
_(approx. 2-3 paragraphs)_

The dataset for this project will come from OpenStreetMaps.org. This open source geospacial data can be downloaded in .OSM format, which is very similar to XML. Further, there are many good resources on how to extract and manipulate these files. The map for this project will include parts of Malden, Melrose, and Winchester, MA. which is primarly the Middlesex Fells Reservation area. Technically, the bounds include <bounds minlat="42.4251000" minlon="-71.1318000" maxlat="42.4702000" maxlon="-71.0699000"/>. 

This data includes both nodes and ways. Nodes -- which include latitude and longitude coordinates -- identify points on a map and ways -- which include collections of nodes -- identify links between nodes. Nodes and ways are tagged with different types of identifiers. For example, a node may be tagged with v="traffic_signal" meaning there is a traffic light at those coordinates. Waypoints have significantly more tags. One very common tag is k="name" usually accompanied by a street name. The starting location for this project will be Stone Place in Melrose, MA - where I currently reside. Three other tags that will be leveraged to assign rewards to different ways are

1) "highway" equals "path" or "footpath" which will indicate that the way is a running path prefered over the road. 
2) "tourism" equals "alpine_hut", "wilderness_hut", or "viewpoint" which indicates either natural-setting shelter (usually in cool places) or a lookout where you can see something neat (in this case it will be a skyline view of Boston). This tag also includes "artwork" (it's always neat to run by a Banksy).
3) "historic" equals anything usually means something cool. Count it. 
3) "natural" equals anything. There are a variety of tags to tell us about the way here including "peak" (is it a mountain peak) and "water" or "spring" (does it go past a body of water).

Each of these tags will provide us with information about the reward system of a particular course. At a high level (more details in the solution section), the algorithm will parse this data, move from node to node along the ways, increment it's knowledge base (q-table) of the best ways based on the tags, and create a policy for each decision point along the route. Of course, this is in addition to determingn a proper target mileage loop for the runner.  

http://www.openstreetmap.org
http://www.openstreetmap.org/#map=13/42.4530/-71.1269
http://wiki.openstreetmap.org/wiki/Hiking

### Solution Statement
_(approx. 1 paragraph)_

The optimal route -- for this particular solution -- will maximize miles on either "trails" (which can include hiking trails, running paths, or bike paths) rather than roads, will include pictuesque water views, and will incorporate the highest number of historical landmarks possible. Balancing other variables will result in alternative solutions to this problem. For instance, if an individual is recovering from a hamstring injury they will want to avoid hills and as such minimize elevation gain to yield the optimal route. This implementation will focus on mileage on trails, aestetically pleasing or educational surroundings.

The algorithm under development will include 2 user inputs. A starting location (in this implementation that will be Stone Place in Melrose, MA.) and a target mileage for the run. Simulataneoulsy, we'll use a q-learning algorithm and a route loop planner to determine the best route for the target mileage. Temporarily, the logic for the solution will look something like this:

1. Find the starting node.
2. Identify next possible nodes to move to. Randomly move to next node. 
3. Define a temporary q-table. If total mileage outside acceptable range (+/- one-querter mile), we will discard the findings of 
3. If total mileage > 1/2 target mileage, move to the next node with the shortest distance from the end location,
else -- depending upon exploratory status -- either move to a random location or exploit current information in your q-table.
4. Increment mileage and update q-table (q-values must depend on current and future reward). Starting update function: Q(s,a) = R(s,a) + gamma * max(Q(nextstate,allactions))
5. Initial reward system. +2 if tag "highway" equals "footway" or "path". +2 if tag "tourism" equals "viewpoint". +2 if tag "historic" exists on that way. +2 if tag "natural" equals "water". 
5. Repeat step 3 & 4 until agent has reached end location. If mileage within acceptable range (+/- one-querter mile of target range), replace existing q-table with temp q-table. Note: if the run comes up too short or too long, the information we learned during that run could be couterproductive. 
6. Repeat steps 1-5 until algorithm converges. 

Ultimately, you'll have an enourmous q-table with q-values for each possible move that will still loop you from the same location and route your run through the best places the area has to offer (+trails, +views, +history). This entirely answer the question, if I'm at location X on this 5 mile run, which direction should I go next in order to maximize utility? We'll be able to look at the optimal policy the algrithm determines, look at the path and its contents on a map, and determine if the algorithm has learned what we would consider the best policy. 

A successful implementation will yield a running route that is within one-quarter mile of the target mileage for the run and will include the maximum number of waterfront paths and historic landmarks given the vacinity of the users location. This may be challenging, if not impossible, in some cases. For example, the desired start location may be in Nebraska where there is only a single road in two directions for 10+ with no trails, no water, and no historic landmarks in the area. Since success in that instance would not be acheivable, this implementation will narrow the geographic boundaries considered for training to a protion of Malden, Melrose, and Winchester, Masachussettes the majority of which is called the Middlesex Fells Reservation. A successful algorithm will have the ability to render the best (optimal) running route from most any location and should be tested as such.



In this section, clearly describe a solution to the problem. The solution should be applicable to the project domain and appropriate for the dataset(s) or input(s) given. Additionally, describe the solution thoroughly such that it is clear that the solution is quantifiable (the solution can be expressed in mathematical or logical terms) , measurable (the solution can be measured by some metric and clearly observed), and replicable (the solution can be reproduced and occurs more than once).

### Benchmark Model
_(approximately 1-2 paragraphs)_

In this section, provide the details for a benchmark model or result that relates to the domain, problem statement, and intended solution. Ideally, the benchmark model or result contextualizes existing methods or known information in the domain and problem given, which could then be objectively compared to the solution. Describe how the benchmark model or result is measurable (can be measured by some metric and clearly observed) with thorough detail.

### Evaluation Metrics
_(approx. 1-2 paragraphs)_

In this section, propose at least one evaluation metric that can be used to quantify the performance of both the benchmark model and the solution model. The evaluation metric(s) you propose should be appropriate given the context of the data, the problem statement, and the intended solution. Describe how the evaluation metric(s) are derived and provide an example of their mathematical representations (if applicable). Complex evaluation metrics should be clearly defined and quantifiable (can be expressed in mathematical or logical terms).

### Project Design
_(approx. 1 page)_

In this final section, summarize a theoretical workflow for approaching a solution given the problem. Provide thorough discussion for what strategies you may consider employing, what analysis of the data might be required before being used, or which algorithms will be considered for your implementation. The workflow and discussion that you provide should align with the qualities of the previous sections. Additionally, you are encouraged to include small visualizations, pseudocode, or diagrams to aid in describing the project design, but it is not required. The discussion should clearly outline your intended workflow of the capstone project.

-----------

**Before submitting your proposal, ask yourself. . .**

- Does the proposal you have written follow a well-organized structure similar to that of the project template?
- Is each section (particularly **Solution Statement** and **Project Design**) written in a clear, concise and specific fashion? Are there any ambiguous terms or phrases that need clarification?
- Would the intended audience of your project be able to understand your proposal?
- Have you properly proofread your proposal to assure there are minimal grammatical and spelling mistakes?
- Are all the resources used for this project correctly cited and referenced?