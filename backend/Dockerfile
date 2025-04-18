# Use the specified Node.js version
ARG NODE_VERSION=20.10.0
FROM node:${NODE_VERSION}-alpine

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci

# Copy application code
COPY . .

# Expose the application port
EXPOSE 4000

# Start the application
CMD ["npm", "start"] 