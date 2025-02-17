FROM nodered/node-red:latest

# Copy your custom package.json to the /data folder
COPY package.json /data/package.json

# Change to the /data directory and install dependencies
RUN cd /data && npm install

# Expose the default Node-RED port (optional if already exposed in base image)
EXPOSE 1880

CMD ["npm", "start"]
