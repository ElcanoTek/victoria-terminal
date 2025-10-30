FROM registry.fedoraproject.org/fedora:latest AS builder

ENV PATH="/root/.local/bin:${PATH}" \
    PYTHONUNBUFFERED="1" \
    GOTOOLCHAIN="auto" \
    GOSUMDB="sum.golang.org" \
    PIP_ROOT_USER_ACTION="ignore" \
    PIP_BREAK_SYSTEM_PACKAGES="1"

RUN dnf -y upgrade && \
    dnf -y install python3 python3-pip git curl golang helix \
        gcc gcc-c++ make cmake ninja-build pkgconf-pkg-config \
        python3-devel libffi-devel openssl-devel && \
    # Change @latest to a pinned version if we ever need to lock Crush.
    GOBIN=/usr/local/bin go install github.com/charmbracelet/crush@latest && \
    dnf clean all && rm -rf /var/cache/dnf && rm -rf /root/go/pkg/mod

WORKDIR /workspace

COPY requirements.txt ./
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Final stage - without Go compiler
FROM registry.fedoraproject.org/fedora:latest

ENV PATH="/root/.local/bin:${PATH}" \
    PYTHONUNBUFFERED="1" \
    PIP_ROOT_USER_ACTION="ignore" \
    PIP_BREAK_SYSTEM_PACKAGES="1" \
    VICTORIA_HOME="/workspace/Victoria"

# Install runtime dependencies
RUN dnf -y upgrade && \
    dnf -y install python3 python3-pip git curl helix \
        libffi openssl && \
    dnf clean all && rm -rf /var/cache/dnf && rm -rf /root/go/pkg/mod

# Reuse compiled tooling and Python packages from builder stage
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /usr/local/lib/python*/site-packages /usr/local/lib/

WORKDIR /workspace

COPY . .

RUN install -Dm755 container_entrypoint.sh /usr/local/bin/container-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/container-entrypoint.sh"]
CMD ["python3", "/workspace/victoria_terminal.py"]
