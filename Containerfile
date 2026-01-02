FROM registry.fedoraproject.org/fedora:latest

ENV VICTORIA_HOME="/workspace/Victoria" \
    PYTHONUNBUFFERED="1" \
    PIP_ROOT_USER_ACTION="ignore" \
    GOTOOLCHAIN="auto" \
    GOSUMDB="sum.golang.org"

# Install runtime and build dependencies plus crush
RUN dnf -y upgrade && \
    dnf -y install \
        python3 \
        python3-pip \
        python3-devel \
        git \
        curl \
        helix \
        golang \
        gcc \
        gcc-c++ \
        make \
        cmake \
        libffi-devel \
        openssl-devel \
        redhat-rpm-config \
        nodejs \
        npm && \
    # Change @latest to a pinned version if we ever need to lock Crush.
    GOBIN=/usr/local/bin go install github.com/charmbracelet/crush@latest && \
    dnf clean all && rm -rf /var/cache/dnf && rm -rf /root/go/pkg/mod

WORKDIR /workspace

# Python packages (unpinned for rolling updates)
RUN pip3 install --no-cache-dir \
    altair \
    black \
    boto3 \
    duckdb \
    email-validator \
    flake8 \
    httpx \
    ipykernel \
    isort \
    matplotlib \
    mcp[cli] \
    mcp-server-motherduck \
    nox \
    numpy \
    openpyxl \
    pandas \
    plotly \
    polars \
    pyarrow \
    pylsp-mypy \
    pytest \
    pytest-cov \
    pytest-timeout \
    python-dotenv \
    python-lsp-ruff \
    python-lsp-server \
    requests \
    rich \
    scikit-learn \
    scipy \
    seaborn \
    sendgrid \
    snowflake-labs-mcp \
    sqlalchemy \
    statsmodels \
    xlsxwriter

# Node.js MCP servers
RUN npm install -g @browserbasehq/mcp-server-browserbase

COPY . .

RUN install -Dm755 entrypoint.sh /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
