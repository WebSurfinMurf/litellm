FROM python:3.11-slim

WORKDIR /app

# Install required packages
RUN pip install flask requests

# Copy middleware script
COPY mcp-middleware-service.py /app/

# Expose port
EXPOSE 4001

# Run the middleware
CMD ["python", "mcp-middleware-service.py"]