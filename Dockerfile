 
# FROM python:3.11-slim AS builder 
# WORKDIR /app 
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1 
# RUN apt-get update && apt-get clean && apt-get install -y \
#   build-essential \
#   curl \
#   software-properties-common \
#   git \
#   && rm -rf /var/lib/apt/lists/*

# # Create a virtualenv to keep dependencies together
# RUN python -m venv /opt/venv
# ENV PATH="/opt/venv/bin:$PATH" 
# COPY requirements.txt .

# # Install the Python dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# # Stage 2 - Copy only necessary files to the runner stage

# # The FROM instruction initializes a new build stage for the application
# FROM python:3.11-slim

# # Define the filename to copy as an argument
# ARG FILENAME=app.py

# # Deefine the port to run the application on as an argument
# ARG PORT=80

# # Set an environment variable
# ENV FILENAME=${FILENAME}

# # Sets the working directory to /app
# WORKDIR /app

# # Copy the virtual environment from the builder stage
# COPY --from=builder /opt/venv /opt/venv

# # Set environment variables
# ENV PATH="/opt/venv/bin:$PATH"

# # Clone the $FILENAME containing the application code
# COPY $FILENAME .

# # Copy the chainlit.md file to the working directory
# COPY chainlit.md .

# # Copy the .chainlit folder to the working directory
# COPY ./.chainlit ./.chainlit
# COPY ./public ./public
# COPY ./public/CollapsiblePanel.css ./CollapsiblePanel.css
# COPY ./realtime ./realtime

# # The EXPOSE instruction informs Docker that the container listens on the specified network ports at runtime.
# # For more information, see: https://docs.docker.com/engine/reference/builder/#expose
# EXPOSE 8080 
# CMD [ "chainlit", "run", "app.py", "-h","--host", "0.0.0.0", "--port", "8080"]   


 
FROM python:3.9 
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
COPY chainlit.md .
COPY app.py .
COPY ./.chainlit ./.chainlit
COPY ./public ./public
COPY ./public/CollapsiblePanel.css ./CollapsiblePanel.css
COPY ./realtime ./realtime
EXPOSE 8080 
CMD [ "chainlit", "run", "app.py", "-h","--host", "0.0.0.0", "--port", "8080"]  
