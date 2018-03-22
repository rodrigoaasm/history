#!/bin/bash -ex


version="latest"
if [ ${TRAVIS_BRANCH} != "master" ] ; then
  version=${TRAVIS_BRANCH}
fi

function buildPublish() {
  tag="${1}:${version}"
  docker build -t ${tag} -f docker/${2} .
  docker login -u="${DOCKER_USERNAME}" -p="${DOCKER_PASSWORD}"
  docker push $tag
}

buildPublish "dojot/history" history.docker
buildPublish "dojot/persister" persister.docker
