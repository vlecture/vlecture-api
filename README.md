# NotebookAI Backend Documentation

## Instructions

### How to install and use the project (for the first time)

1. Clone this repository with the command `git clone https://github.com/jeremyalv/vlecture-api.git`
2. Make sure to enter the directory using `cd notebook-be`
3. Create a virtual environment using `python -m venv env`
4. Run the virtual environment using `source env/bin/activate` for Mac and `env\Scripts\activate.bat` for Windows
5. Install the required modules with `pip install -r requirements.txt`
6. Run the app using `make dev` or `.\build.bat`

### How to run (if you have already installed)

1. Make sure to be in the **notebook-be** directory using `cd notebook-be`
2. Run your virtual environment using `source env/bin/activate` for Mac and `env\Scripts\activate.bat` for Windows
3. Keep your project up-to-date by installing the newest modules using `pip install -r requirements.txt`
4. Run the app using `make dev` or `.\build.bat`

## Running Docker container
1. Build Docker image: `docker build -t notebook-fastapi .`
2. Run image on container port 8080: `docker run -p 8080:8080 notebook-fastapi`
