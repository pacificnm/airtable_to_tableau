#!/usr/bin/env python3
# start_web.py

from airtable_to_tableau.web.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)