# Use the official Node.js image as the base image for building
FROM node:14-alpine as build

# Set the working directory inside the container
WORKDIR /app

# Copy the package.json and package-lock.json files into the container
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy the entire frontend directory into the container
COPY . .

# Expose port 3000 to the outside world (this port is used by React development server)
EXPOSE 3000

# Command to start the React development server
CMD ["npm", "start"]
