# Python-Task

For this project I have used Python V3.9.2, for database I have used PostgreSQL. I have created a virtual environment called myenv by running this command: python3 -m venv myenv. I have installed all the required packages for the project to work in this virtual environment,and to activate it I had to run this command: myenv/Scripts/activate. 

For the project to work, it is required to first initialize the database and to populate the tables with data. This is done by running the create_db.py file in terminal.

Before running the file, you first need to download the following dependencies:
pip install uvicorn
pip install fastapi
pip install sqlalchemy
pip install jinja2
pip install psycopg2
pip install fastapi uvicorn asyncpg

In addition, you also need to open pgAdmin4, create a new database titled 'pythontask' and if required change the database username, port, password, host or name in the create_db.py file.

After the dependencies are downloaded and the database has been created in pgadmin, you need to open the terminal in your project location and type: python create_db.py

This will create 5 tables and will then fill these tables with the data from the arxiv-metadata-oai-snapshot.json file.

Once the tables are filled, we need to initialize a web server. We have used the Uvicorn web server by typing the command below on the terminal and we can then open the web application on our localhost:8080 url:

uvicorn main:app --host 0.0.0.0 --port 8080

Once you do this, you will be able to open your browser on localhost:8080 and see the main.py project.