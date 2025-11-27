FROM node:22-alpine

ARG USER_NAME="not-admin"

ENV USER_NAME $USER_NAME
WORKDIR /react-app

# add non root user
RUN adduser --disabled-password --gecos "" $USER_NAME

COPY react-app .
RUN npm install

# RUN chown -R $USER_NAME /react-app

# Switch to non-root
USER $USER_NAME


CMD ["npm", "start"] #TODO: npm start not recommended for deployment
