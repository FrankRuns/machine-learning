library(ggmap)
library(dplyr)

setwd("/Users/frankcorrigan")

data <- read.csv("route.csv")


stoneplace <- c(-71.07208, 42.44364)
fells_entrance <- c(-71.07397, 42.44374)
# MelroseMap <- qmap(location = c(4.734712,52.268002,5.048166,52.454599), zoom = 12, color = 'bw')
MelroseMap <- qmap(location = fells_entrance, zoom = 17, color = 'bw')
# MelroseMap <- qmap(location = "boston", zoom=10)
sp_s <- 40
sp_e <- 50
showme <- seq(0, nrow(data), 10)
MelroseMap +
  geom_path(aes(x = LON, y = LAT),
            colour="#1E2B6A", data=data, alpha=0.8) +
  geom_text(data=data[c(showme),],
            aes(x=LON, y=LAT, label=rownames(data[c(showme),])),
            size=3,
            position=position_jitter()) +
  #geom_label(data=data[sp_s:sp_e,],
  #           aes(x=LON, y=LAT, label=rownames(data[sp_s:sp_e,])),size=2)
  geom_point(aes(x=-71.0741334,42.4437147), color='red') + 
  geom_point(aes(x=-71.0741807,42.4436882), color='blue') +
  geom_point(aes(x=-71.0740402,42.4437457), color='green') +
  geom_point(aes(x=-71.072104,42.4436421), color='black')
  

test1 <- c(-71.0741807,42.4436882)
test2 <- c(-71.0740402,42.4437457)
fuckedup <- '-71.0741334,42.4437147'
  
1912872951 -- example of footway we dont want
3222127554 -- service road example we dont want

plot(cos(seq(0,400,1)*0.003))
plot(cos(seq(0,400,1)*0.004))

MelroseMap <- qmap(location = fells_entrance, zoom = 17, color = 'bw')
MelroseMap +
  geom_point(aes(x=LON,y=LAT)) +
  geom_point(aes(x=-71.072104,42.4436421),color='red',size=5)

