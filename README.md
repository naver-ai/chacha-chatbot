# LLM-Driven Chatbot for Enhancing Emotional Awareness in Children


## System Requirements
1. Python 3.10 or higher
2. [Poetry](https://python-poetry.org/docs/)
3. Paid OpenAI API key

## How To Run
### Installation
1. In the root directory, install dependencies using `poetry`.
```shell
> poetry install
```

2. Run the setup script and follow the steps.
```shell
> python setup.py
```

### Testing Chatbot on Command Line
3. Run chat.py on command line:
```shell
> python chat.py
```

### Testing Chatbot on Web

#### Running on development mode
1. **Run backend server**
    ```shell
    > py main.py
    ```
    The default port is 8000. You can set `--port` to designate manually.
    ```shell
    > py main.py --port 3000
    ```
2. **Run frontend server**
   
    The frontend is implemented with React in TypeScript. The development server is run on [Parcel](https://parceljs.org/).
    ```shell
    > cd frontend
    > npm install <-- Run this to install dependencies 
    > npm run dev
    ```
    Access http://localhost:8888 on web browser.

#### Running on production mode

The backend server can serve the frontend web under the hood, via the same port.
To activate this, build the frontend code once:

```shell
> cd frontend
> npm run build
```

Then run the backend server:
```shell
> cd ..
> python3 main.py --production --port 80
```
Access http://localhost on web browser.

## Author
* Woosuk Seo (Intern at NAVER AI Lab, PhD candidate at University of Michigan)
* Young-Ho Kim (NAVER AI Lab)

# LLM-Driven Chatbot for Enhancing Emotional Awareness in Children

## Prerequisites

Ensure that your system meets the following requirements:

1. Python 3.10 or higher
2. [Poetry](https://python-poetry.org/docs/) - Python package and dependency management tool
3. Paid OpenAI API key

## Setup & Running Instructions

Follow the instructions below to set up and run the project.

### Setup
1. Navigate to the root directory of the project and install the dependencies using `poetry`:
    ```shell
    poetry install
    ```

2. Run the setup script and follow the on-screen prompts:
    ```shell
    python setup.py
    ```

### Test Chatbot in Command Line Interface

To test the chatbot directly in the command line, run the following command:
```shell
python chat.py
```

### Test Chatbot via Web Interface

#### Development Mode

1. **Start the backend server:**
    ```shell
    py main.py
    ```
    The server runs on port 8000 by default. You can use the `--port` argument to specify a different port:
    ```shell
    py main.py --port 8888
    ```

2. **Start the frontend server:**

    The frontend is developed using React in TypeScript and served in a development server via [Parcel](https://parceljs.org/).
    
    Navigate to the frontend directory and install the necessary dependencies:
    ```shell
    cd frontend
    npm install
    ```
    
    Run the development server:
    ```shell
    npm run dev
    ```
    
    Access the application at http://localhost:8888 (or the port you specified) in your web browser.

#### Production Mode

*Instructions to be added*

## Contributing Authors
* Woosuk Seo - Intern at NAVER AI Lab and a PhD candidate at the University of Michigan
* Young-Ho Kim - NAVER AI Lab
