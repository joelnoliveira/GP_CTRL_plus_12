FROM node:22-bookworm-slim

ARG USER_NAME="not-admin"

ENV USER_NAME $USER_NAME
WORKDIR /react-app

# Instalar dependências do sistema para Playwright
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# add non root user
RUN adduser --disabled-password --gecos "" $USER_NAME

COPY react-app .
RUN npm install

# Instalar Playwright e browsers
RUN npx playwright install chromium

# RUN chown -R $USER_NAME /react-app

# Switch to non-root
USER $USER_NAME


CMD ["npm", "start"] #TODO: npm start not recommended for deployment
