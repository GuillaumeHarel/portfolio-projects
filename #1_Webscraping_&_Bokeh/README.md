#1_Webscraping_&_Bokeh
<br>
<br>
<h2><u>Context and objectives</u></h2>
This is a personal project which aims at centralizing in a single app my job searches on several online job boards. To date, in the framework of this project, "only" the APEC and Indeed job websites have been scraped and the job search queries have been restricted to data-related positions in France. 
<br>

This project can be divided into three tasks with distinct purposes: 
<br>
* Web scraping exercise with the Python libraries Selenium and BeautifulSoup; 
* Construction of the personal aggregated job dashboard using the Bokeh libraryFinally;
* Exploratory data analysis of all the information collected in order to have an overall picture of the data-related job market in France and enlighten the most valuable and sought-after soft and hard skills.
<br>
<br>
<u>*Key skills:*</u>
<br>
**Unstructured data**, **Web scraping**, **Text mining**, **Dataviz**, **Text similarity metrics**
<br>
<u>*Key libraries:*</u>
<br>
**Selenium**, **BeautifulSoup**, **Bokeh**, **Pandas**, **Re**
<br>
<br>
## How to use this repo
<br>
<br>
Webscraping and Construction of the custom aggregated job board can be achieved through the didactical notebook or running the raw web_scraping.py file (which mostly corresponds to a raw Copy/Paste of necessary code in the notebook).
<br>
To run the Bokeh interactive dashboard, please follow instructions provided in the Notebook for further details.
<br>
Run Bokeh server "directory format". The name of my directory is web_scraping and it respects the following general architecture:
<br>
<br>
web_scraping
   |
   +---job_db
   |    +---apec_db.xlsx
   |    +---indeed_db.xlsx
   |    +---union_database.xlsx
   |
   +---skill_word_counter
   |    +---skill_word_counter.pkl
   |    +---X_sim.pkl
   |
   +---templates
   |    +---index.html
   |    +---styles.css
   |
   +---main.py
