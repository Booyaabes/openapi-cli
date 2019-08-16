FROM python:3.7.4-buster

RUN useradd -ms /bin/bash user

WORKDIR /root

RUN wget https://raw.githubusercontent.com/swagger-api/swagger-codegen/4607a90d7b69463a0ae8fc94fac68fc95d80965e/modules/swagger-codegen/src/main/resources/python/requirements.mustache -O requirements.txt && \
    echo "argcomplete >= 1.10.0" >> requirements.txt && \
    pip install -r requirements.txt && rm -f requirements.txt && \
    mkdir /home/user/.bash_completion.d && \
    activate-global-python-argcomplete --dest=/home/user/.bash_completion.d/ && \
    echo "source ~/.bash_completion.d/python-argcomplete.sh" >> /home/user/.bashrc

USER user

WORKDIR /app

ENV PYTHONPATH=/app

ADD open-api-cli.py /usr/local/bin/.

ENTRYPOINT ["/bin/bash"]