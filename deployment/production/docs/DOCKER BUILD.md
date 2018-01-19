# General How To Use for production Build Scripts

For each production image, there are several environment variable that can be
used to customize the build script

- REPO_NAME: Target repo name of the image
- IMAGE_NAME: The docker image name
- TAG_NAME: Specific tag of the docker image. Will default to latest
- BUILD_ARGS: Additional docker build params

You can create source script for your build. For example like this

```
#!/usr/bin/env bash
export REPO_NAME=yourreponame
export IMAGE_NAME=yourimagename
export TAG_NAME=yourtag
```

You can name it as `init-script.sh` and source this script before executing
the build.

```
# <from the build.sh directory>
# change init-script.sh to a name that you actually use
source init-script.sh
./build.sh
```

There are also additional environment needed by the build possible. Look at
the content of the build script to make sure.
