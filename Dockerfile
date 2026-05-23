FROM python:3.11-slim

# Hugging Face Spaces sets HOME to /home/user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY src/       ./src/
COPY scripts/   ./scripts/
COPY assets/    ./assets/
COPY app.py     .

# Expose the port Hugging Face Spaces expects
EXPOSE 7860

# Run healthcheck at image startup to verify the environment, then start Streamlit
CMD python healthcheck.py && \
    streamlit run app.py \
        --server.port=7860 \
        --server.address=0.0.0.0 \
        --server.headless=true \
        --server.enableCORS=false \
        --server.enableXsrfProtection=false
