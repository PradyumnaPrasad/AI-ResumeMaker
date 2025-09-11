FROM python:3.10-slim-buster

WORKDIR /app

# Copy requirements.txt from the backend directory
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the entire project into the container
COPY . .

EXPOSE 8000

# Run from the /app directory, treating 'backend' as a package
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]