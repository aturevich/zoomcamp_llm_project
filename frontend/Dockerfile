# Use an official Node runtime as the base image
FROM node:18-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and yarn.lock
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy the rest of the application code, including node_modules
COPY . .

# Make sure react-scripts is in PATH
ENV PATH /app/node_modules/.bin:$PATH

# Build the application
RUN yarn build

# Expose port 3000
EXPOSE 3000

# Start the application using a production-ready server
CMD ["yarn", "start"]
