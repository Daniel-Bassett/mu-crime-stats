# MU Crime Stats

## Introduction
This is a brief exploration of the publicly available <a href='http://muop-mupdreports.missouri.edu/dclog.php'>MU crime log </a>. The data was scraped directly from the site, cleaned, and examined. 
The resulting data and analysis were then used to create a web application showing the crime trends in around the MU campus. The web app is not complete, but there are some interesting visualizations 
currently available for data between October 2019 and April 2023. The unfinished app can be found <a href='https://mu-crime-stats.streamlit.app/'>here</a>.

## Key Steps
### Data Scraping
- <a href='https://github.com/Daniel-Bassett/mu-crime-stats/blob/master/scrapers/mu_crime_scraper.ipynb'>Scraped</a> the MU crime log.
- <a href='https://github.com/Daniel-Bassett/mu-crime-stats/blob/master/wrangler/data_wrangler.ipynb'>Cleaned</a> the crime log in preparation for geocoding.
- <a href='https://github.com/Daniel-Bassett/mu-crime-stats/blob/master/scrapers/crime_geocode_scraper.ipynb'>Geocoded</a> the address data.

### Exploratory Data Analysis
- <a href='https://github.com/Daniel-Bassett/mu-crime-stats/blob/master/eda/eda.ipynb'>Performed</a> exploratory data analysis on data. This also included further munging.

### Web Application 
- <a href='https://github.com/Daniel-Bassett/mu-crime-stats/blob/master/app.py'>Built</a> web app with cleaned data.

## Refinement
- Finish web application
- The machine learning results are weak. It needs more data, better feature engineering, and a more balanced data set perhaps by over/under sampling
- Create an automated pipeline including scraping, processing, and storing new data. Look into AWS Lamda for running scripts at set intervals 
