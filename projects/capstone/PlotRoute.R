library(ggmap)
library(dplyr)

# setwd("/Users/frankcorrigan") # only works on my computer

data <- read.csv("route.csv")

stoneplace_lat <- 42.44364
stoneplace_lon <- -71.07208
fells_entrance <- c(-71.07397, 42.44374)
our_fells <- c(-71.07938, 42.44205)
# jeanne <- c(-73.31783, 40.87651) # testing ny
MelroseMap <- qmap(location = fells_entrance, zoom = 16)
# MelroseMap <- qmap(location = jeanne, zoom = 16) # testing ny
showme <- seq(0, nrow(data), 25)
MelroseMap +
  geom_path(aes(x = LON, y = LAT),
            colour="#1E2B6A", data=data, alpha=0.6, size=1) +
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
  

# Plot any point
'-71.071877,42.445716'
plot_me_lat <- 42.445716
plot_me_lon <- -71.071877
MelroseMap +  geom_point(aes(x=plot_me_lon,plot_me_lat), color='red')       


# Playing with decay
plot(cos(seq(0,400,1)*0.0039))
plot(cos(seq(0,500,1)*1.60/500))
lines(cos(seq(0,500,1)*1.50/500))
lines(cos(seq(0,500,1)*1.40/500))
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
# MelroseMap <- qmap(location = jeanne, zoom = 14) # testing ny
MelroseMap +
  geom_point(data=all_nodes, aes(x=LON,y=LAT),size=1) +
  geom_point(aes(x=-71.072104,42.4436421),color='red',size=5) +
  geom_point(aes(x=-71.0751194,42.4416901),color='blue') +
  geom_point(aes(x=-71.0770067,42.4419444),color='blue')
  

# intersections only
mid_fells <- c(-71.0978,42.4469)
map_intersections <- read.csv("intersections.csv",stringsAsFactors = FALSE)
MelroseMap <- qmap(location = mid_fells, zoom = 14)
# MelroseMap <- qmap(location = jeanne, zoom = 14) # testing ny
MelroseMap +
  geom_point(data=map_intersections, aes(x=LON,y=LAT),size=1) +
  geom_point(aes(x=-71.072104,42.4436421),color='red',size=5) +
  geom_point(aes(x=-71.0751194,42.4416901),color='blue') +
  geom_point(aes(x=-71.0770067,42.4419444),color='blue')