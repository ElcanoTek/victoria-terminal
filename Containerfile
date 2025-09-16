FROM registry.fedoraproject.org/fedora:latest

ENV PATH="/root/.local/bin:${PATH}" \
    PYTHONUNBUFFERED="1"

RUN dnf -y upgrade && \
    dnf -y install python3 python3-pip git curl && \
    printf "[charm]\nname=Charm\nbaseurl=https://repo.charm.sh/yum/\nenabled=1\ngpgcheck=1\ngpgkey=https://repo.charm.sh/yum/gpg.key\n" > /etc/yum.repos.d/charm.repo && \
    dnf -y install crush && \
    dnf clean all && rm -rf /var/cache/dnf

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR /workspace

COPY requirements.txt requirements-dev.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "/workspace/victoria_entrypoint.py"]
