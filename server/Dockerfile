FROM node:12

# Create app directory

WORKDIR /usr/src/app

# Install app dependencies

COPY /server/package*.json ./

RUN npm install

# If you are building your code for production

RUN npm ci --only=production

# Bundle app source

COPY . .

EXPOSE 80

CMD [ "node", "server.js" ]