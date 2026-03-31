pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 15, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        PROJECT_DIR   = "${WORKSPACE}"
        PYTHON        = 'python3'
        REPORT_DIR    = 'reports'
        CHROMEDRIVER  = "${WORKSPACE}/chromedriver"
    }

    stages {

        stage('Checkout') {
            steps {
                echo '── Cloning GitHub repository ──'
                bat """
                    if exist student-feedback-form rmdir /s /q student-feedback-form
                    git clone https://github.com/PinakRokde/student-feedback-form.git
                    cd student-feedback-form
                    dir
                """
            }
        }

        stage('Setup Environment') {
            steps {
                echo '── Installing Python dependencies ──'
                bat """
                    cd student-feedback-form
                    where python >nul 2>nul || (echo Python is not in PATH. Please install Python 3 and add it to PATH. && exit /b 1)
                    python --version
                    python -m pip install --upgrade pip
                    python -m pip install selenium webdriver-manager pytest pytest-html
                """
            }
        }

        stage('Verify ChromeDriver') {
            steps {
                echo '── Checking ChromeDriver & Chrome versions ──'
                bat """
                    cd student-feedback-form
                    if exist chromedriver (
                        echo Local chromedriver:
                        chromedriver --version
                    ) else (
                        echo No local chromedriver found — webdriver_manager will download one.
                    )
                    where chrome >nul 2>nul && chrome --version || echo Chrome binary not found in PATH
                """
            }
        }

        stage('Run Selenium Tests') {
            steps {
                echo '── Running Selenium test suite ──'
                bat """
                    cd student-feedback-form
                    if not exist reports mkdir reports
                    python -m pytest test_form.py -v --html=reports/test_report.html --self-contained-html --tb=short -p no:cacheprovider
                """
            }
        }
    }

    post {
        always {
            echo '── Publishing test report ──'
            // publishHTML(target: [
            //     allowMissing:         false,
            //     alwaysLinkToLastBuild: true,
            //     keepAll:              true,
            //     reportDir:            'reports',
            //     reportFiles:          'test_report.html',
            //     reportName:           'Selenium Test Report'
            // ])
        }

        success {
            echo "✅ All tests passed on branch: ${env.BRANCH_NAME ?: 'local'}"
        }

        failure {
            echo "❌ Tests failed — check the Selenium Test Report above."
            // Uncomment to email on failure:
            // mail to: 'dev@symbiosis.ac.in',
            //      subject: "FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
            //      body: "See console output at ${env.BUILD_URL}"
        }

        cleanup {
            echo '── Cleaning workspace ──'
            cleanWs()
        }
    }
}
