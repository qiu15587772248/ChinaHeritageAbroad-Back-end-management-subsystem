from app import create_app
import os

# 禁用.env文件加载
os.environ['FLASK_SKIP_DOTENV'] = '1'

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 