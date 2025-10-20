# Use a slim Python 3.11 image as the base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install the dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files into the container
COPY . .

# Expose the port that Streamlit will use
EXPOSE 5000

# Set the entry point to run the Streamlit app
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port", "5000", "--server.address", "0.0.0.0"]