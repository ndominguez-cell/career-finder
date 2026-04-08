# Playwright's official Python image ships all Chromium system deps pre-installed.
# Version must match the playwright pin in requirements.txt (1.49.x → use latest jammy tag).
FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

WORKDIR /app

# Install Python dependencies (includes playwright, PyPDF2, openai, etc.)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure the Playwright Chromium binary is present inside the container
RUN playwright install chromium --with-deps

# Copy the backend application
COPY backend/ ./backend/

# Expose port
EXPOSE 8000

# Launch the app
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
