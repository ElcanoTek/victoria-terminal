FROM registry.fedoraproject.org/fedora:latest

ENV PATH="/root/.local/bin:${PATH}" \
    PYTHONUNBUFFERED="1" \
    GOTOOLCHAIN="auto" \
    GOSUMDB="sum.golang.org" \
    PIP_ROOT_USER_ACTION="ignore" \
    VICTORIA_HOME="/workspace/Victoria"

RUN dnf -y upgrade && \
    dnf -y install python3 python3-pip git curl golang helix uv shadow-utils && \
    GOBIN=/usr/local/bin go install github.com/charmbracelet/crush@latest && \
    dnf clean all && rm -rf /var/cache/dnf && rm -rf /root/go/pkg/mod

WORKDIR /workspace

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

RUN install -Dm755 container_entrypoint.sh /usr/local/bin/container-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/container-entrypoint.sh"]
CMD ["python3", "/workspace/victoria_terminal.py"]
