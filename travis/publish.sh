#!/bin/bash -ex


version="latest"
if [ ${TRAVIS_BRANCH} != "master" ] ; then
  version=${TRAVIS_BRANCH}
fi

username=$(echo ${TRAVIS_REPO_SLUG}  | sed  "s/\(.*\)\/.*/\1/")
docker login -u="${DOCKER_USERNAME}" -p="${DOCKER_PASSWORD}"

function buildPublish() {
  tag=${username}"/"$1:$version
  docker tag $1 ${tag}
  echo "Pushing tag ${tag}"
  docker push $tag
}

buildPublish "history"
buildPublish "persister"