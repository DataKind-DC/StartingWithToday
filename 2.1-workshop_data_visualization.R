#DataKind DC Hackathon @Georgetown University
#Date: October 22, 2022
#Organization: Starting With Today
#Volunteer: Alex Adams (thisismyusername11199@gmail.com)

# Packages ----
require (tidyverse)
require (lubridate)
require(dplyr)
require(ggplot2)

# Read in Data ----
#List of years
years <-
  c(2014:2020)

#Instantiate new empty data frame
data <-
  data.frame()

#Loop over years, read in data
setwd("./StartingWithToday/")
for (year in years){
  filename <-
    paste0(
      getwd(),
      '/Data/raw data/',
      'swt_',
      as.character(year),
      '_raw.xlsx'
      #'_attend.xlsx'
    )
  df <-
    readxl::read_excel(
    filename,
    col_types = 'text'
  ) %>%
    mutate(year = year) 
  
  if("Gender:" %in% colnames(df)){
    df <-
      df %>%
      rename('Gender' = `Gender:`)
  }
  
  if("Zip Code:" %in% colnames(df)){
    df <-
      df %>%
      rename('Zip Code' = `Zip Code:`)
  }
  
  if("Age Range (please select one):" %in% colnames(df)){
    df <-
      df %>%
      rename('Age Range' = `Age Range (please select one):`)
  }
  
  data <-
    data %>%
    bind_rows(df)
}

#Remove unneeded object
rm(df)

### Load other data, Dec 11 2022 GH
years_online = 2019:2020
for (year in years_online){
  filename <-
    paste0(
      getwd(),
      '/Data/raw data/',
      'swt_',
      as.character(year),
      '_raw.xlsx'
      #'_attend.xlsx'
    )
  ### QUICK FIX THERE ARE ONLY TWO
  if (year == 2019) {
    df <-
      readxl::read_excel(
        filename,
        col_types = 'text',
        sheet = 'Online & Community Events'
      ) %>%
      mutate(year = year)
  }
  else {
    df <- 
      readxl::read_excel(
        filename,
        col_types = 'text',
        sheet = 'Online & Community events progr'
      ) %>%
      mutate(year = year)
  }
    
  # add dummy data for each workshop. maybe a case statement to assign Workshop Category
  tmp = data
  df$`In-person` = as.numeric(df$`In-person`)
  for (i in 1:dim(df)[1]){
    inpers = df[i,]$`In-person`
    if (!is.na (inpers)) {
      for (j in 1:inpers) {
        wsdate = as.Date(as.numeric(df$Date[i]),origin = '1900-01-01')
        tmp = tmp %>% add_row (Workshop = df$Workshop[i],#paste0(df$Workshop[i]," ",wsdate),
                               year = year (wsdate)
                               )
      }
    }
  }
  
  # data <-
  #   data %>%
  #   tmp
  data = tmp
}
### end new data


# Read in workshop categories ----

#Load in workshop categories
categories <-
  readxl::read_xlsx(
    './Data/raw data/Workshop Categories.xlsx',
    sheet = 'Workshop names'
  )


#Join data to categories
data <-
  data %>%
  left_join(
    categories,
    by = 'Workshop'
  )


# Create some data visualizations ----

# Group # of attendees by category/year ---- 

#Group data by workshop category and year
data %>%
  group_by(
   `Workshop Category`,
   year
  ) %>%
  #Count number of occurrences 
  summarise(
    count = n()
  ) %>%
  #Ungroup
  ungroup() %>%
  #Pipe data into bar chart
  ggplot(
    aes(
      x = factor(year),
      y = count,
      fill = `Workshop Category`)) +
  geom_col(position = 'dodge') +
  theme_bw() +
  #Fill colors with official SWT colors
  scale_fill_manual(values = c('#af1f27',
                               '#f1e21f',
                               '#56B4E9',
                               '#1a8c47')) +
  #Make sure all labels are present
  theme(axis.text.x = element_text(angle = 60, vjust = 0.5)) +
  #Add plot title and axis labels
  ggtitle('Number of Attendees at SWT Workshops by Category, 2014-2020') +
  ylab('Number of Attendees') +
  xlab('Year') +
  labs(caption = 'Data Provided by Starting With Today')
