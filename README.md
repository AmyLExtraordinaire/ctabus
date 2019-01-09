# CTA Bus Data Analysis

CTA Bus Data Analysis is an ongoing project to analyze the performance of the Chicago Transit Authority's bus routes. 

Visit the project page: [https://spencerchan.github.io/ctabus](https://spencerchan.github.io/ctabus)

## Motivation
This project started because I kept having bad luck catching the bus. I wanted to know: is the bus schedule for CTA route 55 Garfield overpromising on its mid-afternoon wait times or am I just unlucky? Asked more precisely: is 20 minutes an unreasonable amount of time to wait for an eastbound 55 Garfield bus at the Garfield Red Line Station at 4pm on a weekday? Since answering this question, the project has morphed into something larger and more ambitious.

Even in the face of declining ridership over the past decade, the bus remains a popular way to get around Chicago: the CTA provides over 800,000 bus rides every weekday, totaling to nearly 250 million bus rides each year. In fact, bus rides account for over half of the CTA's daily and annual ridership. With so many Chicagoans depending on the bus each day, it is critical that bus service throughout the city is reliable, fast, and frequent. This is especially true in order to encourage people to start using public transit and to stem further losses in ridership.

The goal of this project is not to offer suggestions to improve service, but to leverage data to highlight issues with the existing service. Some of the questions the project hopes to answer are: what are travel and wait times for each bus route, and how do these times compare to the scheduled service? Which routes experience bus bunching most frequently? Are there areas of the city with better bus performance than others? A secondary goal for the future is to offer a statistical approach to commuting by bus that improves upon individual experience or directions provided by a service like Google Maps.

## Technologies Used
* Python 2.7
* Jupyter
* pandas
* D3.js
* SQLite
* HTML
* JavaScript

## Project Status
The project is actively collecting and analyzing data. Throughout 2019, bus location data will be gathered for all active CTA bus routes—over 120 routes—and will be processed and analyzed on a monthly basis.

## Data Sources
Bus location data is gathered from the CTA [Bus Tracker](http://www.transitchicago.com/developers/bustracker.aspx)’s **`getvehicles`** API at a regular interval via a Python script run as a cron job. The Bus Tracker family of APIs provides near-real-time locations and estimated arrival times of all CTA buses. The API makes accessible only the most recent position for each vehicle, hence the need to regularly access the API and archive the data.

Supporting data, such as the locations of bus stops, also comes from the Bus Tracker API. Read the [documentation](https://github.com/spencerchan/ctabus/blob/master/references/cta_Bus_Tracker_API_Developer_Guide_and_Documentation_20160929.pdf) to learn more about what data is available through the API and how to access it. Scheduled service data is obtained from the [CTA's GTFS feed](https://www.transitchicago.com/developers/gtfs/).

For the purposes of this project, the most important data collected from **`getvehicles`** is the location of each vehicle along its route (`pdist`) and the time the vehicle was at that location (`tmstmp`). We can discover a lot using those two pieces of information, especially when combined with the bus stop location data, including: the speed of a bus, the wait time between two buses at a particular stop, the travel time between two stops, and more.

## Current Analysis
The visualizations on the project website currently focus on bus location data collected during February and March 2017 from the 55 Garfield bus. At present, they show:
* When buses are dispatched throughout the day and week
* The time of day and location along the route where bus bunching occurs most often
* Travel times between any two major stops broken down by time of day
* Wait times between consecutive buses broken down by time of day

## Future Plans
* Process data for all major CTA bus routes each month
* Analyze how each bus route adheres to or deviates from its scheduled service
* Improve project page visualizations and enhance interactivity
* Improve project page functionality on mobile devices
* Improve documentation
* Publish raw data

## Directory structure
```bash
├── data
│   └── processed				# final data sets used in visualizations and analysis
├── flask-bokeh_site				# old flask site with bokeh visualizations 
├── scripts					# D3.js visualizations for current project page
│ 
├── src						# source code for project
│   ├── processing				# data processing scripts
│   └── remote					# scripts to scrape vehicle data from Bus Tracker API
├── .gitignore
├── index.html					# current landing page for project
├── LICENSE
└── README.md
```

## Author
**Spencer Chan**  - [https://github.com/spencerchan](https://github.com/spencerchan)

## Acknowledgments
I started this project as a participant in the Spring 2017 [ChiPy Mentorship Program](https://chipymentor.org). I want to thank my mentor, Matt Hall, for his support and guidance while I learned Python for the first time. Special thanks to the program director, Ray Berg, without whose hard work and organization, the program would not have been possible. Data was collected from the Chicago Transit Authority's [Bus Tracker API](http://www.transitchicago.com/developers/bustracker.aspx).

## License
Released under the [GNU General Public License, version 3](https://opensource.org/licenses/GPL-3.0)
