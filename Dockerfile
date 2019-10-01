FROM python:3
#COPY qemu-arm-static /usr/bin/qemu-arm


WORKDIR /usr/local/bin
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.16.0/bin/linux/arm/kubectl
RUN chmod +x ./kubectl

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
#CMD [ "/usr/bin/qemu-arm", "/usr/bin/python", "./listener.py" ]
CMD [ "python", "./listener.py" ]
