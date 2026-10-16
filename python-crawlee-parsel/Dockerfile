# First, specify the base Docker image.
# You can also use any other image from Docker Hub.
FROM scrapely/actor-python:3.14-latest
USER root


# Second, copy just requirements.txt into the Actor image,
# since it should be the only file that affects the dependency install in the next step,
# in order to speed up the build
COPY --chown=myuser:myuser requirements.txt ./

# Install the packages specified in requirements.txt,
# Print the installed Python version, pip version
# and all installed packages with their versions for debugging
RUN echo "Python version:" \
 && python --version \
 && echo "Pip version:" \
 && pip --version \
 && echo "Installing dependencies:" \
 && pip install -r requirements.txt \
 && echo "All installed Python packages:" \
 && pip freeze

# Next, copy the remaining files and directories with the source code.
# Since we do this after installing the dependencies, quick build will be really fast
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
