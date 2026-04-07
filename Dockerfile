# Use an official Python runtime as a parent image
# We use the official Playwright image to ensure all Chromium dependencies are present
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install PyPDF2  # Added manually since it was installed dynamically

# Install Playwright browsers (already in the image, but good to be explicit)
RUN playwright install chromium

# Copy the rest of the backend application
COPY backend/ ./backend/

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
