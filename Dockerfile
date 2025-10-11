FROM python:3.10-slim

WORKDIR /app

EXPOSE 8000

# Install curl
RUN apt-get update && apt-get install -y curl 

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project metadata and install dependencies
COPY uv.lock pyproject.toml ./
RUN uv sync

# Copy the rest of the app
COPY tchapia ./

# Run Django dev server
CMD ["uv", "run", "python",  "manage.py", "runserver", "0.0.0.0:8000"]
