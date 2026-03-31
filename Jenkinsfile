pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 15, unit: 'MINUTES')
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Cloning repository...'
                bat '''
                    if exist student-feedback-form rmdir /s /q student-feedback-form
                    git clone https://github.com/PinakRokde/student-feedback-form.git
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing Python packages...'
                bat '''
                    cd student-feedback-form
                    python --version
                    python -m pip install --upgrade pip
                    python -m pip install selenium webdriver-manager pytest pytest-html
                '''
            }
        }

        stage('Run Selenium Test') {
            steps {
                echo 'Running test...'
                bat '''
                    cd student-feedback-form
                    if not exist reports mkdir reports
                    python -m pytest test_form.py -v --html=reports/test_report.html --self-contained-html
                '''
            }
        }
    }

    post {
        success {
            echo 'Build Successful ✅'
        }
        failure {
            echo 'Build Failed ❌'
        }
        always {
            cleanWs()
        }
    }
}