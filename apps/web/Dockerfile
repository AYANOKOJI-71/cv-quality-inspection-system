FROM node:22-alpine
WORKDIR /app
COPY apps/web/package.json ./package.json
RUN npx --yes pnpm@10.6.3 install --frozen-lockfile=false
COPY apps/web ./
EXPOSE 5188
CMD ["npx", "--yes", "pnpm@10.6.3", "dev", "--host", "0.0.0.0", "--port", "5188"]
