FROM python:3.10-slim-buster

WORKDIR /app

# Copy requirements.txt from the frontend directory
COPY frontend/requirements.txt ./frontend/requirements.txt
RUN pip install --no-cache-dir -r frontend/requirements.txt

# Copy the entire project into the container
COPY . .

EXPOSE 8501

# Run from the /app directory, specifying the full path to app.py
CMD ["streamlit", "run", "frontend/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]