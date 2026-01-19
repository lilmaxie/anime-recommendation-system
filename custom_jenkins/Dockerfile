# Use the Jenkins image as the base image
FROM jenkins/jenkins:lts

# Switch to root user to install dependencies
USER root

# Install prerequisites and Docker
# Thay đổi:
# 1. Xóa 'software-properties-common' (gây lỗi và không thực sự cần thiết khi ta echo repo thủ công).
# 2. Thêm 'lsb-release' để tự động lấy tên mã Debian (bookworm/bullseye) thay vì hardcode.
# 3. Sử dụng thư mục '/usr/share/keyrings' thay vì 'apt-key' (đã lỗi thời).
RUN apt-get update -y && \
    apt-get install -y lsb-release apt-transport-https ca-certificates curl gnupg && \
    mkdir -p /usr/share/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update -y && \
    apt-get install -y docker-ce docker-ce-cli containerd.io && \
    apt-get clean

# Add Jenkins user to the Docker group
RUN groupadd -f docker && \
    usermod -aG docker jenkins

# Create the Docker directory and volume for DinD
RUN mkdir -p /var/lib/docker
VOLUME /var/lib/docker

# Switch back to the Jenkins user
USER jenkins