#!/bin/bash

cd ~/gp_red_teaming_llms/GP_CTRL_plus_12
podman-compose -f docker-compose.deployment.yml pull
podman-compose -f docker-compose.deployment.yml up -d