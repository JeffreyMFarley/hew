FROM alpine

RUN apk add --update python python3 py-pip ca-certificates && \
	apk add --no-cache --virtual=build-dependencies && \
    wget "https://bootstrap.pypa.io/get-pip.py" -O /dev/stdout | python3 && \
    apk del build-dependencies

# Copy over the local directory
ADD . /home/project
WORKDIR /home/project

# Run the tests
CMD ["python3", "setup.py", "test"]