FROM python:3.8-slim-buster

# Install the security updates.
RUN apt-get update && apt-get -y upgrade

# Install the required dependencies.
RUN apt-get install -y libgl1-mesa-glx libgomp1

# Remove all cached file. Get a smaller image.
RUN apt-get clean && \ 
    rm -rf /var/lib/apt/lists/*

# Copy the application.
COPY /app /app
WORKDIR /app

# Install the app librairies.
RUN pip install -r requirements.txt

# Start the app.
ENTRYPOINT [ "python" ]
CMD [ "main.py" ]