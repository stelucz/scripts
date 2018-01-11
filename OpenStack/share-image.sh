#!/bin/bash
####
#
# Script for image sharing in OpenStack
#
# Lukas Stehlik 2017
#
# usage: share-images <project-UUID>
#
####

# images to share
images=( adb486ef-6bc4-47d3-b0a9-27b9aab5900f
  8fd41391-2d25-4d53-89ef-f47d953e619e
  a763181a-0ce0-47fe-8546-8b1cbf277e90
  d33708bc-b211-45c6-8a46-3754a87c6c26
  832d37df-e49f-42cc-8f44-fa7d9261b3dc )

if [ -n "$1" ]; then
for (( i = 0; i < ${#images[@]}; i++ )); do

  echo "Image $(($i+1)) / ${#images[@]}"
  glance member-create ${images[i]} $1
  glance member-update ${images[i]} $1 accepted

done
else
  echo "No project UUID supplied. Nothing done."
  echo "Usage: share-images <project-UUID>"
fi
