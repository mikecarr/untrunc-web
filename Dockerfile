# Use a base image with Python
FROM ubuntu:22.04 AS build
LABEL stage=intermediate
ARG FF_VER=shared

# install packaged dependencies
RUN apt-get update && [ "$FF_VER" = 'shared' ] && \
	apt-get -y install --no-install-recommends libavformat-dev libavcodec-dev libavutil-dev g++ make git python3-pip || \
	apt-get -y install --no-install-recommends yasm wget g++ make git ca-certificates xz-utils  && \
	rm -rf /var/lib/apt/lists/*


# Clone and build untrunc
RUN git clone https://github.com/anthwlock/untrunc.git && \
    cd untrunc && \
    make FF_VER=shared && \
    strip untrunc && \
	cp /untrunc/untrunc /usr/bin

# Install Flask
# Ensure shared folder exists in the container
RUN mkdir -p /app/shared/uploads /app/shared/fixed

# Set environment variables
ENV UPLOAD_FOLDER=/app/shared/uploads
ENV FIXED_FOLDER=/app/shared/fixed


# Copy the web app code
COPY webapp /webapp
# COPY templates /app/templates
# COPY static /app/static

WORKDIR /webapp

RUN pip install -r requirements.txt

# Expose the port the app runs on
EXPOSE 5001

# Set the entry point to run the web app
CMD ["python3", "app.py"]
