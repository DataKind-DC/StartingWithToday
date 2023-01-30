#DataKind DC Hackathon @Georgetown University
#Date: October 22, 2022
#Organization: Starting With Today
#Volunteer: Alex Adams (thisismyusername11199@gmail.com)
#Updates through Jan 2023 by Glenn. 
#2.1a separates data from workshops and community events; no longer merge dummy rows

rm (list = ls())
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
setwd ("C:/Users/Public/Documents/Work/StartingWithToday/")
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
#rm(df)

### Load other data (community / online event), Dec 11 2022 GH
### Jan 25 2023 GH - no longer merge
years_online = 2018:2021
data_events = data [0:0,]
data_events = data_events %>% mutate (EventType = "")

for (year in years_online){
  tmp = data_events
  filename <-
    paste0(
      getwd(),
      '/Data/raw data/',
      'swt_',
      as.character(year),
      '_raw.xlsx'
      #'_attend.xlsx'
    )
  ### Hard coded sheet names
  if (year %in% c(2018)) {
    df <-
      readxl::read_excel(
        filename,
        col_types = 'text',
        sheet = 'Online & Community Events '
      ) %>%
      mutate(year = year)
  } else if (year %in% c(2019)) {
    df <-
      readxl::read_excel(
        filename,
        col_types = 'text',
        sheet = 'Online & Community Events'
      ) %>%
      mutate(year = year)
  } else {
    df <- 
      readxl::read_excel(
        filename,
        col_types = 'text',
        sheet = 'Online & Community events progr'
      ) %>%
      mutate(year = year)
  }

  # add dummy data for each workshop. maybe a case statement to assign Workshop Category
  df$`In-person` = as.numeric(df$`In-person`)
  df$`In-person` = ifelse ( is.na (df$`In-person`), 0, df$`In-person`)
  df$`Online` = as.numeric(df$`Viewers/Listeners Total`) - df$`In-person`
  df = df [! (df$Workshop == "" | is.na (df$Workshop)), ]
  for (i in 1:dim(df)[1]){
    inpers = df[i,]$`In-person`
    online = df[i,]$`Online`
    if (!is.na (inpers)) {
      for (j in 1:inpers) {
        wsdate = as.Date(as.numeric(df$Date[i]),origin = '1900-01-01')
        tmp = tmp %>% add_row (Workshop = df$Workshop[i],#paste0(df$Workshop[i]," ",wsdate),
                               year = year,# year (wsdate),
                               EventType = "In Person")
        
      }
    }
    if (!is.na (online)) {
      for (j in 1:online) {
        wsdate = as.Date(as.numeric(df$Date[i]),origin = '1900-01-01')
        tmp = tmp %>% add_row (Workshop = df$Workshop[i],#paste0(df$Workshop[i]," ",wsdate),
                               year = year,# (wsdate),
                               EventType = "Online"
                               )
      }
    }
    
  }
  
  data_events = tmp
}
### end new data


# Read in workshop categories ----

#Load in workshop categories
categories <-
  readxl::read_xlsx(
    './Data/raw data/Workshop Categories.xlsx',
    sheet = 'Workshop names'
  )

categories = categories %>%
  distinct (Workshop, .keep_all = TRUE)

#Join data to categories
data <-
  data %>%
  left_join(
    categories,
    by = 'Workshop'
  )

data_events <-
  data_events %>%
  left_join(
    categories,
    by = 'Workshop'
  )

# Create some data visualizations ----

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
ggsave (width = 12, height = 6, filename = './visualizations/Number of Attendees at SWT Workshops by Age Range, 2014-2020.png')

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
ggsave (width = 12, height = 6, filename = './visualizations/Number of Attendees at SWT Workshops by Category, 2014-2020.png')



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
ggsave (width = 12, height = 6, filename = './visualizations/Number of Attendees at SWT Workshops by Gender, 2015-2020.png')

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
ggsave (width = 12, height = 6, filename = './visualizations/Number of Attendees at SWT Workshops, 2014-2020.png')

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
      y = count
    )
  ) +
  geom_col(position = 'dodge',
           fill = '#af1f27') +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 60, vjust = 0.5)) +
  ggtitle('Number of Attendees at SWT Workshops per Category',
          subtitle = '2014-2020') +
  ylab('Number of Attendees') +
  xlab('Workshop Category') +
  labs(caption = 'Data Provided by Starting With Today')
