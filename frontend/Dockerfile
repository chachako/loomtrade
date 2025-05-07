# Stage 1: Build the application
# Use an official Node.js LTS version as a parent image
FROM node:20-alpine AS builder

# Set the Node.js environment to production for the build stage
# This ensures Next.js optimizes the build for production
ENV NODE_ENV=production

# Set the working directory in the container
WORKDIR /app

# Copy package.json and yarn.lock (or package-lock.json)
# The build context in docker-compose.yml is ./frontend,
# so these paths are relative to the frontend/ directory.
COPY package.json yarn.lock ./

# Install project dependencies
# Using --frozen-lockfile ensures that the exact versions specified in yarn.lock are used.
# We install all dependencies (including devDependencies) as they might be needed for the build process.
RUN yarn install --frozen-lockfile

# Copy the rest of the application code into the container
COPY . .

# (Optional) If your application requires build-time environment variables (e.g., NEXT_PUBLIC_API_URL),
# you can define them here using ARG and ENV.
# Example:
# ARG NEXT_PUBLIC_API_BASE_URL
# ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}
# These would typically be passed during the docker build command or from docker-compose.yml.

# Build the Next.js application
# This command (e.g., `next build`) compiles the application for production.
RUN yarn build

# Stage 2: Production image
# Use a slim Node.js LTS image for the production environment
FROM node:20-alpine AS runner

# Set the working directory in the container
WORKDIR /app

# Set the Node.js environment to production for the runtime stage
ENV NODE_ENV=production

# (Optional) If your application requires runtime environment variables that were also build arguments,
# ensure they are also available in the runner stage.
# Example:
# ARG NEXT_PUBLIC_API_BASE_URL
# ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}

# Copy necessary artifacts from the builder stage for Next.js standalone output
# This includes the .next/standalone directory, the .next/static directory, and the public directory.
# The standalone output is optimized for production deployment and includes only necessary files.
COPY --from=builder /app/public ./public
COPY --from=builder --chown=node:node /app/.next/standalone ./
COPY --from=builder --chown=node:node /app/.next/static ./.next/static

# Expose the port the Next.js application runs on (default is 3000)
EXPOSE 3000

# Set the default command to start the Next.js application in production mode.
# For Next.js standalone output, this is typically `node server.js`.
# The `server.js` file is part of the standalone output.
# Consider creating and using a non-root user for better security in production.
# Example for creating a non-root user (uncomment and adapt if needed):
# RUN addgroup --system --gid 1001 nodejs
# RUN adduser --system --uid 1001 nextjs
# USER nextjs
# For simplicity, this Dockerfile runs as root by default.
# Ensure your `package.json` scripts or Next.js configuration correctly handles port binding (usually 0.0.0.0 for containers).
CMD ["node", "server.js"]