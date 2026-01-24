FROM node:22-bookworm-slim

ARG USER_NAME="not-admin"

ENV USER_NAME $USER_NAME
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
WORKDIR /react-app

# add non root user
RUN adduser --disabled-password --gecos "" $USER_NAME

COPY react-app .
RUN npm ci

# Instalar Playwright, browsers e dependências do sistema
RUN npx playwright install --with-deps

RUN chown -R $USER_NAME /react-app /ms-playwright

# Switch to non-root
USER $USER_NAME


CMD ["npm", "start"] #TODO: npm start not recommended for deployment
