pipeline {
    agent any
    
    options {
        timeout(time: 20, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    
    stages {
        stage('🧹 Очистка') {
            steps {
                cleanWs()
                bat 'echo Рабочая директория очищена'
            }
        }
        
        stage('🐍 Установка зависимостей') {
            steps {
                bat '''
                    python --version
                    python -m venv venv
                    call venv\\Scripts\\activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip list
                '''
            }
        }
        
        stage('🧪 Запуск теста') {
            steps {
                bat '''
                    call venv\\Scripts\\activate
                    pytest test_shoporg_perfect.py --alluredir=allure-results --clean-alluredir -v --tb=short
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
            archiveArtifacts artifacts: 'allure-results/**', allowEmptyArchive: true
        }
        success {
            echo '✅ Тест пройден успешно! Отчёт доступен во вкладке "Allure Report"'
        }
        failure {
            echo '❌ Тест упал. Проверьте логи и скриншоты в отчёте.'
        }
    }
}
