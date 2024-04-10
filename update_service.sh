export API_DOMAIN=$1.wps.met.no
export UI_DOMAIN=$2.wps.met.no
docker stack rm $1
sleep 15
export NODE_ID=$(docker info -f '{{.Swarm.NodeID}}')
docker node update --label-add $1.$1-data=true $NODE_ID
sleep 5
docker stack deploy -c $1.yml $1

