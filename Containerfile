FROM registry.fedoraproject.org/fedora:latest

ARG USERNAME=victoria
ARG USER_UID=1000
ARG USER_GID=${USER_UID}

ENV PATH="/home/${USERNAME}/.local/bin:/root/.local/bin:${PATH}" \
    PYTHONUNBUFFERED="1" \
    GOTOOLCHAIN="auto" \
    GOSUMDB="sum.golang.org"

RUN dnf -y upgrade && \
    dnf -y install python3 python3-pip git curl golang helix uv shadow-utils && \
    GOBIN=/usr/local/bin go install github.com/charmbracelet/crush@latest && \
    dnf clean all && rm -rf /var/cache/dnf && rm -rf /root/go/pkg/mod

WORKDIR /workspace

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

RUN groupadd --gid "${USER_GID}" --non-unique "${USERNAME}" \
    && useradd --uid "${USER_UID}" --gid "${USER_GID}" --create-home --shell /bin/bash --non-unique "${USERNAME}" \
    && mkdir -p /home/${USERNAME}/.local/share/crush \
    && cp configs/crush/crush.local.json /home/${USERNAME}/.local/share/crush/crush.json \
    && chown -R ${USER_UID}:${USER_GID} /home/${USERNAME}/.local \
    && chown -R ${USER_UID}:${USER_GID} /workspace \
    && install -Dm755 container_entrypoint.sh /usr/local/bin/container-entrypoint.sh

USER ${USERNAME}

ENV HOME="/home/${USERNAME}"

ENTRYPOINT ["/usr/local/bin/container-entrypoint.sh"]
CMD ["python3", "/workspace/victoria_terminal.py"]
