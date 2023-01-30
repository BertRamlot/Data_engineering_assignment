import os
import re
import pandas as pd
from collections import Counter


class StackOverflowSurvey:
    def __init__(self):
        self._data_path = "data/"

        # Mappings to convert non-trivial strings to floats
        self._age_mapping: dict[str, float] = {
            "Younger than 5 years": 4.0,
            "Under 18 years old": 17.0,
            "Older than 64 years": 65.0,
            "65 years or older": 66.0,
            "Older than 85": 86.0
        }
        
        # Load the iso mapping (ISO 3166-1), contains extra entries to comply with the stackoverflow survey options
        # https://en.wikipedia.org/wiki/ISO_3166-1
        self._iso_mapping: pd.DataFrame = pd.read_csv(
            f"{self._data_path}/ISO_mapping.csv",
            escapechar='\\'
        )
        
        # Load the gdp data
        # https://ec.europa.eu/eurostat/databrowser/view/tec00001/default/table?lang=en
        gdp_df = pd.read_csv(
            f"{self._data_path}/eu_gdp_data.csv",
            usecols=["unit", "geo", "TIME_PERIOD", "OBS_VALUE"]
        )
        gdp_df = gdp_df[gdp_df["unit"]=="CP_EUR_HAB"].drop(columns=["unit"])
        gdp_df = gdp_df.rename(columns={"geo": "Alpha-2 code", "TIME_PERIOD": "year", "OBS_VALUE": "CP_EUR_HAB"})
        self._gdp_data: pd.DataFrame = pd.merge(self._iso_mapping, gdp_df, on="Alpha-2 code", how='left')
        
    def get_all_data(self, year: int|str) -> pd.DataFrame:
        """
        Get the complete Stack Overflow survey data for the given year.
        :param year: The year of the survey.
        :return: A Pandas dataframe containing the survey data for the given year.
        """
        survey_path = f"{self._data_path}/stack-overflow-developer-survey/results_{year}.csv"
        if not os.path.exists(survey_path):
            # Download the missing csv file
            # Very rudementary download, unzip routine. But runs very infrequently.
            import requests
            import zipfile
            import io

            response = requests.get(f"https://info.stackoverflowsolutions.com/rs/719-EMH-566/images/stack-overflow-developer-survey-{year}.zip")
            z = zipfile.ZipFile(io.BytesIO(response.content))

            allowed_csv_names = [
                    "survey_results_public.csv",
                    f"{year} Stack Overflow Developer Survey Responses.csv",
                    f"{year} Stack Overflow Survey Results.csv"
                ]
            csv_name = next((p for p in allowed_csv_names if p in z.namelist()), None)
            if csv_name is None:
                raise Exception("Failed to find survey csv in zip")

            z.extract(csv_name, path=f"{self._data_path}/stack-overflow-developer-survey")
            os.rename(f"{self._data_path}/stack-overflow-developer-survey/{csv_name}", survey_path)

        # Load survey data, use 'latin1' encoding to handle/ignore non-utf-8 characters
        survey_df = pd.read_csv(
            survey_path,
            encoding="latin1",
            keep_default_na=False
        )
        iso_tagged_df = pd.merge(survey_df, self._iso_mapping, on=["Country"], how="left")
        return iso_tagged_df
    
    def get_first_coding_age_data(self, year: int|str) -> tuple[pd.DataFrame, list[tuple[str, float]]]:
        """
        Retrieve the mass function of the first coding age of each surveyed country.
        :param year: The year of the survey.
        :return: Tuple:
        - first element: data frame containing the mass function.
        - second element: sorted mapping of the age range to a numerical value.
        """
        raw_df = self.get_all_data(year)

        # Map the age ranges to a single number
        invalid_age_columns = []
        ages_mapped = []
        for col in set(raw_df["Age1stCode"]):
            if col in self._age_mapping:
                age = self._age_mapping[col]
            elif col.isdigit():
                age = float(col)
            else:
                result = re.compile(r"^(\d+)\ ?-\ ?(\d+)\ ").search(col)
                if result:
                    # e.g. "11 - 17 years" -> (11, 17) -> 14
                    age_lb, age_ub = int(result.group(1)), int(result.group(2))
                    age = (age_ub+age_lb)/2.0
                else:
                    # No valid age conversion was found
                    # Allowed to happen for 'NA' etc.
                    invalid_age_columns.append(col)
                    continue
            ages_mapped.append((col, age))
        ages_mapped.sort(key=lambda t:t[1])
        age_columns = [t[0] for t in ages_mapped]

        # Group by country (iso-code) and count age range occurences
        age_occurences_df = raw_df.groupby("Alpha-2 code")["Age1stCode"].apply(Counter).unstack(level=-1).reset_index()

        # Merge with gdp data
        merged_df = pd.merge(age_occurences_df, self._gdp_data[self._gdp_data["year"] == year], on=["Alpha-2 code"], how="left")
        merged_df.drop(merged_df.filter(invalid_age_columns), inplace=True, axis=1)

        # Only use countries with available gdp data
        merged_df = merged_df[merged_df["CP_EUR_HAB"].notnull()]

        # Convert the absolute occurences to a probability mass function & amount of samples
        age_df = merged_df[age_columns].fillna(0)
        merged_df["samples"] = age_df.sum(axis=1)
        merged_df[age_columns] = age_df.div(merged_df["samples"], axis='rows')

        # Add year and de-fragment frame
        merged_df["year"] = year
        merged_df = merged_df.copy()

        return merged_df, ages_mapped
