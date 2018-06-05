#!/usr/bin/env bash

if [ -z "$REPO_NAME" ]; then
	REPO_NAME=inasafe
fi

if [ -z "$IMAGE_NAME" ]; then
	IMAGE_NAME=headless_processor
fi

if [ -z "$TAG_NAME" ]; then
	TAG_NAME=latest
fi

if [ -z "$BUILD_ARGS" ]; then
	BUILD_ARGS="--pull --no-cache"
fi

# Build Args Environment

if [ -z "$INASAFE_CORE_TAG" ]; then
	INASAFE_CORE_TAG=version-4_4_0
fi

if [ -z "$INASAFE_HEADLESS_TAG" ]; then
	INASAFE_HEADLESS_TAG=develop
fi

echo "INASAFE_CORE_TAG=${INASAFE_CORE_TAG}"
echo "INASAFE_HEADLESS_TAG=${INASAFE_HEADLESS_TAG}"

echo "Build: $REPO_NAME/$IMAGE_NAME:$TAG_NAME"
echo "Build Args: $BUILD_ARGS"

docker build -t ${REPO_NAME}/${IMAGE_NAME} \
	--build-arg INASAFE_CORE_TAG=${INASAFE_CORE_TAG} \
	--build-arg INASAFE_HEADLESS_TAG=${INASAFE_HEADLESS_TAG} \
	${BUILD_ARGS} . && \
docker tag ${REPO_NAME}/${IMAGE_NAME} ${REPO_NAME}/${IMAGE_NAME}:${TAG_NAME} && \
docker push ${REPO_NAME}/${IMAGE_NAME}:${TAG_NAME}
