# First, specify the base Docker image.
# You can also use any other image from Docker Hub.
FROM scrapely/actor-python:3.14-latest
USER root


# Second, copy just requirements.txt into the Actor image,
# since it should be the only file that affects the dependency installation in the next step,
# in order to speed up the build.
COPY --chown=myuser:myuser requirements.txt ./

# Install the packages specified in requirements.txt,
# print the installed Python version, pip version,
# and all installed packages with their versions for debugging.
RUN echo "Python version:" \
 && python --version \
 && echo "Pip version:" \
 && pip --version \
 && echo "Installing dependencies:" \
 && pip install -r requirements.txt \
 && echo "All installed Python packages:" \
 && pip freeze

# Install the wrapped stdio MCP server into its own isolated environment with uv, so that its
# dependencies (e.g. a different `mcp` version) cannot conflict with the proxy's dependencies.
# The `arxiv-mcp-server` executable is placed on PATH (/usr/local/bin).
# Replace it with the MCP server you want to wrap, and update the `mcpServerCommand` input default.
RUN UV_TOOL_DIR=/opt/mcp-servers UV_TOOL_BIN_DIR=/usr/local/bin UV_PYTHON_DOWNLOADS=never \
    uv tool install "arxiv-mcp-server >= 0.8.0, < 1.0.0"

# Next, copy the remaining files and directories with the source code.
# Since we do this after installing the dependencies, quick builds will be really fast
# for most source file changes.
COPY --chown=myuser:myuser . ./

# Use compileall to ensure the runnability of the Actor Python code.
RUN python -m compileall -q my_actor/

# Specify how to launch the source code of your Actor.

RUN \
    python -m pip install --upgrade --upgrade-strategy only-if-needed "crawlee>=1.8.0,<2.0.0"; \
    python -c "from importlib.metadata import version; import scrapely; from crawlee.request_loaders import SitemapRequestLoader; print('Scrapely runtime OK with Crawlee', version('crawlee'))"; \
    python -m pip check
RUN chown -R myuser:myuser /usr/src/app /usr/local/lib/python*/site-packages

USER myuser
CMD ["python", "-m", "my_actor"]
