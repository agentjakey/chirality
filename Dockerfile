FROM python:3.11-slim

# Hugging Face Spaces sets HOME to /home/user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system libraries needed by scipy and matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    libopenblas-dev \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies before copying source (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY src/          ./src/
COPY scripts/      ./scripts/
COPY notebooks/    ./notebooks/
COPY assets/       ./assets/
COPY docs/         ./docs/
COPY app.py        .
COPY healthcheck.py .

# Create outputs directory structure so the app can write to it
RUN mkdir -p outputs/panels outputs/movies outputs/star_ascidian \
             outputs/phase_diagrams outputs/reference outputs/data

# Expose the port Hugging Face Spaces expects
EXPOSE 7860

# Verify environment, then start Streamlit
CMD python healthcheck.py && \
    streamlit run app.py \
        --server.port=7860 \
        --server.address=0.0.0.0 \
        --server.headless=true \
        --server.enableCORS=false \
        --server.enableXsrfProtection=false
