FROM registry.fedoraproject.org/fedora:latest

ENV PATH="/root/.local/bin:${PATH}" \
    PYTHONUNBUFFERED="1" \
    GOTOOLCHAIN="auto" \
    GOSUMDB="sum.golang.org"

RUN dnf -y upgrade && \
    dnf -y install python3 python3-pip git curl golang && \
    GOBIN=/usr/local/bin go install github.com/charmbracelet/crush@latest && \
    dnf clean all && rm -rf /var/cache/dnf && rm -rf /root/go/pkg/mod

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR /workspace

COPY requirements.txt requirements-dev.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "/workspace/victoria_entrypoint.py"]
