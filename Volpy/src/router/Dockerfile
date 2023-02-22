FROM crossbario/crossbar:pypy-slim-amd64

USER root
COPY . /mynode/

ENTRYPOINT ["crossbar", "start", "--cbdir", "/mynode/.crossbar"]

# sudo docker build -t router -f Dockerfile .
# sudo docker run --rm -it -p 8080:8080 router
