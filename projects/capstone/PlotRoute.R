library(ggmap)
library(dplyr)

setwd("/Users/frankcorrigan")

data <- read.csv("route.csv", stringsAsFactors = FALSE)


stoneplace <- c(-71.07208, 42.44364)
# MelroseMap <- qmap(location = c(4.734712,52.268002,5.048166,52.454599), zoom = 12, color = 'bw')
MelroseMap <- qmap(location = stoneplace, zoom = 17, color = 'bw')
# MelroseMap <- qmap(location = "boston", zoom=10)
MelroseMap +
  geom_path(aes(x = LON, y = LAT),
            colour="#1E2B6A", data=data, alpha=0.2) +
  geom_text(data=data[1:30,],
            aes(x=LON, y=LAT, label=rownames(data[1:30,]),
                color='red'))

