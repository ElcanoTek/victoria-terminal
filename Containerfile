FROM registry.fedoraproject.org/fedora:latest

ENV PATH="/root/.local/bin:${PATH}" \
    PYTHONUNBUFFERED="1" \
    GOTOOLCHAIN="auto" \
    GOSUMDB="sum.golang.org"

RUN dnf -y upgrade && \
    dnf -y install python3 python3-pip git curl golang helix uv && \
    GOBIN=/usr/local/bin go install github.com/charmbracelet/crush@latest && \
    dnf clean all && rm -rf /var/cache/dnf && rm -rf /root/go/pkg/mod

WORKDIR /workspace

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /root/.local/share/crush \
    && cp configs/crush/crush.local.json /root/.local/share/crush/crush.json

CMD ["python3", "/workspace/victoria_terminal.py"]
