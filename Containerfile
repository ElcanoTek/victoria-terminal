FROM registry.fedoraproject.org/fedora:latest AS builder

# Install Go and build Crush from source. Fedora currently packages Go 1.24, so
# we pin the toolchain download to Go 1.25 in order to satisfy Crush's minimum
# version requirement.
RUN dnf -y install golang && \
    dnf clean all && \
    GOTOOLCHAIN=go1.25.2 go install github.com/charmbracelet/crush@latest

# Final stage - without Go compiler
FROM registry.fedoraproject.org/fedora:latest

ENV PATH="/root/.local/bin:${PATH}" \
    PYTHONUNBUFFERED="1" \
    PIP_ROOT_USER_ACTION="ignore" \
    VICTORIA_HOME="/workspace/Victoria"

# Copy crush binary from builder
COPY --from=builder /root/go/bin/crush /usr/local/bin/crush

# Install runtime dependencies
RUN dnf -y upgrade && \
    dnf -y install python3 python3-pip git curl helix && \
    dnf clean all && rm -rf /var/cache/dnf && rm -rf /root/go/pkg/mod

WORKDIR /workspace

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

RUN install -Dm755 container_entrypoint.sh /usr/local/bin/container-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/container-entrypoint.sh"]
CMD ["python3", "/workspace/victoria_terminal.py"]
