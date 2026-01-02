FROM registry.fedoraproject.org/fedora:latest

ENV PATH="/root/.local/bin:${PATH}" \
    PYTHONUNBUFFERED="1" \
    PIP_ROOT_USER_ACTION="ignore" \
    GOTOOLCHAIN="auto" \
    GOSUMDB="sum.golang.org" \
    VICTORIA_HOME="/workspace/Victoria"

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

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY package.json ./
RUN npm install -g $(node -e "console.log(Object.entries(require('./package.json').dependencies).map(([k,v]) => v === '*' ? k : k+'@'+v).join(' '))")

COPY . .

RUN install -Dm755 container_entrypoint.sh /usr/local/bin/container-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/container-entrypoint.sh"]
CMD ["python3", "-m", "configurator"]
