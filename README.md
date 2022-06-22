## How to start Django
1. Redirect to `backend` directory
    ```
    cd backend
    ```
2. Create `python` environment and activate it.
    ```
    python -m venv venv-resume-builder
    source venv-resume_builder/bin/activate
    ```

3. Install dependencies
    ```
    pip install -r requirements.txt
    ```
4. Start `Django` server
    ```
    python manage.py runserver
    ```
## How to format python code
```
python scripts/autopep8.py
```
## Build image
```
docker image build -t thequy/resume_builder_django:1.0 .
```
You need to change `thequy` to your docker hub username if you wish to publish your own image to docker hub.  
Google to learn how to publish your docker image.
