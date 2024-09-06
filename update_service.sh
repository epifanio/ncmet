#!/bin/bash

# utility script to update a service
# example usage: ./update_service.sh service_name api_domain ui_domain
# service_name needs to match the name of the service in the stack
# which will be updated by loading the service_name.yml file
# api_domain is the domain name for the api service
# ui_domain is the domain name for the ui service
# the script will remove the service, update the node label, and redeploy the service

export SERVICE_NAME=$1
export API_DOMAIN=$2
export UI_DOMAIN=$3
docker stack rm $1
sleep 15
export NODE_ID=$(docker info -f '{{.Swarm.NodeID}}')
docker node update --label-add $1.$1-data=true $NODE_ID
sleep 5
docker stack deploy -c $1.yml $1


