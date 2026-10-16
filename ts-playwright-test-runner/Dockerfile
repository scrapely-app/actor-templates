FROM scrapely/actor-node-playwright:24-1.61.1-latest

COPY --chown=myuser:myuser package*.json Dockerfile ./

# Install NPM packages, skip optional and development dependencies to
# keep the image small. Avoid logging too much and print the dependency
# tree for debugging
RUN npm --quiet set progress=false \
    && npm install --omit=dev --omit=optional \
    && echo "Installed NPM packages:" \
    && (npm list --omit=dev --all || true) \
    && echo "Node.js version:" \
    && node --version \
    && echo "NPM version:" \
    && npm --version \
    && rm -r ~/.npm

# Next, copy the remaining files and directories with the source code.
# Since we do this after NPM install, quick build will be really fast
# for most source file changes.
COPY --chown=myuser:myuser . ./

# Compile the TypeScript sources (TypeScript is installed as a regular dependency).
RUN npm run build

# Run the image.
CMD ["node", "dist/src/main.js"]
