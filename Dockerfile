ARG UNIT_VARIANT=1.31.1-python3.11

# Initialize virtual environement in a separate build image
# We want to minimize work in target platform image as much as possible as it may run under emulation
FROM unit:${UNIT_VARIANT} AS builder
LABEL stage=builder

# Copy application files
ADD ./pyproject.toml /app/pyproject.toml
ADD ./app /app/app

# Change work directory to application
WORKDIR /app

# Create virtual environement
RUN python3 -m venv /venv

# Install dependencies in virtual environement
RUN /bin/bash -c "source /venv/bin/activate && pip install ."

# Build final image, with target platform
FROM --platform=$TARGETPLATFORM unit:${UNIT_VARIANT}

# Copy application files from build image
COPY --from=builder /app /app

# Copy virtual environment from build image
COPY --from=builder /venv /app/venv

# Copy NGINX Unit configuration
COPY ./nginx/* /docker-entrypoint.d/

# Change work directory to application
WORKDIR /app
