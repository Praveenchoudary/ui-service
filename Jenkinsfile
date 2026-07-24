pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    environment {
        APP_REPO = "https://github.com/Praveenchoudary/ui-service.git"
        
        APP_BRANCH      = "main"

        GITOPS_REPO     = "https://github.com/Praveenchoudary/new-hotel-booking-gitops.git"
        GITOPS_BRANCH   = "main"

        DOCKER_USERNAME = "praveen22233"

        IMAGE_NAME = "ui-service"

        IMAGE_TAG       = "${BUILD_NUMBER}"

        FULL_IMAGE      = "${DOCKER_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"

       TARGET_ENV = "${env.BRANCH_NAME == 'main' ? 'prod' : 'dev'}"
    }

    stages {

        stage('Clean Workspace') {
            steps {
                cleanWs()
            }
        }

        stage('Checkout Application') {
            steps {
                dir('application') {
                    git branch: APP_BRANCH, url: APP_REPO
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                dir('application') {
                    sh """
                    docker build \
                    -t ${FULL_IMAGE} \
                    -t ${DOCKER_USERNAME}/${IMAGE_NAME}:latest .
                    """
                }
            }
        }

        stage('Smoke Test') {
            steps {
                sh """
                docker run -d \
                --name smoke-${IMAGE_NAME} \
                -p 8091:8080 \
                ${FULL_IMAGE}

                sleep 10

                docker ps

                curl -f http://localhost:8091/health || exit 1

                docker rm -f smoke-${IMAGE_NAME}
                """
            }
        }

      stage('Trivy Scan') {
          steps {
        sh '''
        trivy image \
        --severity HIGH,CRITICAL \
        --exit-code 0 \
        ${FULL_IMAGE}
              '''
    }
      }
        stage('Docker Login') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {

                    sh """
                    echo \$DOCKER_PASS | docker login \
                    -u \$DOCKER_USER \
                    --password-stdin
                    """
                }
            }
        }

        stage('Push Image') {
            steps {
                sh """
                docker push ${FULL_IMAGE}
                docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:latest
                """
            }
        }

        stage('Checkout GitOps Repo') {
            steps {
                dir('gitops') {
                    git branch: GITOPS_BRANCH, url: GITOPS_REPO
                }
            }
        }

        stage('Update Helm Values') {
            steps {
                dir('gitops') {

                    sh """
                    sed -i 's/tag:.*/tag: "${IMAGE_TAG}"/' charts/${IMAGE_NAME}/values-prod.yaml

                    cat charts/${IMAGE_NAME}/values-dev.yaml
                    """
                }
            }
        }

        stage('Commit & Push') {
            steps {

                withCredentials([
                    usernamePassword(
                        credentialsId: 'github-creds',
                        usernameVariable: 'GIT_USER',
                        passwordVariable: 'GIT_TOKEN'
                    )
                ]) {

                    dir('gitops') {

                        sh """
                        git config user.name Jenkins

                        git config user.email jenkins@example.com

                        git add charts/${IMAGE_NAME}/values-prod.yaml

                        git commit -m "Deploy ${IMAGE_NAME}:${IMAGE_TAG}" || true

                        git remote set-url origin https://${GIT_USER}:${GIT_TOKEN}@github.com/Praveenchoudary/new-hotel-booking-gitops.git

                        git push origin main
                        """
                    }

                }

            }
        }

    }

    post {

        always {

            sh "docker logout || true"

            sh "docker rmi ${FULL_IMAGE} ${DOCKER_USERNAME}/${IMAGE_NAME}:latest || true"

            cleanWs()

        }

    }

}
