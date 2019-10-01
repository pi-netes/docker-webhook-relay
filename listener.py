import json
import os
from flask import Flask, jsonify, request
from waitress import serve
from kubernetes import client, config


config.load_incluster_config()
# config.load_kube_config(config_file="./kubeconfig")
v1 = client.CoreV1Api()
def getMatchingDeployments(image):
    ret = v1.list_pod_for_all_namespaces(watch=False)
    return [ i for i in ret.items if i.spec.containers[0].image == image], [i.metadata.labels["app"] for i in ret.items if i.spec.containers[0].image == image]

def rolloutRestart(i):
    # command = 'kubectl --kubeconfig ./kubeconfig rollout restart deployment/' + i.metadata.labels["app"] + ' -n ' + i.metadata.namespace
    command = 'kubectl rollout restart deployment/' + i.metadata.labels["app"] + ' -n ' + i.metadata.namespace
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
        deploymentsToRollout, res = getMatchingDeployments(image)

        for deployment in deploymentsToRollout:
            rolloutRestart(deployment)

        return jsonify(res)
        # return "restarting pods"


    if request.method == 'GET':
        return "i am listening!"

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=3000)
