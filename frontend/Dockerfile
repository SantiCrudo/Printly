FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 4050 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "4050"]

