# Python image to use.
FROM python:3.12-slim

# Set the working directory to /app
WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    git \
    libprotobuf-dev \
    libnl-route-3-dev \
    libcap-dev \
    libseccomp-dev \
    pkg-config \
    wget \
    protobuf-compiler \
    unzip \
    python3-dev \
    flex \
    bison \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/google/nsjail.git /opt/nsjail && \
    cd /opt/nsjail && make && \
    ln -s /opt/nsjail/nsjail /usr/local/bin/nsjail

# copy the requirements file used for dependencies
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the rest of the working directory contents into the container at /app
COPY . .

# Run app.py when the container launches
ENTRYPOINT ["python", "app.py"]
