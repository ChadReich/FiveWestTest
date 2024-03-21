# Use the official Node.js image as the base image for building
FROM node:14-alpine as build

# Set the working directory inside the container
WORKDIR /app

# Copy the package.json and package-lock.json files into the container
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy only the necessary files into the container
COPY src ./src
COPY public ./public

# Build the React JS app
RUN npm run build

# Use the official Nginx image as the base image for serving the static files
FROM nginx:alpine

# Copy the build output from the previous stage into the nginx container
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 3000 to the outside world (this port is used by React development server)
EXPOSE 3000

# Command to run Nginx
CMD ["nginx", "-g", "daemon off;"]
