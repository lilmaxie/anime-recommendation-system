# Sử dụng Jenkins LTS làm nền
FROM jenkins/jenkins:lts

# Chuyển sang quyền root để cài đặt
USER root

# 1. Cài đặt các gói cơ bản và Docker
RUN apt-get update -y && \
    apt-get install -y lsb-release apt-transport-https ca-certificates curl gnupg && \
    mkdir -p /usr/share/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update -y && \
    apt-get install -y docker-ce docker-ce-cli containerd.io

# 2. Cài đặt Google Cloud CLI & Kubectl (Phiên bản mới nhất)
RUN curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee /etc/apt/sources.list.d/google-cloud-sdk.list && \
    apt-get update -y && \
    apt-get install -y google-cloud-cli google-cloud-sdk-gke-gcloud-auth-plugin kubectl && \
    apt-get clean

# 3. Thêm user jenkins vào nhóm docker để có quyền chạy lệnh docker
RUN groupadd -f docker && \
    usermod -aG docker jenkins

# Tạo thư mục Docker volume
RUN mkdir -p /var/lib/docker
VOLUME /var/lib/docker

# Chuyển lại về user jenkins
USER jenkins