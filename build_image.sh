#!/usr/bin/env bash
# just build the updated docker image
ALL_ARCHS="amd64 arm64 armv7 armv6"

function usage {
    cat <<EOF
Usage: $0 [publish|publish-all|{blank}]
    publish: build and publish the image for the current architecture
    publish-all: build and publish the image for all architectures
    blank: build the image for the current architecture
EOF
}

if [[ -z $1 ]]; then
  echo "BUILD is TEST MODE"
  echo "ARCH: $(uname -m)"
elif [[ $1 == "publish" ]]; then
  echo "BUILD is PUBLISH MODE"
  echo "ARCH: $(uname -m)"
  export ARCH_MODE_PUBLISH=1
elif [[ $1 == "publish-all" ]]; then
    echo "BUILD is PUBLISH ALL MODE"
    echo "ARCH: ${ALL_ARCHS}"
    export ARCH_MODE_ALL=0
else
    echo "Unknown build mode: $1"
    usage
    exit 1
fi 

# activate venv
if ! [ -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "New virtual environment [venv] activated."
else
    source venv/bin/activate
    echo "Existing virtual environment [venv] activated."
fi

DATE=$(date +%Y%m%d%H%M%S)
DOCKER_USER="pwhite00"
IMAGE_NAME="read_me_later"

# build the image
docker build -t $IMAGE_NAME:$DATE .

if [[ $ARCH_MODE_ALL == 1 ]] ; then
    for arch in ${ALL_ARCHS}; do
        echo "Building for $arch"
        docker build --build-arg ARCH=$arch -t $DOCKER_USER/$IMAGE_NAME:$DATE-$arch .
        if [[ $1 == "publish-all" ]]; then
            echo "Publishing for $arch"
            docker push $DOCKER_USER/$IMAGE_NAME:$DATE-$arch
        fi
    done

else
    echo "Building for $(uname -m)"
    docker build --build-arg ARCH=$(uname -m) -t $DOCKER_USER/$IMAGE_NAME:$DATE-$(uname -m) .
    if [[ $1 == "publish" ]]; then
        echo "Publishing for $(uname -m)"
        docker push $DOCKER_USER/$IMAGE_NAME:$DATE-$(uname -m)
    fi
fi

echo "Done."