pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = 'omega-branch-483602-k3'
        // Không cần khai báo GCLOUD_PATH vì đã cài vào hệ thống
    }

    stages{
        stage("Cloning from Github..."){
            steps{
                script{
                    echo 'Cloning from Github...'
                    // Nhớ thay URL repo của bạn nếu cần
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/lilmaxie/anime-recommendation-system.git']])
                }
            }
        }

        stage("Making a virtual environment..."){
            steps{
                script{
                    echo 'Making a virtual environment...'
                    sh '''
                    if [ ! -d "${VENV_DIR}" ]; then
                        python3 -m venv ${VENV_DIR}
                    fi
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    # Dùng --no-cache-dir để tránh làm đầy ổ cứng ảo
                    pip install --no-cache-dir -e .
                    pip install --no-cache-dir dvc
                    '''
                }
            }
        }

        stage('DVC Pull'){
            steps{
                withCredentials([file(credentialsId:'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script{
                        echo 'DVC Pull...'
                        sh '''
                        . ${VENV_DIR}/bin/activate
                        # Thêm --force để ghi đè dữ liệu cũ nếu có xung đột
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
                        # Nhớ đổi tên cluster và region cho đúng với GCP của bạn
                        gcloud container clusters get-credentials ml-app-cluster --region asia-east1
                        kubectl apply -f deployment.yaml
                        '''
                    }
                }
            }
        }
    }
}