ggsave (filename = './visualizations/Number of Attendees at SWT Workshops by Category, 2014-2020.png')

#Group data by age range and year
data %>%
  group_by(
    `Age Range`,
    year
  ) %>%
  #Count number of occurrences 
  summarise(
    count = n()
  ) %>%
  #Ungroup
  ungroup() %>%
  #Pipe data into bar chart
  ggplot(
    aes(
      x = factor(year),
      y = count,
      fill = `Age Range`)) +
  geom_col(position = 'dodge',
           color = 'black') +
  theme_bw() +
  #Fill colors with official SWT colors
  # scale_fill_manual(values = c('#af1f27',
  #                              '#f1e21f',
  #                              '#1a8c47')) +
  #Make sure all labels are present
  theme(axis.text.x = element_text(angle = 60, vjust = 0.5)) +
  #Add plot title and axis labels
  ggtitle('Number of Attendees at SWT Workshops by Age Range, 2014-2020') +
  ylab('Number of Attendees') +
  xlab('Year') +
  labs(caption = 'Data Provided by Starting With Today')
ggsave (filename = './visualizations/Number of Attendees at SWT Workshops by Age Range, 2014-2020.png')


#Group data by workshop category and year
data %>%
  mutate(Gender = case_when(Gender == 'sistagirl' ~ 'Female',
                            Gender != 'sistagirl' ~ Gender)) %>%
  filter(year != 2014) %>%
  group_by(
    Gender,
    year
  ) %>%
  #Count number of occurrences 
  summarise(
    count = n()
  ) %>%
  #Ungroup
  ungroup() %>%
  #Pipe data into bar chart
  ggplot(
    aes(
      x = factor(year),
      y = count,
      fill = Gender)) +
  geom_col(position = 'dodge') +
  theme_bw() +
  #Fill colors with official SWT colors
  scale_fill_manual(values = c('#af1f27',
                               '#f1e21f',
                               '#1a8c47')) +
  #Make sure all labels are present
  theme(axis.text.x = element_text(angle = 60, vjust = 0.5)) +
  #Add plot title and axis labels
  ggtitle('Number of Attendees at SWT Workshops by Gender, 2015-2020') +
  ylab('Number of Attendees') +
  xlab('Year') +
  labs(caption = 'Data Provided by Starting With Today')
ggsave (filename = './visualizations/Number of Attendees at SWT Workshops by Gender, 2015-2020.png')

# Group by year ----

data %>%
  group_by(
    year
  ) %>%
  summarise(
    count = n()
  ) %>%
  ungroup() %>%
  ggplot(
    aes(
      x = factor(year),
      y = count)) +
  geom_col(position = 'dodge',
           fill = '#1a8c47') +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 60, vjust = 0.5)) +
  ggtitle('Number of Attendees at SWT Workshops, 2014-2020') +
  ylab('Number of Attendees') +
  xlab('Year') +
  labs(caption = 'Data Provided by Starting With Today')
ggsave (filename = './visualizations/Number of Attendees at SWT Workshops, 2014-2020.png')

# Attendees Per Category ----

data %>%
  group_by(
    `Workshop Category`
  ) %>%
  summarise(
    count = n()
  ) %>%
  ungroup() %>%
  ggplot(
    aes(
      x = factor(`Workshop Category`),
      y = count)) +
  geom_col(position = 'dodge',
           fill = '#af1f27') +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 60, vjust = 0.5)) +
  ggtitle('Number of Attendees at SWT Workshops per Category',
          subtitle = '2014-2020') +
  ylab('Number of Attendees') +
  xlab('Workshop Category') +
  labs(caption = 'Data Provided by Starting With Today')
ggsave (filename = './visualizations/Number of Attendees at SWT Workshops per Category.png')


# Group by gender/year ------------------------------------------------

View(data %>%
       group_by(year,
                `Gender`) %>%
       summarise(count = n()) %>%
       ungroup())

write.csv (data, file = "swt_alldata.csv")
#getwd()
