# ChaCha (CHAtbot for CHildren's emotion Awareness): LLM-Driven Chatbot for Enhancing Emotional Awareness in Children


## System Requirements
1. Python 3.11.2 or higher
2. [Poetry](https://python-poetry.org/docs/) - Python project dependency manager
3. NodeJS and NPM
4. Paid OpenAI API key (ChaCha uses GPT-3.5 and GPT-4 models internally).

## How To Run
### Installation
1. In the root directory, install dependencies using `poetry`.
```shell
> poetry install
```

2. Install frontend Node dependencies
```shell
> cd frontend
> npm install
> cd ..
```

4. Run the setup script and follow the steps. It would help if you prepared the OpenAI API Key ready.
```shell
> poetry run python setup.py
```

### Testing Chatbot on Command Line
3. Run chat.py on the command line:
```shell
> poetry run python chat.py
```

### Testing Chatbot on Web

#### Running in development mode
1. **Run backend server**
    ```shell
    > poetry run python main.py
    ```
    The default port is 8000. You can set `--port` to designate manually.
    ```shell
    > poetry run python main.py --port 3000
    ```
2. **Run frontend server**
   
    The frontend is implemented with React in TypeScript. The development server is run on [Parcel](https://parceljs.org/).
    ```shell
    > cd frontend
    > npm install <-- Run this to install dependencies 
    > npm run dev
    ```
    Access http://localhost:8888 on web browser.

You can perform the above steps using a shell script:
```shell
> sh ./run-web-dev.sh
```


#### Running in production mode

The backend server can serve the frontend web under the hood via the same port.
To activate this, build the frontend code once:

```shell
> cd frontend
> npm run build
```

Then run the backend server:
```shell
> cd ..
> poetry run python main.py --production --port 80
```
Access http://localhost on web browser.

## Authors of the System
* Young-Ho Kim (NAVER AI Lab)
* Woosuk Seo (Intern at NAVER AI Lab, PhD candidate at University of Michigan)
