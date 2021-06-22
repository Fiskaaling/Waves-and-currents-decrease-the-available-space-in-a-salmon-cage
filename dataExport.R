#This extracts data from raw echo files and exports csv files

library(devtools)
library(SimradRaw)
library(oce)
library(grid)

dataPath = "./"

files = list.files(dataPath, pattern = "\\.raw$")


for (file in 1:length(files))
{
  filename = paste(dataPath, files[file], sep = "")
  print(filename)
  rawData <- readEKRawOld(toString(filename), t = "all", minTimeDiff = Inf)

  ttime <- rawData$data$pings$time #Extract times
  tttime <- as.POSIXct.Date(ttime[1, ]) #Convert to date objects.
  fn = files[file]
  prettyTime = paste(substring(fn, 2, 5), '-', substring(fn, 6, 7), '-', substring(fn, 8, 9), ' ', substring(fn, 12, 13), ':', substring(fn, 14, 15),  ':', substring(fn, 16, 17),sep="")
  print(prettyTime)
  refDate <-
    as.POSIXct(prettyTime, tz = "GMT") #Saves the correct starting point. Adjust for correct starting point
  ttttime = tttime - tttime[1] + refDate #Calculates the correct times based on previous time codes
  write.table(ttttime, paste(substring(fn,1, 17), '-times.csv', sep=""), sep = "\t")
  print(paste(substring(fn,1, 17), '-times.csv', sep=""))

  temp = rawData$data$pings$power
  echo1 = list()
  echo2 = list()

  for (i in 1:length(temp))
  {
    echo1row = temp[[i]][, 1]
    echo1[[i]] = echo1row[1:2000]
    echo2row = temp[[i]][, 2]
    echo2[[i]] = echo2row[1:2000]
  }


  write.table(
    as.data.frame(echo1),
    paste(filename, '1.csv', sep = ""),
    sep = ',',
    row.names = FALSE,
    col.names = FALSE
  )
  write.table(
    as.data.frame(echo1),
    paste(filename, '2.csv', sep = ""),
    sep = ',',
    row.names = FALSE,
    col.names = FALSE
  )
}


