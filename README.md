# Analyzing CTA Bus Data

Analyzing CTA Bus Data is an ongoing project to analyze the performance of the Chicago Transit Authority's bus routes. 

Visit the project page: [https://spencerchan.github.io/ctabus](https://spencerchan.github.io/ctabus)

## Technologies Used
* Python 2.7
* Jupyter
* pandas
* D3.js
* SQLite
* HTML
* JavaScript

## The Project

### Announcements and Updates
During 2019, location data will be gathered for all active CTA bus routes. That's over 120 bus routes! The efficiency of the data processing scripts has improved greatly in anticipation of the large volume of new data. Stay tuned as processed data from new bus routes are added to the project.

### The Data
Bus location data is gathered from the CTA [Bus Tracker's](http://www.transitchicago.com/developers/bustracker.aspx). **`getvehicles`** API at a regular interval via Python script scheduled with cron. The Bus Tracker family of APIs provides near-real-time locations and estimated arrival times of all CTA buses. The API makes accessible only the *latest* vehicle positions, hence the need to regularly access the API and archive the data.

Supporting data, such as the locations of bus stops also comes from the Bus Tracker API. Scheduled service data is obtained from the [CTA's GTFS feed](https://www.transitchicago.com/developers/gtfs/)

For the purposes of this project, the most important data collected from **`getvehicles`** is the location of each vehicle along its route (`pdist`) and the time the vehicle was at that location (`tmstmp`). Much can be gleaned from this little bit of information, especially when combined with the bus stop location data, including: the speed of a bus, the wait time between two buses at a particular stop, the travel time between two stops, and more.

### Current Features
The visualizations on the project website currently focus on bus location data collected during February and March 2017 from the 55 Garfield bus. At present, you are able to discover:
* When buses are dispatched throughout the day and week
* The time of day and location along the route where bus bunching occurs most often
* Travel times between any two major stops broken down by time of day
* Wait times between consecutive buses broken down by time of day

### Future Plans
* Process data for all major CTA bus routes each month
* Analyze how each bus route adheres to or deviates from its scheduled service
* Improve project page visualizations and enhance interactivity
* Improve project page functionality on mobile devices
* Improve documentation
* Publish raw data

### Old Features
This project originally existed as a flask site with interactive visualizations created using Bokeh.

## Scrape Your Own Bus Tracker Data
1. Download the data collection scripts and supporting files located in `src/remote/`.
2. Install the required packages and [sqlite3](https://www.sqlite.org/download.html). The scripts only support Python 2.7+ at this time.
3. Acquire a Bus Tracker [API Key](https://www.transitchicago.com/developers/bustracker/).
4. Run ```make table``` to initialize a SQLite database.
5. If desired, set up a cron job to schedule regular data requests from the Bus Tracker API.

## Directory structure
```bash
├── data
│   └── processed				# final data sets used in visualizations
├── flask-bokeh_site				# old flask site with bokeh visualizations 
├── scripts					# D3.js visualizations for current project page
│ 
├── src						# source code for project
│   ├── notebooks				# data processing scripts
│   └── remote					# scripts to scrape vehicle data from Bus Tracker API
├── .gitignore
├── index.html					# current landing page for project
├── LICENSE
└──	README.md
```

## Author
**Spencer Chan**  - [https://github.com/spencerchan](https://github.com/spencerchan)

## Acknowledgments
I started this project as a participant in the Spring 2017 [ChiPy Mentorship Program](https://chipymentor.org). I want to thank my mentor, Matt Hall, for his support and guidance while I learned Python for the first time. Special thanks to the program director, Ray Berg, without whose hard work and organization, the program would not have been possible. Data was collected from the Chicago Transit Authority's [Bus Tracker API](http://www.transitchicago.com/developers/bustracker.aspx).

## License
Released under the [GNU General Public License, version 3](https://opensource.org/licenses/GPL-3.0)
