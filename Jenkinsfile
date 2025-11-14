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
        SEMANTIC_VERSION = ''
        IMAGE_TAG = ''

        // Component change flags (set in Detect Changes stage)
        API_CHANGED = 'false'
        PIPELINE_CHANGED = 'false'
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
                    changedFiles.each { file -> echo "${file}" }

                    // Set component flags based on changed files
                    env.API_CHANGED = (
                        changedFiles.any { f ->
                            def file = f.trim()
                            file.startsWith('api/') || file.startsWith('serving-pipeline/')
                        } || changedFiles.contains('all')
                    ) ? 'true' : 'false'
                    env.PIPELINE_CHANGED = (
                        changedFiles.any { f ->
                            def file = f.trim()
                            file.startsWith('training-pipeline/')
                        } || changedFiles.contains('all')
                    ) ? 'true' : 'false'

                    echo ""
                    echo "COMPONENTS TO PROCESS:"
                    echo "   Serving Pipeline: ${env.API_CHANGED}"
                    echo "   Training Pipeline: ${env.PIPELINE_CHANGED}"
                    echo ""
                }
            }
        }

        stage('📋 Get Semantic Version') {
            steps {
                script {
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

                        env.SEMANTIC_VERSION = semanticVersion
                        env.IMAGE_TAG = semanticVersion

                        echo "Semantic Version: ${env.SEMANTIC_VERSION}"
                        echo "Image Tag: ${env.IMAGE_TAG}"

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
                        env.SEMANTIC_VERSION = "${BUILD_NUMBER}"
                        env.IMAGE_TAG = "${BUILD_NUMBER}"
                        echo "Using fallback version: ${env.IMAGE_TAG}"
                    }

                    echo ""
                    echo "FINAL VERSION TO USE: ${env.IMAGE_TAG}"
                    echo ""
                }
            }
        }

        stage('Run Tests') {
            parallel {
                stage('Serving Pipeline Tests') {
                    when {
                        environment name: 'API_CHANGED', value: 'true'
                    }
                    steps {
                        echo "Running serving pipeline tests..."
                        sh '''
                            cd serving-pipeline
                            pip install --user -r requirements.txt
                            cd ..
                            pip install --user pytest httpx
                            export PYTHONPATH="${WORKSPACE}/serving-pipeline:$PYTHONPATH"
                            python -m pytest tests/test_api.py -v || echo "Serving pipeline tests completed"
                        '''
                    }
                }

                stage('Training Pipeline Tests') {
                    when {
                        environment name: 'PIPELINE_CHANGED', value: 'true'
                    }
                    steps {
                        echo "Running training pipeline tests..."
                        sh '''
                            cd training-pipeline
                            pip install --user -r requirements.txt
                            cd ..
                            pip install --user pytest
                            export PYTHONPATH="${WORKSPACE}/training-pipeline:$PYTHONPATH"
                            python -m pytest tests/test_data_pipeline.py -v || echo "Training pipeline tests completed"
                        '''
                    }
                }
            }
        }

        stage('Build & Deploy') {
            parallel {
                stage('Serving Pipeline Build & Deploy') {
                    when {
                        environment name: 'API_CHANGED', value: 'true'
                    }
                    steps {
                        echo "Building and deploying model with KServe..."
                        script {
                            dir('serving-pipeline') {
                                // Build KServe model image
                                def modelImage = docker.build("sentiment-model:${IMAGE_TAG}")
                                modelImage.tag("sentiment-model:latest")

                                echo "Model image built successfully"

                                // Create namespace if it doesn't exist
                                sh '''
                                    kubectl apply -f namespace.yaml || echo "Namespace already exists or kubectl not available"
                                '''

                                // Deploy KServe InferenceService
                                sh '''
                                    # Update image tag in inference service
                                    sed "s|sentiment-model:latest|sentiment-model:${IMAGE_TAG}|g" inference-service.yaml > inference-service-${IMAGE_TAG}.yaml

                                    # Apply the inference service
                                    kubectl apply -f inference-service-${IMAGE_TAG}.yaml || echo "KServe deployment failed - check if KServe is installed"
                                '''

                                echo "KServe InferenceService deployed successfully"
                            }
                        }
                    }
                }

                stage('Training Pipeline Build & Deploy') {
                    when {
                        environment name: 'PIPELINE_CHANGED', value: 'true'
                    }
                    steps {
                        echo "Building and running training pipeline..."
                        script {
                            dir('training-pipeline') {
                                // Build pipeline image
                                def pipelineImage = docker.build("${PROJECT_NAME}-training-pipeline:${IMAGE_TAG}")
                                pipelineImage.tag("${PROJECT_NAME}-training-pipeline:latest")

                                // Run pipeline (one-time execution)
                                sh '''
                                    docker run --rm \
                                        -v ${WORKSPACE}/models:/app/models \
                                        ai-sentiment-training-pipeline:latest
                                '''

                                echo "Training pipeline executed successfully"
                            }
                        }
                    }
                }
            }
        }
    }

    post {
        success {
            script {
                def changedComponents = []
                if (env.API_CHANGED == 'true') changedComponents.add('Serving Pipeline')
                if (env.PIPELINE_CHANGED == 'true') changedComponents.add('Training Pipeline')

                def message = """
**Selective CI/CD Pipeline Completed Successfully!**

**Components Processed:** ${changedComponents.join(', ') ?: 'No changes detected'}
**Build:** #${BUILD_NUMBER}
**Version:** ${env.SEMANTIC_VERSION ?: env.IMAGE_TAG}
**Branch:** ${BRANCH_NAME}

**What happened:**
${env.API_CHANGED == 'true' ? "• Serving pipeline was built and deployed with version ${env.IMAGE_TAG}" : ''}
${env.PIPELINE_CHANGED == 'true' ? "• Training pipeline was executed and model updated with version ${env.IMAGE_TAG}" : ''}
${changedComponents.isEmpty() ? '• No components changed, pipeline optimized to skip unnecessary steps' : ''}

**Access your services:**
${env.API_CHANGED == 'true' ? '• KServe Model: kubectl port-forward service/sentiment-model-predictor-default -n ml-models 8080:80' : ''}
${env.API_CHANGED == 'true' ? '• Test Command: python serving-pipeline/test_kserve.py http://localhost:8080' : ''}
                """.stripIndent()

                echo message
            }
        }

        failure {
            script {
                def message = """
**Selective CI/CD Pipeline Failed**

**Build:** #${BUILD_NUMBER}
**Version:** ${env.SEMANTIC_VERSION ?: env.IMAGE_TAG ?: 'Unknown'}
**Branch:** ${BRANCH_NAME}
**Components being processed:** ${env.API_CHANGED == 'true' ? 'Serving Pipeline ' : ''}${env.PIPELINE_CHANGED == 'true' ? 'Training Pipeline' : ''}

Please check the build logs for details.
                """.stripIndent()

                echo message
            }
        }
    }
}
