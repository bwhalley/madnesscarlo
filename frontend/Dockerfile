FROM node:18-slim

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
# Use --force to ensure platform-specific binaries are installed correctly
RUN npm install --force

# Copy application code (but not node_modules from host)
COPY . .

EXPOSE 5173

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

