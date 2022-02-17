## Warbler

To get this application running, make sure you do the following in the Terminal:

1. `python3 -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt` may need to manually install based on which version of python is on your machine.
4. `createdb warbler` running on PostreSQL
5. (optional) `python seed.py`
6. `flask run`
