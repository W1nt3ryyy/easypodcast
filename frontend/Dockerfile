# Stage 1: Build the React app
FROM node:20 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve the app with Apache
FROM httpd:alpine
# Copy built files
COPY --from=build /app/dist/ /usr/local/apache2/htdocs/

# Enable required modules
RUN sed -i \
    -e '/LoadModule proxy_module/s/^#//g' \
    -e '/LoadModule proxy_http_module/s/^#//g' \
    -e '/LoadModule rewrite_module/s/^#//g' \
    /usr/local/apache2/conf/httpd.conf

# Add custom config
COPY my-proxy.conf /usr/local/apache2/conf/extra/my-proxy.conf
RUN echo "Include conf/extra/my-proxy.conf" >> /usr/local/apache2/conf/httpd.conf

