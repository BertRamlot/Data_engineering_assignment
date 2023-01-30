# Data engineering assignment - Bert Ramlot

To complete this assignment I used:
- Python 3.10.7
- Jupyter Notebook
- packages listed in [requirements.txt](requirements.txt)

As my data sources I used:
- ISO mappings: https://en.wikipedia.org/wiki/ISO_3166-1
- GDP data: https://ec.europa.eu/eurostat/databrowser/view/tec00001/default/table?lang=en
- Stack Overflow developer survey data from 2021 (and 2020)

The ISO mappings and GDP data come with this respository. The stack overflow survey data is downloaded upon trying to use it. Multiple years of surveys is supported in spirit, but in the interest of time and the widly different formats used by StackOverflow, I focussed soley on the 2021 (and 2020) survey(s).

[src/StackOverflowSurveyData.py](src/StackOverflowSurveyData.py) Downloads and cleans the surveys data, and is used by part 1, 2, and 3 as its 'information source'.

## Solution Part 1
Assignment:
**Determine whether there is a relationship between GDP and the age that developers of a country
first start coding. Extract and create one or more tables to store the data necessary to perform this
comparison. Use a visual plot to support your conclusion(s).**

Solution: [src/gdp_age_correlation_analysis.ipynb](src/gdp_age_correlation_analysis.ipynb) (contains plots)

### In short:
There is probably no statistical significant correlation between the GDP of a country and the age ranges.

### In long:
The situation is a bit more complex due to the mass function of the age ranges being random variables and some data points having few samples. Ideally there would a statistical test for such a problem that takes the variance of the random variable into account (but I know of no such test). Thus I resorted to filtering on the amount of samples (requiring atleast k samples). This is certainly not ideal and this brings its own problems (e.g. amount of samples migth be correlated with gdp, coding age, ...).

I suspected that there would be a correlation, thus I tried to argue that there is one. To do this I tested used the Pearson correlation coefficient.

First I looked at the average coding age, but I was not able to refute the null-hypothesis for non-cherry-picked k values.

Suspecting now that there no correlation, I compared each age range individually to the reference (correcting the p values, see the Multiple comparisons problem) and found again that I was not able to refute the null-hypothesis for non-cherry-picked k values. (The corrected pvalue with relation to k is plotted in the notebook).


To further support my conclusion, I plot the age densities for each country, with a slider to filter on GDP. It is indeed not clear that there is any correlation.

## Solution Part 2
Assigment:
**Create a REST web service that exposes a single method to return both the GDP and youngest coding
age range, using the table(s) defined in Part 1, when the ISO code of a country is supplied as input.
Suggest at least 2 ways that the scalability of this service can be increased.**

Solution: [src/gdp_age_app.py](src/gdp_age_app.py)

I used Flask to create a REST web service. The exposed method uses the supplied ISO code (Alpha-2 or 3 code) to find the correct row in the pre-loaded/computed pandas DataFrame. This row is then used to find the youngest coding range and gdp. The results are returned in a json, with an alternate json returned in case of an error.

Ways to improve the scalability of this service (in the order in which I would consider implementing):
1. As the data doesn't change over time or per user, using any kind of caching system will be highly effictive. I.e. compute and save the appropriate response for all valid ISO-codes.
2. Use a CDN (e.g. Cloudflare)
3. Move the application to the cloud to make use of their extreme scalibility. For this simple of an application, using a serverless function provider seems like a good fit.
4. Use a more performant framework/language. *Generally speaking* [Flask performs rather poor](https://www.techempower.com/benchmarks/#section=data-r21&hw=ph&test=fortune).



## Solution Part 3
Assignment:
**Load the survey results into a SQL table and write a pivot query to list the number of developers by
country for the top 3 programming languages.**

Solution: [src/popular_languages_per_country.ipynb](src/popular_languages_per_country.ipynb)

The notebook above:
- Uses sqlalchemy to easily load the survey results from the pandas DataFrame into a local PostgreSQL server
- Querries that database with the pivot query, and prints the results.

I used the column 'LanguageWorkedWith' to get the top 3 programming languages. This column is only available for 2021.

The SQL table is not cleaned/properly imported, I focussed on the SQL query writing aspect. Properly importing the survey results would most likely lead to moving columns such as 'LanguageWorkedWith' to their own seperate table, which is a valid alternative approach.