# ---- Builder Stage ----
# This stage installs build tools and compiles the crush binary.
FROM registry.fedoraproject.org/fedora:latest as builder

# Set environment variables for the build
ENV GOTOOLCHAIN="auto" \
    GOSUMDB="sum.golang.org"

# Install build-time dependencies and the crush binary
RUN dnf -y upgrade && \
    dnf -y install golang && \
    GOBIN=/usr/local/bin go install github.com/charmbracelet/crush@latest && \
    dnf clean all && rm -rf /var/cache/dnf && rm -rf /root/go/pkg/mod

# ---- Runtime Stage ----
# This is the final, smaller image with only runtime dependencies.
FROM registry.fedoraproject.org/fedora:latest

# Set environment variables for runtime
ENV PATH="/app/victoria/.local/bin:${PATH}" \
    PYTHONUNBUFFERED="1"

# Create a non-root user and group for security
RUN groupadd --gid 1001 victoria && \
    useradd --uid 1001 --gid 1001 --shell /bin/bash --create-home victoria

# Install only runtime dependencies
RUN dnf -y upgrade && \
    dnf -y install python3 python3-pip git curl helix uv && \
    dnf clean all && rm -rf /var/cache/dnf

# Set up the application directory
WORKDIR /app

# Copy python requirements and install them as the non-root user
COPY --chown=victoria:victoria requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code and other necessary files
COPY --chown=victoria:victoria . .

# Copy the crush binary from the builder stage
COPY --from=builder /usr/local/bin/crush /usr/local/bin/crush

# Create crush config directory and copy config file
RUN mkdir -p /home/victoria/.local/share/crush && \
    cp configs/crush/crush.local.json /home/victoria/.local/share/crush/crush.json && \
    chown -R victoria:victoria /home/victoria/.local && \
    install -o victoria -g victoria -m 755 container_entrypoint.sh /usr/local/bin/container-entrypoint.sh

# Switch to the non-root user
USER victoria

# Set the entrypoint and default command
ENTRYPOINT ["/usr/local/bin/container-entrypoint.sh"]
CMD ["python3", "/app/victoria_terminal.py"]
