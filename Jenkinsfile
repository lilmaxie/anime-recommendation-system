pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = 'omega-branch-483602-k3'
        // Đã xóa các biến GCLOUD_PATH thừa vì ta đã cài vào hệ thống ở Bước 2
    }

    stages{
        stage("Cloning from Github..."){
            steps{
                script{
                    echo 'Cloning from Github...'
                    // Lưu ý: Đảm bảo Credentials ID 'github-token' đã tạo trên Jenkins
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/lilmaxie/anime-recommendation-system.git']])
                }
            }
        }

        stage("Making a virtual environment..."){
            steps{
                script{
                    echo 'Making a virtual environment...'
                    sh '''
                    # Kiểm tra nếu venv chưa có thì mới tạo để tiết kiệm thời gian
                    if [ ! -d "${VENV_DIR}" ]; then
                        python3 -m venv ${VENV_DIR}
                    fi
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    pip install dvc
                    '''
                }
            }
        }

        stage('DVC Pull'){
            steps{
                // Lưu ý: Đảm bảo Credentials ID 'gcp-key' (file json) đã upload lên Jenkins
                withCredentials([file(credentialsId:'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script{
                        echo 'DVC Pull...'
                        sh '''
                        . ${VENV_DIR}/bin/activate
                        # Thêm --force để ghi đè dữ liệu cũ
                        dvc pull --force
                        '''
                    }
                }
            }
        }

        stage('Build and Push Image to GCR'){
            steps{
                withCredentials([file(credentialsId:'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script{
                        echo 'Build and Push Image to GCR'
                        sh '''
                        # Không cần export PATH nữa
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        gcloud auth configure-docker --quiet
                        docker build -t gcr.io/${GCP_PROJECT}/ml-project:latest .
                        docker push gcr.io/${GCP_PROJECT}/ml-project:latest
                        '''
                    }
                }
            }
        }

        stage('Deploying to Kubernetes'){
            steps{
                withCredentials([file(credentialsId:'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS' )]){
                    script{
                        echo 'Deploying to Kubernetes'
                        sh '''
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        gcloud container clusters get-credentials ml-app-cluster --region asia-east1
                        kubectl apply -f deployment.yaml
                        '''
                    }
                }
            }
        }
    }
}