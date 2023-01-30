import unittest

import gdp_age_app


class TestGdpAgeApp(unittest.TestCase):
    def setUp(self):
        self.endpoint = "/gdp_and_youngest_age_range"
        self.app = gdp_age_app.app.test_client()

    def test_valid_iso_code(self):
        response = self.app.get(f"{self.endpoint}/BEL")
        self.assertEqual(response.status_code, 200)
        self.assertIn("ISO_code", response.json)
        self.assertIn("youngest_coding_age_range", response.json)
        self.assertIn("CP_EUR_HAB", response.json)

    def test_invalid_iso_code(self):
        response = self.app.get(f"{self.endpoint}/ZZZ")
        self.assertEqual(response.status_code, 404)
        self.assertIn("ISO_code", response.json)
        self.assertIn("error", response.json)


if __name__ == "__main__":
    unittest.main()
