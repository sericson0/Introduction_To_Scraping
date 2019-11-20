rm(list = ls()) #Clears working memory
usePackage <- function(p) {
  #Helper function to load/install packages
  if (!is.element(p, installed.packages()[,1]))
    install.packages(p, dep = TRUE)
  require(p, character.only = TRUE)
}
#
usePackage("rstudioapi") 
usePackage("tidyverse")
usePackage("readxl")
WD = file.path(dirname(rstudioapi::getSourceEditorContext()$path)) #Sets path to working directory
setwd(WD)
#_________________________________________________________________________________________________________
#_________________________________________________________________________________________________________
#_________________________________________________________________________________________________________
#_________________________________________________________________________________________________________
#Create some directories with dir.create
main_dir = "../Electricity Data"
dir.create(main_dir)
compiled_files = file.path(main_dir, "Compiled Files") 
dir.create(compiled_files)
emissions_dir = file.path(main_dir, "EIA Emissions Raw")
dir.create(emissions_dir)
#_________________________________________________________________________________________________________
#Say we want to download Emissions data from power plants. 
#The EIA has data on emissions at https://www.eia.gov/electricity/data/emissions/ from 2013 to 2018
#Right clicking on a file and then selecting copy link location, we see the data is accessed via a url which looks like
#https://www.eia.gov/electricity/data/emissions/archive/xls/emissions2015.xlsx
#And we also notice that the final year does not have /archive in the name. 
#For each year we use download.file to save the data, and then we compile it to a single file
years = 2013:2018
for(y in years) {
  archive = "archive/"
  if(y == max(years)) archive = ""
  url = paste0("https://www.eia.gov/electricity/data/emissions/",archive,"xls/emissions",y,".xlsx")
  print(url)
  download.file(url, paste0(emissions_dir,"/", "Plant Emissions_", y, ".xlsx"), mode = "wb")
}
##
CO2 = plyr::ldply(list.files(emissions_dir, full.names = TRUE), function(x) read_excel(x, sheet = "CO2", skip = 1))
write_csv(CO2, file.path(compiled_files, "EIA Emissions Data.csv"))
#_________________________________________________________________________________________________________
#_________________________________________________________________________________________________________
#_________________________________________________________________________________________________________
#Yay! We just downloaded and compiled some data from the internet. Congratulations, you are one step
#to getting your PhD. At the same time, we only downloaded 6 files. It would have taken less time to do it manually.
#Lets not step to a problem where automation really shines.

#The EPA keeps hourly data from the Continuous Emissions Monitors (CEMs) for every major facility in the US. 
#The Air Markets Program Data website is https://ampd.epa.gov/ampd/ which says the data sets are available at 
#ftp://newftp.epa.gov/DMDnLoad/emissions/
#Lets compile the hourly data.

#Here are a couple of examples of the links:
# ftp://newftp.epa.gov/DMDnLoad/emissions/hourly/monthly/2010/2010ar01.zip
# ftp://newftp.epa.gov/DMDnLoad/emissions/hourly/monthly/1995/1995al01.zip
#The format seems to be year/year/state_abb/month

states_not_in_set = c("ak", "hi") #Arkansas an Hawaii are not tracked
state_abb = tolower(state.abb) #state.abb gives upper case stae abbreviations
state_abb = state_abb[which(!(state_abb %in% states_not_in_set))]
#
#Full Data
#_________________________________________________________________________________________________________
# month_str = c(paste0("0", 1:9), "10", "11", "12")
# final_months = paste0("0", 1:9) #Currently 2019 only goes up to September
# years = 1995:2019
#_________________________________________________________________________________________________________

# subset of data
month_str = c(paste0("0", 1:3))
final_months = month_str
years = 1995
#Create folder
epa_raw_folder = file.path(main_dir,"EPA Emissions Raw")
dir.create(epa_raw_folder)
##Loop through each value
for(yr in years) {
  print(yr)
  months = month_str
  if(yr == max(years)) months = final_months
  #
  for(state in state_abb) {
    print(state)
    for(m in months) {
      temp = tempfile() #Creates a temp file to save the zip file in
      url = paste0("ftp://newftp.epa.gov/DMDnLoad/emissions/hourly/monthly/",yr,"/",yr,state,m,".zip")
      download.file(url, temp, quiet = TRUE)
      unzip(temp, exdir = epa_raw_folder) #Unzip the csv fil and save it to the epa_raw_folder
      unlink(temp) #Remove the temp file now that we don't need it
    }
  }
}
####
#Load Dataset, supressing warnings
#For full data may have to break this up into several subsets, it is a lot of data afterall
D = plyr::ldply(list.files(epa_raw_folder, full.names = TRUE), function(x) suppressWarnings(read_csv(x, col_types = cols())))

#Save to csv
write_csv(D, file.path(compiled_files, "EPA Data.csv"))

tail(D)
