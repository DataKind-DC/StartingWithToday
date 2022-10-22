
#DataKind DC Hackathon @Georgetown University
#Date: October 22, 2022
#Organization: Starting With Today
#Volunteer: Alex Adams (thisismyusername11199@gmail.com)

# Packages ----
require(dplyr)
require(ggplot2)

# Read in Data ----
years <-
  c(2014:2021)

data <-
  data.frame()

for (year in years){
  filename <-
    paste0(
      'raw data/',
      as.character(year),
      '_attend.xlsx'
    )
  df <-
    readxl::read_excel(
    filename,
    col_types = 'text'
  ) %>%
    mutate(year = year)
  
  data <-
    data %>%
    bind_rows(df)
}

rm(df)

# Read in workshop categories ----
categories <-
  readxl::read_xlsx(
    'Workshop Categories.xlsx',
    sheet = 'Workshop names'
  )

data <-
  data %>%
  left_join(
    categories,
    by = 'Workshop'
  )

# Create some data visualizations ----

# Group # of attendees by category/year ----
data %>%
  group_by(
   `Workshop Category`,
   year
  ) %>%
  summarise(
    count = n()
  ) %>%
  ungroup() %>%
  ggplot(
    aes(
      x = factor(year),
      y = count,
      fill = `Workshop Category`)) +
  geom_col(position = 'dodge') +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 60, vjust = 0.5)) +
  ggtitle('Number of Attendees at SWT Workshops by Category, 2014-2021') +
  ylab('Number of Attendees') +
  xlab('Year') +
  labs(caption = 'Data Provided by Starting With Today')

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
  ggtitle('Number of Attendees at SWT Workshops, 2014-2021') +
  ylab('Number of Attendees') +
  xlab('Year') +
  labs(caption = 'Data Provided by Starting With Today')

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
          subtitle = '2014-2021') +
  ylab('Number of Attendees') +
  xlab('Workshop Category') +
  labs(caption = 'Data Provided by Starting With Today')
