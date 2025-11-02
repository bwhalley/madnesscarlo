FROM node:18

WORKDIR /app

# Copy package files only
COPY package.json ./

# Clean npm cache and install dependencies fresh
# This ensures platform-specific binaries are built for Linux
RUN npm cache clean --force && \
    rm -rf node_modules package-lock.json && \
    npm install

# Copy application code (excluding node_modules via .dockerignore)
COPY . .

EXPOSE 5173

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

