import unittest

import pandas as pd

from stack_overflow_survey import StackOverflowSurvey


class TestStackOverflowSurvey(unittest.TestCase):
    def setUp(self):
        self.survey = StackOverflowSurvey()
        self.year = 2021

    def test_get_all_data(self):
        all_data = self.survey.get_all_data(self.year)

        self.assertIsInstance(all_data, pd.DataFrame)
        for expected_col in ["Country", "Alpha-2 code", "Alpha-3 code"]:
            self.assertIn(expected_col, all_data.columns)

        self.assertGreater(len(all_data), 0)

    def test_get_country_coding_age_data(self):
        gdp_age_df, age_mapping = self.survey.get_first_coding_age_data(self.year)

        # Check types
        self.assertIsInstance(gdp_age_df, pd.DataFrame)
        self.assertIsInstance(age_mapping, list)
        for key, val in age_mapping:
            self.assertIsInstance(key, str)
            self.assertIsInstance(val, float)
        
        # Check that mapping doesn't contain useless entries
        for age_col, _ in age_mapping:
            self.assertIn(age_col, gdp_age_df.columns)

        for expected_col in ["year", "Country", "Alpha-2 code", "Alpha-3 code", "CP_EUR_HAB"]:
            self.assertIn(expected_col, gdp_age_df.columns)

        self.assertGreater(len(gdp_age_df), 0)


    def test_invalid_year(self):
        self.assertRaises(Exception, self.survey.get_all_data, 1000)


if __name__ == "__main__":
    unittest.main()
