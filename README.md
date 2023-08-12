# ChaCha (CHAtbot for CHildren's emotion Awareness): LLM-Driven Chatbot for Enhancing Emotional Awareness in Children


## System Requirements
1. Python 3.11.2 or higher
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
3. Run chat.py on the command line:
```shell
> python chat.py
```

### Testing Chatbot on Web

#### Running in development mode
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
> python3 main.py --production --port 80
```
Access http://localhost on web browser.

## Author
* Woosuk Seo (Intern at NAVER AI Lab, PhD candidate at University of Michigan)
* Young-Ho Kim (NAVER AI Lab)