ggsave (width = 12, height = 6, filename = './visualizations/Number of Attendees at SWT Workshops per Category.png')


# Group by gender/year ------------------------------------------------

# View(data %>%
#        group_by(year,
#                 `Gender`) %>%
#        summarise(count = n()) %>%
#        ungroup())

write.csv (data, file = "swt_data_workshops.csv")
write.csv (data_events, file = "swt_data_events.csv")
#getwd()

# make a new set of plots, online incl




# EVENTS PLOTS BELOW
#Group data by workshop category and year
data_events %>%
  group_by(
    `Workshop Category`,
    EventType,
    year
  ) %>%
  #Count number of occurrences 
  summarise(
    count = n()
  ) %>%
  #Ungroup
  ungroup() %>%
  #Pipe data_events into bar chart
  ggplot(
    aes(
      x = factor(year),
      y = count,
      fill = `Workshop Category`,
      color = EventType)) +
  geom_col(position = 'dodge', linewidth = .6) +
  theme_bw() +
  #Fill colors with official SWT colors
  scale_fill_manual(values = c('#af1f27',
                               '#f1e21f',
                               '#56B4E9',
                               '#0066CC',
                               '#1a8c47')) +
  scale_color_manual(values = c('black', 'red')) +
  #Make sure all labels are present
  theme(axis.text.x = element_text(angle = 60, vjust = 0.5)) +
  #Add plot title and axis labels
  ggtitle('Number of Attendees at SWT Online and Community Events by Category, 2018-2021') +
  ylab('Number of Attendees') +
  xlab('Year') +
  labs(caption = 'Data Provided by Starting With Today')
ggsave (width = 12, height = 6, filename = './visualizations/Number of Attendees at SWT Online and Community Events by Category, 2018-2021.png')




data_events %>%
  group_by(
    year,
    EventType
  ) %>%
  summarise(
    count = n()
  ) %>%
  ungroup() %>%
  ggplot(
    aes(
      x = factor(year),
      y = count,
      fill = EventType)) +
  geom_col(position = 'dodge') +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 60, vjust = 0.5)) +
  ggtitle('Number of Attendees at SWT Online and Community Events, 2018-2021') +
  ylab('Number of Attendees') +
  xlab('Year') +
  labs(caption = 'Data Provided by Starting With Today')
ggsave (width = 12, height = 6, filename = './visualizations/Number of Attendees at SWT Online and Community Events, 2018-2021.png')

# Attendees Per Category ----
data_events %>%
  group_by(
    `Workshop Category`,
    EventType
  ) %>%
  summarise(
    count = n()
  ) %>%
  ungroup() %>%
  ggplot(
    aes(
      x = factor(`Workshop Category`),
      y = count,
      fill = EventType)) +
  geom_col(position = 'dodge') +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 60, vjust = 0.5)) +
  ggtitle('Number of Attendees at SWT In-Person Community Events by Category',
          subtitle = '2018-2021') +
  ylab('Number of Attendees') +
  xlab('Workshop Category') +
  labs(caption = 'Data Provided by Starting With Today')
ggsave (width = 12, height = 6, filename = './visualizations/Number of Attendees at SWT Online and Community Events per Category In Person.png')

data_events %>%
  filter (EventType == "In Person") %>%
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
  ggtitle('Number of Attendees at SWT In-Person Community Events by Category',
          subtitle = '2018-2021') +
  ylab('Number of Attendees') +
  xlab('Workshop Category') +
  labs(caption = 'Data Provided by Starting With Today')
ggsave (width = 12, height = 6, filename = './visualizations/Number of Attendees at SWT Online and Community Events per Category In Person.png')

data_events %>%
  filter (EventType == "Online") %>%
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
  ggtitle('Number of Attendees at SWT Online Events by Category',
          subtitle = '2018-2021') +
  ylab('Number of Attendees') +
  xlab('Workshop Category') +
  labs(caption = 'Data Provided by Starting With Today')
ggsave (width = 12, height = 6, filename = './visualizations/Number of Attendees at SWT Online and Community Events per Category Online.png')


# EVENT PLOTS DONE
