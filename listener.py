import json
from flask import Flask, jsonify, request
from waitress import serve
from kubernetes import client, config


def listPods():
    # config.load_incluster_config()
    config.load_kube_config(config_file="./kubeconfig")

    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        # print("%s\t%s\t%s\t%s" %
              # (i.status.pod_ip, i.metadata.namespace, i.metadata.name, i.spec))
        print(i)

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.get_json()

        if data is None:
            data = json.loads(request.get_data())

        print(data)

        try:
            environment = data['push_data']['tag']
            repo = data['repository']['repo_name']
        except Exception as e:
            print('error, could not deploy', e)
            return jsonify(success=False), 500


    if request.method == 'GET':
        return "i am listening!"

if __name__ == "__main__":
    listPods()
    serve(app, host='0.0.0.0', port=3000)
