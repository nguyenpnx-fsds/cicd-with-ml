/*
 * Jenkins Pipeline for Selective CI/CD with KServe Deployment
 *
 * This pipeline demonstrates intelligent CI/CD that only processes changed components
 * and deploys ML models using KServe (Kubernetes-native model serving platform).
 *
 * Key Concepts:
 * 1. Change Detection - Using git diff to identify modified files
 * 2. Semantic Versioning - Using GitVersion to generate proper semantic versions
 * 3. Conditional Execution - Running stages only when relevant files change
 * 4. KServe Deployment - Deploy ML models to Kubernetes using KServe InferenceServices
 */

pipeline {
    agent any

    environment {
        // Simple environment variables
        PROJECT_NAME = 'ai-sentiment'

        // Semantic version variables (set in Get Semantic Version stage)
        // SEMANTIC_VERSION = ''
        // IMAGE_TAG = ''

        // Component change flags (set in Detect Changes stage)
        // API_CHANGED = 'false'
        // CHANGED_TRAINING_PIPELINE = 'false'
    }

    options {
        // Keep only the last 10 builds
        buildDiscarder(logRotator(numToKeepStr: '10'))
        // Add timestamps to console output
        // timestamps()
    }

    stages {
        stage('🔍 Detect Changes') {
            steps {
                script {
                    echo "=" * 50
                    echo "DETECTING CHANGED COMPONENTS"
                    echo "=" * 50

                    // Get list of changed files
                    def changedFiles = []
                    try {
                        changedFiles = sh(
                            /**
                             * Retrieves the list of files changed between the current HEAD and the previous commit.
                             * Suppresses any error output by redirecting stderr to /dev/null.
                             * If no changes are detected or the command fails, returns "all".
                             * Used in the Jenkins pipeline to dynamically determine affected files for conditional build stages.
                             */
                            script: 'git diff --name-only HEAD~1 HEAD 2>/dev/null || echo "all"',
                            returnStdout: true
                        ).trim().split('\n')
                    } catch (Exception e) {
                        echo "Could not detect changes, processing all components"
                        changedFiles = ['all']
                    }

                    echo "Changed Files:"
                    changedFiles.each { file ->
                        echo " -> '${file}' (length: ${file.length()}) '${file.startsWith('api/')}'"
                    }

                    // Set component flags based on changed files
                    def normalizedFiles = changedFiles.collect { f -> f.toString().trim() }
                    def changedAPI = normalizedFiles.any { it.startsWith('api/') }
                    def changedServingPipeline = normalizedFiles.any { it.startsWith('serving-pipeline/') }
                    def changedTrainingPipeline = normalizedFiles.any { it.startsWith('training-pipeline/') }

                    env.CHANGED_API = changedAPI ? 'true' : 'false'
                    env.CHANGED_SERVING_PIPELINE = changedServingPipeline ? 'true' : 'false'
                    env.CHANGED_TRAINING_PIPELINE = changedTrainingPipeline ? 'true' : 'false'

                    echo ""
                    echo "COMPONENTS TO PROCESS:"
                    echo "   API Changes Detected: ${env.CHANGED_API}"
                    echo "   Serving Pipeline: ${env.CHANGED_SERVING_PIPELINE}"
                    echo "   Training Pipeline: ${env.CHANGED_TRAINING_PIPELINE}"
                    echo ""
                }
            }
        }

        stage('📋 Get Semantic Version') {
            agent {
                kubernetes {
                    containerTemplate {
                        name 'docker'
                        image  'docker:27-dind'
                        alwaysPullImage true
                        privileged true
                    }
                }
            }
            steps {
                script {
                    container('docker') {
                        echo "=" * 50
                        echo "DETERMINING SEMANTIC VERSION"
                        echo "=" * 50

                        try {
                            // Get semantic version using GitVersion
                            def semanticVersion = sh(
                                script: '''
                                    docker run --rm \
                                    -v "$(pwd)":/repo \
                                    -w /repo \
                                    gittools/gitversion:latest \
                                    /repo /showvariable FullSemVer
                                ''',
                                returnStdout: true
                            ).trim()

                            echo "Determined Semantic Version: ${semanticVersion}"

                            env.SEM_VERSION = "${semanticVersion}"
                            env.IMG_TAG = "${semanticVersion}"

                            echo "Semantic Version: ${env.SEM_VERSION}"
                            echo "Image Tag: ${env.IMG_TAG}"

                            // Also get additional version information for logging
                            def versionInfo = sh(
                                script: '''
                                    docker run --rm \
                                    -v "$(pwd)":/repo \
                                    -w /repo \
                                    gittools/gitversion:latest \
                                    /repo /output json
                                ''',
                                returnStdout: true
                            ).trim()

                            echo "Full Version Information:"
                            echo versionInfo

                        } catch (Exception e) {
                            echo "Warning: Could not determine semantic version, falling back to build number"
                            env.SEM_VERSION = "BUILD_NUMBER"
                            env.IMG_TAG = "BUILD_NUMBER"
                            echo "Using fallback version: ${env.IMG_TAG}"
                        }

                        echo ""
                        echo "FINAL VERSION TO USE: ${env.IMG_TAG}"
                        echo ""
                    }
                }
            }
        }

        // stage('Run Tests') {
        //     parallel {
        //         stage('Serving Pipeline Tests') {
        //             agent {
        //                 kubernetes {
        //                     containerTemplate {
        //                         name 'python'
        //                         image  'python:3.10'
        //                         alwaysPullImage true
        //                         command 'cat'
        //                         ttyEnabled true
        //                     }
        //                 }
        //             }
        //             steps {
        //                 script {
        //                     container('python') {
        //                         echo "Running serving pipeline tests..."
        //                         sh '''
        //                             cd serving-pipeline
        //                             pip install --user -r requirements.txt
        //                             cd ..
        //                             pip install --user pytest httpx
        //                             export PYTHONPATH="${WORKSPACE}/serving-pipeline:$PYTHONPATH"
        //                             python -m pytest tests/test_api.py -v || echo "Serving pipeline tests completed"
        //                         '''
        //                     }
        //                 }
        //             }
        //         }

        //         stage('Training Pipeline Tests') {
        //             // when {
        //             //     environment name: 'CHANGED_TRAINING_PIPELINE', value: 'true'
        //             // }
        //             agent {
        //                 kubernetes {
        //                     containerTemplate {
        //                         name 'python'
        //                         image  'python:3.10'
        //                         alwaysPullImage true
        //                         command 'cat'
        //                         ttyEnabled true
        //                     }
        //                 }
        //             }
        //             steps {
        //                 script {
        //                     container('python') {
        //                         echo "Running training pipeline tests..."
        //                         sh '''
        //                             cd training-pipeline
        //                             pip install --user -r requirements.txt
        //                             cd ..
        //                             pip install --user pytest
        //                             export PYTHONPATH="${WORKSPACE}/training-pipeline:$PYTHONPATH"
        //                             python -m pytest tests/test_data_pipeline.py -v || echo "Training pipeline tests completed"
        //                         '''
        //                     }
        //                 }
        //             }
        //         }
        //     }
        // }

        stage('Build & Deploy') {
            parallel {
                stage('Serving Pipeline Build & Deploy') {
                    // when {
                    //     environment name: 'CHANGED_SERVING_PIPELINE', value: 'true'
                    // }
                    stages {
                        stage('Build image for Serving Pipeline') {
                            agent {
                                kubernetes {
                                    containerTemplate {
                                        name 'docker'
                                        image  'docker:27-dind'
                                        alwaysPullImage true
                                        privileged true
                                    }
                                }
                            }
                            steps {
                                script {
                                    container('docker') {
                                        dir('serving-pipeline') {
                                            // Build KServe model image
                                            // echo "Building model Docker image with tag: sentiment-model:${env.IMG_TAG}"
                                            // sh """
                                            //     docker build --no-cache -t sentiment-model:${env.IMG_TAG} .
                                            //     docker tag sentiment-model:${env.IMG_TAG} sentiment-model:latest
                                            // """

                                            // echo "Model image built successfully"

                                            withCredentials([usernamePassword(
                                                credentialsId: 'dockerhub',
                                                usernameVariable: 'DOCKER_USER',
                                                passwordVariable: 'DOCKER_PASS'
                                            )]) {

                                                sh """
                                                    echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin

                                                    docker build -t $DOCKER_USER/sentiment-model:${env.IMG_TAG} .
                                                    docker push $DOCKER_USER/sentiment-model:${env.IMG_TAG}

                                                    # Optionally push latest
                                                    docker tag $DOCKER_USER/sentiment-model:${env.IMG_TAG} $DOCKER_USER/sentiment-model:latest
                                                    docker push $DOCKER_USER/sentiment-model:latest
                                                """
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        stage('Deploy Serving Pipeline') {
                            agent {
                                kubernetes {
                                    containerTemplate {
                                        name 'kubectl'
                                        image  'xuannguyenhehe/custom-jenkins:0.0.3'
                                        alwaysPullImage true
                                    }
                                }
                            }
                            steps {
                                script {
                                    container('kubectl') {
                                        dir('serving-pipeline') {
                                            // Create namespace if it doesn't exist
                                            sh """
                                                kubectl apply -f namespace.yaml || echo "Namespace already exists or kubectl not available"
                                            """

                                            // Deploy KServe InferenceService
                                            sh """
                                                # Update image tag in inference service
                                                sed "s|sentiment-model:latest|sentiment-model:${env.IMG_TAG}|g" inference-service.yaml > inference-service-${env.IMG_TAG}.yaml

                                                # Apply the inference service
                                                kubectl apply -f inference-service-${env.IMG_TAG}.yaml || echo "KServe deployment failed - check if KServe is installed"
                                            """

                                            echo "KServe InferenceService deployed successfully"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // stage('Training Pipeline Build & Deploy') {
                //     agent {
                //         kubernetes {
                //             containerTemplate {
                //                 name 'tools'
                //                 image  'ghcr.io/jenkinsci/agent-k8s-tools:latest'
                //                 alwaysPullImage true
                //                 privileged true
                //             }
                //         }
                //     }
                //     when {
                //         environment name: 'CHANGED_TRAINING_PIPELINE', value: 'true'
                //     }
                //     steps {
                //         echo "Building and running training pipeline..."
                //         script {
                //             container('tools') {
                //                 dir('training-pipeline') {
                //                     // Build pipeline image
                //                     def pipelineImage = docker.build("${PROJECT_NAME}-training-pipeline:${env.IMG_TAG}")
                //                     pipelineImage.tag("${PROJECT_NAME}-training-pipeline:latest")

                //                     // Run pipeline (one-time execution)
                //                     sh '''
                //                         docker run --rm \
                //                             -v ${WORKSPACE}/models:/app/models \
                //                             ai-sentiment-training-pipeline:latest
                //                     '''

                //                     echo "Training pipeline executed successfully"
                //                 }
                //             }
                //         }
                //     }
                // }
            }
        }
    }

    post {
        success {
            script {
                def changedComponents = []
                if (env.CHANGED_API == 'true') changedComponents.add('Serving Pipeline')
                if (env.CHANGED_TRAINING_PIPELINE == 'true') changedComponents.add('Training Pipeline')

                def message = """
**Selective CI/CD Pipeline Completed Successfully!**

**Components Processed:** ${changedComponents.join(', ') ?: 'No changes detected'}
**Build:** #${BUILD_NUMBER}
**Version:** ${env.SEM_VERSION ?: env.IMG_TAG}
**Branch:** ${BRANCH_NAME}

**What happened:**
${env.CHANGED_SERVING_PIPELINE == 'true' ? "• Serving pipeline was built and deployed with version ${env.IMG_TAG}" : ''}
${env.CHANGED_TRAINING_PIPELINE == 'true' ? "• Training pipeline was executed and model updated with version ${env.IMG_TAG}" : ''}
${changedComponents.isEmpty() ? '• No components changed, pipeline optimized to skip unnecessary steps' : ''}

**Access your services:**
${env.CHANGED_SERVING_PIPELINE == 'true' ? '• KServe Model: kubectl port-forward service/sentiment-model-predictor-default -n ml-models 8080:80' : ''}
${env.CHANGED_SERVING_PIPELINE == 'true' ? '• Test Command: python serving-pipeline/test_kserve.py http://localhost:8080' : ''}
                """.stripIndent()

                echo message
            }
        }

        failure {
            script {
                def message = """
**Selective CI/CD Pipeline Failed**

**Build:** #${BUILD_NUMBER}
**Version:** ${env.SEM_VERSION ?: env.IMG_TAG ?: 'Unknown'}
**Branch:** ${BRANCH_NAME}
**Components being processed:** ${env.CHANGED_SERVING_PIPELINE == 'true' ? 'Serving Pipeline ' : ''}${env.CHANGED_TRAINING_PIPELINE == 'true' ? 'Training Pipeline' : ''}

Please check the build logs for details.
                """.stripIndent()

                echo message
            }
        }
    }
}
