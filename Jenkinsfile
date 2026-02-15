pipeline {
    agent any
    
    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    
    stages {
        stage('🧹 Очистка') {
            steps {
                cleanWs()
            }
        }
        
        stage('🐍 Установка зависимостей') {
            steps {
                bat '''
                    python -m venv venv
                    call venv\\Scripts\\activate
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                    pip list
                '''
            }
        }
        
        stage('🧪 Запуск теста') {
            steps {
                bat '''
                    call venv\\Scripts\\activate
                    pytest test_shoporg_perfect.py --alluredir=allure-results --clean-alluredir -v
                '''
            }
        }
        
        stage('📊 Генерация отчёта Allure') {
            steps {
                allure([
                    includeProperties: false,
                    jdk: '',
                    results: [[path: 'allure-results']]
                ])
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'screenshots/*.png', allowEmptyArchive: true
        }
        success {
            echo '✅ Тест пройден успешно!'
        }
        failure {
            echo '❌ Тест упал'
        }
    }
}
