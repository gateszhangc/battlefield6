FROM node:20-alpine

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000
ENV HOST=0.0.0.0

COPY --chown=node:node assets ./assets
COPY --chown=node:node favicon.ico ./favicon.ico
COPY --chown=node:node index.html ./index.html
COPY --chown=node:node robots.txt ./robots.txt
COPY --chown=node:node script.js ./script.js
COPY --chown=node:node server.js ./server.js
COPY --chown=node:node site.webmanifest ./site.webmanifest
COPY --chown=node:node sitemap.xml ./sitemap.xml
COPY --chown=node:node styles.css ./styles.css

USER node

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/healthz >/dev/null || exit 1

CMD ["node", "server.js"]
