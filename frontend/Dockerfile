# Use an official Node runtime as the base image
FROM node:18-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and yarn.lock
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install

# Copy the rest of the application code
COPY . .

# Make sure react-scripts is in PATH
ENV PATH /app/node_modules/.bin:$PATH

# Add more verbose output
RUN echo "Node version:" && node --version && \
    echo "Yarn version:" && yarn --version && \
    echo "React version:" && yarn list react && \
    echo "React DOM version:" && yarn list react-dom

# Build the app
RUN yarn build

# Remove Search.js from the build
RUN rm -f build/static/js/*Search*.js build/static/css/*Search*.css

# Install serve to run the application
RUN yarn global add serve

# Expose port 3000
EXPOSE 3000

# Start the application
CMD ["serve", "-s", "build", "-l", "3000"]
