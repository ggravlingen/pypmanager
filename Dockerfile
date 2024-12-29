# docker build . --tag removeme
# docker run -p 8001:8001 removeme
FROM python:3.12-bullseye

# Set timezone
ENV TZ=Europe/Stockholm
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Don't install node dev dependencies
ENV NODE_ENV="production"

# Install node
# Install node dependencies
RUN apt-get update && \
    apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        libgnutls30 && \
        rm -rf /var/cache/apt && \
        apt-get clean && \
        apt-get autoremove

# Add node source
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list

# Install node and yarn
RUN apt-get update && \
    apt-get install -y \
        nodejs \
        supervisor && \
    npm install -g yarn

# Copy code dir
COPY . /code/app

# Install backend dependencies
RUN pip install --upgrade pip wheel \
    && cd /code/app \
    && pip install --no-cache-dir -e .

# Build frontend
RUN cd /code/app/ && \
    ./script/install-frontend.sh

# Copy supervisord config
COPY supervisord/supervisord.conf /etc/supervisor/supervisord.conf
COPY supervisord/01-fastapi.conf /etc/supervisor/conf.d/01-fastapi.conf

WORKDIR /code/app

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD curl -f http://localhost:8001/status || exit 1

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf", "--nodaemon"]
