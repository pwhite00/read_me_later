#!/usr/bin/env bash
set -euo pipefail

# Configuration
DOCKER_USER="pwhite00"
IMAGE_NAME="read_me_later"
ALL_ARCHS="linux/amd64 linux/arm64 linux/arm/v7"

function usage {
    cat <<EOF
Usage: $0 [publish|publish-all|build|{blank}]
    build: build the image for the current architecture (default)
    publish: build and publish the image for the current architecture
    publish-all: build and publish the image for all architectures
    blank: same as build

Examples:
    $0                    # Build for current arch
    $0 build             # Build for current arch
    $0 publish           # Build and publish for current arch
    $0 publish-all       # Build and publish for all architectures
EOF
}

function get_current_arch() {
    case $(uname -m) in
        x86_64) echo "linux/amd64" ;;
        aarch64|arm64) echo "linux/arm64" ;;
        armv7l) echo "linux/arm/v7" ;;
        *) echo "linux/amd64" ;; # fallback
    esac
}

function check_docker_auth() {
    echo "Docker Hub authentication check skipped (you're already logged in)"
}

function build_single_arch() {
    local arch=$1
    local tag_suffix=$2
    local publish_mode=$3
    local date_tag=$(date +%Y%m%d%H%M%S)
    
    echo "Building for $arch..."
    docker build --platform $arch -t $IMAGE_NAME:$date_tag$tag_suffix .
    
    if [[ "$publish_mode" == "publish" || "$publish_mode" == "publish-all" ]]; then
        echo "Tagging for Docker Hub..."
        docker tag $IMAGE_NAME:$date_tag$tag_suffix $DOCKER_USER/$IMAGE_NAME:$date_tag$tag_suffix
        docker tag $IMAGE_NAME:$date_tag$tag_suffix $DOCKER_USER/$IMAGE_NAME:latest$tag_suffix
        
        echo "Publishing to Docker Hub..."
        docker push $DOCKER_USER/$IMAGE_NAME:$date_tag$tag_suffix
        docker push $DOCKER_USER/$IMAGE_NAME:latest$tag_suffix
    fi
}

# Parse arguments
case "${1:-build}" in
    "publish")
        echo "BUILD is PUBLISH MODE"
        echo "ARCH: $(get_current_arch)"
        check_docker_auth
        build_single_arch "$(get_current_arch)" "" "publish"
        ;;
    "publish-all")
        echo "BUILD is PUBLISH ALL MODE"
        echo "ARCHES: ${ALL_ARCHS}"
        check_docker_auth
        for arch in $ALL_ARCHS; do
            arch_suffix=$(echo $arch | sed 's|linux/||' | sed 's|/|_|g')
            build_single_arch "$arch" "-$arch_suffix" "publish-all"
        done
        ;;
    "build"|"")
        echo "BUILD is TEST MODE"
        echo "ARCH: $(get_current_arch)"
        build_single_arch "$(get_current_arch)" "" "build"
        ;;
    *)
        echo "Unknown build mode: $1"
        usage
        exit 1
        ;;
esac

echo "Build completed successfully!"