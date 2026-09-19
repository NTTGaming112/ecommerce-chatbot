# Use Node image
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Build the Vite app
RUN npm run build

# Install serve to serve static files
RUN npm install -g serve

# Expose port
EXPOSE 80

# Command to run the app
CMD ["serve", "-s", "dist", "-l", "80"]
