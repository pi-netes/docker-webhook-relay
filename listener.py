import json
import os
from flask import Flask, jsonify, request
from waitress import serve
from kubernetes import client, config


config.load_incluster_config()
# if developing locally, this might be helpful
# config.load_kube_config(config_file="./kubeconfig")
v1 = client.CoreV1Api()
def getMatchingDeployments(image):
    ret = v1.list_pod_for_all_namespaces(watch=False)
    pods = [ i for i in ret.items if i.spec.containers[0].image == image]
    deployments = [i.metadata.labels["app"] for i in ret.items if i.spec.containers[0].image == image]
    return pods, deployments

def rolloutRestart(pod):
    # command = 'kubectl --kubeconfig ./kubeconfig rollout restart deployment/' + pod.metadata.labels["app"] + ' -n ' + pod.metadata.namespace
    command = 'kubectl rollout restart deployment/' + pod.metadata.labels["app"] + ' -n ' + pod.metadata.namespace
    os.system(command)

def getImageFromWebhook(request):
    data = request.get_json()
    data = json.loads(request.get_data())
    print(data)
    tag = data['push_data']['tag']
    return data['repository']['repo_name'] + ":" + tag

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        image = getImageFromWebhook(request)
        pods, deployments = getMatchingDeployments(image)

        for pod in pods:
            rolloutRestart(pod)

        return jsonify(deployments)
        # return "restarting pods"


    if request.method == 'GET':
        return "i am listening!"

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=3000)
