library(ggmap)
library(dplyr)

setwd("/Users/frankcorrigan")

data <- read.csv("route.csv")

stoneplace_lat <- 42.44364
stoneplace_lon <- -71.07208
fells_entrance <- c(-71.07397, 42.44374)
MelroseMap <- qmap(location = fells_entrance, zoom = 15)#, color = 'bw')
showme <- seq(0, nrow(data), 25)
MelroseMap +
  geom_path(aes(x = LON, y = LAT),
            colour="#1E2B6A", data=data, alpha=0.6, size=2) +
  geom_label(data=data[c(showme),],
            aes(x=LON, y=LAT, label=rownames(data[c(showme),])),
            size=1.5
            #position=position_jitter()
            ) +
  geom_label(data=data[nrow(data),],
             aes(x=LON, y=LAT,
                 label=rownames(data[nrow(data),])),
                 size=2,
                 color="red") +
  geom_point(aes(x=stoneplace_lon,stoneplace_lat), color='red')



plot(cos(seq(0,400,1)*0.0039))
plot(cos(seq(0,200,1)*1.60/200))
lines(cos(seq(0,300,1)*1.60/300))
lines(cos(seq(0,300,1)*1.55/300))
cos(n_trials*1.6/n_trials)

plot(cos(seq(0,400,1)*1.55/400))
lines(cos(seq(0,500,1)*0.005))
lines(cos(seq(0,400,1)*0.0036))
plot(cos(seq(0,1000,1)*0.0015))

# all nodes
mid_fells <- c(-71.0978,42.4469)
all_nodes <- read.csv("all_nodes.csv",stringsAsFactors = FALSE)
MelroseMap <- qmap(location = mid_fells, zoom = 14)
MelroseMap +
  geom_point(data=all_nodes, aes(x=LON,y=LAT),size=1) +
  geom_point(aes(x=-71.072104,42.4436421),color='red',size=5) +
  geom_point(aes(x=-71.0751194,42.4416901),color='blue') +
  geom_point(aes(x=-71.0770067,42.4419444),color='blue')
  

# intersections only
mid_fells <- c(-71.0978,42.4469)
map_intersections <- read.csv("intersections.csv",stringsAsFactors = FALSE)
MelroseMap <- qmap(location = mid_fells, zoom = 14)
MelroseMap +
  geom_point(data=map_intersections, aes(x=LON,y=LAT),size=1) +
  geom_point(aes(x=-71.072104,42.4436421),color='red',size=5) +
  geom_point(aes(x=-71.0751194,42.4416901),color='blue') +
  geom_point(aes(x=-71.0770067,42.4419444),color='blue')

cos(n_trials*1.6/n_trials)

c(miles=1, epsilon=gamma=0.1, factor=0.5, trials=50, r=50, rback=-400, rpath=-50, rhigh1=+10000, rhigh2=+200) - bad. goes north, doesnt return, total miles = 1.46
c(miles=1, gamma=0.1, factor=0.5, trials=100, r=50, rback=-400, rpath=-50, rhigh1=+10000, rhigh2=+200) - bad. goes north, doesnt return, goes down side street detours, total miles = 1.48
c(miles=1, gamma=0.1, factor=0.5, trials=200, r=50, rback=-400, rpath=-50, rhigh1=+10000, rhigh2=+200) - good. finds trail, goes out and finds a loop, returns to start location, total miles = 0.98
c(miles=1, gamma=0.1, factor=0.5, trials=300, r=50, rback=-400, rpath=-50, rhigh1=+10000, rhigh2=+200) - bad. goes north, DOES return, straight out and back, total miles = 1.35
c(miles=1, gamma=0.1, factor=0.5, trials=400, r=50, rback=-400, rpath=-50, rhigh1=+10000, rhigh2=+200) - bad. finds trail, doesnt return, after trail detours to up north, total miles = 1.32

c(miles=2, gamma=0.1, factor=0.5, trials=50, r=50, rback=-400, rpath=-50, rhigh1=+10000, rhigh2=+200) - bad. initial attempt fails to map a required path. 2nd attempt goes direct north does not return. total miles = 2.97
c(miles=2, gamma=0.1, factor=0.5, trials=100, r=50, rback=-400, rpath=-50, rhigh1=+10000, rhigh2=+200) - bad. goes north. attempts side street detour. DOES come back. total miles = 1.66
c(miles=2, gamma=0.1, factor=0.5, trials=200, r=50, rback=-400, rpath=-50, rhigh1=+10000, rhigh2=+200) - bad. goes north. break in the path -- bad data? total miles = 2.95
c(miles=2, gamma=0.1, factor=0.5, trials=300, r=50, rback=-400, rpath=-50, rhigh1=+10000, rhigh2=+200) - ok. finds trail. does a loop. ends at start location. falls short on miles. total miles = 1.34
c(miles=2, gamma=0.1, factor=0.5, trials=400, r=50, rback=-400, rpath=-50, rhigh1=+10000, rhigh2=+200) - ok. finds trail. does repeat loops and comes back to start location. total miles = 1.86
c(miles=2, gamma=0.1, factor=0.5, trials=500, r=50, rback=-400, rpath=-50, rhigh1=+10000, rhigh2=+200) - bad. goes north out and back. total miles = 1.99

c(miles=3, gamma=0.1, factor=0.5, trials=50, r=50, rback=-400, rpath=-50, rhigh1=+10000, rhigh2=+200) - bad. only does continuous loop around stone place island. total miles = 0.13
c(miles=3, gamma=0.1, factor=0.5, trials=100, r=50, rback=-400, rpath=-50, rhigh1=+10000, rhigh2=+200) - ok. finds trail, but excissive looping in close proximity trails total miles = 1.93
c(miles=3, gamma=0.1, factor=0.5, trials=200, r=50, rback=-400, rpath=-50, rhigh1=+10000, rhigh2=+200) - bad. goes north. overlapping route. total miles = 4.4
c(miles=3, gamma=0.1, factor=0.5, trials=300, r=50, rback=-400, rpath=-50, rhigh1=+10000, rhigh2=+200) - bad. finds trail, but keeps looping in local proximity. total miles = 2.91
c(miles=3, gamma=0.1, factor=0.5, trials=400, r=50, rback=-400, rpath=-50, rhigh1=+10000, rhigh2=+200) - 
c(miles=3, gamma=0.1, factor=0.5, trials=500, r=50, rback=-400, rpath=-50, rhigh1=+10000, rhigh2=+200)



