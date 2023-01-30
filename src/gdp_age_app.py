from flask import Flask, jsonify
import pandas as pd
from typing import Dict, Tuple

from stack_overflow_survey import StackOverflowSurvey

surveyData = StackOverflowSurvey()
data, age_mapping = surveyData.get_first_coding_age_data(2021)


app = Flask(__name__)

@app.route("/gdp_and_youngest_age_range/<string:alpha_n_code>", methods=["GET"])
def gdp_and_youngest_coding_age_range(alpha_n_code: str) -> Tuple[Dict, int]:
    global data, age_mapping
    
    if len(alpha_n_code) == 2:
        row = data[data["Alpha-2 code"] == alpha_n_code]
    elif len(alpha_n_code) == 3:
        row = data[data["Alpha-3 code"] == alpha_n_code]
    else:
        row = None
    if row is None or len(row) == 0:
        return jsonify({
                "ISO_code": alpha_n_code,
                "error": "ISO code not found"
            }), 404
    
    youngest_age_range = next((col for col, _ in sorted(age_mapping, key=lambda t: t[1]) if row.iloc[0][col]>0.0), None)
    return jsonify({
            "ISO_code": alpha_n_code,
            "CP_EUR_HAB": row.iloc[0]["CP_EUR_HAB"],
            "youngest_coding_age_range": youngest_age_range
        })


if __name__ == "__main__":
    app.run(debug=True)
