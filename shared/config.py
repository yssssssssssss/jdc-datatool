# 共享配置，如API密钥等
import os
from typing import Dict, Any

class Config:
    """应用配置类"""
    
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        """加载配置"""
        # 数据库配置
        self.DATABASE_CONFIG = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', 5432),
            'database': os.getenv('DB_NAME', 'jdc_datatool'),
            'username': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        }
        
        # API配置
        self.API_CONFIG = {
            'openai_api_key': os.getenv('OPENAI_API_KEY', '35f54cc4-be7a-4414-808e-f5f9f0194d4f'),
            'openai_model': os.getenv('OPENAI_MODEL', 'gpt-4o-0806'),
            'openai_base_url': os.getenv('OPENAI_BASE_URL', 'http://gpt-proxy.jd.com/v1'),
            'max_tokens': int(os.getenv('MAX_TOKENS', '2000')),
            'temperature': float(os.getenv('TEMPERATURE', '0.7'))
        }
        
        # 文件上传配置
        self.UPLOAD_CONFIG = {
            'max_file_size': int(os.getenv('MAX_FILE_SIZE', '200')),  # MB
            'allowed_extensions': ['csv', 'xlsx', 'xls', 'json'],
            'upload_folder': os.getenv('UPLOAD_FOLDER', 'uploads'),
            'temp_folder': os.getenv('TEMP_FOLDER', 'temp')
        }
        
        # 应用配置
        self.APP_CONFIG = {
            'debug': os.getenv('DEBUG', 'False').lower() == 'true',
            'host': os.getenv('HOST', '0.0.0.0'),
            'port': int(os.getenv('PORT', '7701')),
            'secret_key': os.getenv('SECRET_KEY', 'your-secret-key-here'),
            'cors_origins': os.getenv('CORS_ORIGINS', '*').split(',')
        }
        
        # Streamlit配置
        self.STREAMLIT_CONFIG = {
            'port': int(os.getenv('STREAMLIT_PORT', '7001')),
            'host': os.getenv('STREAMLIT_HOST', '0.0.0.0'),
            'theme': {
                'primaryColor': '#1f77b4',
                'backgroundColor': '#ffffff',
                'secondaryBackgroundColor': '#f0f2f6',
                'textColor': '#262730'
            }
        }
        
        # 日志配置
        self.LOGGING_CONFIG = {
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file': os.getenv('LOG_FILE', 'app.log'),
            'max_bytes': int(os.getenv('LOG_MAX_BYTES', '10485760')),  # 10MB
            'backup_count': int(os.getenv('LOG_BACKUP_COUNT', '5'))
        }
        
        # 数据处理配置
        self.DATA_CONFIG = {
            'max_rows': int(os.getenv('MAX_ROWS', '1000000')),
            'chunk_size': int(os.getenv('CHUNK_SIZE', '10000')),
            'encoding': os.getenv('DEFAULT_ENCODING', 'utf-8'),
            'date_format': os.getenv('DATE_FORMAT', '%Y-%m-%d'),
            'decimal_places': int(os.getenv('DECIMAL_PLACES', '2'))
        }
        
        # 可视化配置
        self.VISUALIZATION_CONFIG = {
            'default_width': int(os.getenv('CHART_WIDTH', '800')),
            'default_height': int(os.getenv('CHART_HEIGHT', '600')),
            'dpi': int(os.getenv('CHART_DPI', '300')),
            'color_palette': os.getenv('COLOR_PALETTE', 'Set3').split(','),
            'font_family': os.getenv('FONT_FAMILY', 'Microsoft YaHei')
        }
    
    def get_config(self, section: str) -> Dict[str, Any]:
        """获取指定配置段"""
        config_map = {
            'database': self.DATABASE_CONFIG,
            'api': self.API_CONFIG,
            'upload': self.UPLOAD_CONFIG,
            'app': self.APP_CONFIG,
            'streamlit': self.STREAMLIT_CONFIG,
            'logging': self.LOGGING_CONFIG,
            'data': self.DATA_CONFIG,
            'visualization': self.VISUALIZATION_CONFIG
        }
        return config_map.get(section, {})
    
    def update_config(self, section: str, key: str, value: Any):
        """更新配置项"""
        config = self.get_config(section)
        if config:
            config[key] = value
    
    def validate_config(self) -> Dict[str, bool]:
        """验证配置完整性"""
        validation_results = {
            'openai_api_key': bool(self.API_CONFIG['openai_api_key']),
            'upload_folder_exists': os.path.exists(self.UPLOAD_CONFIG['upload_folder']),
            'temp_folder_exists': os.path.exists(self.UPLOAD_CONFIG['temp_folder']),
            'secret_key_set': self.APP_CONFIG['secret_key'] != 'your-secret-key-here'
        }
        return validation_results
    
    def create_directories(self):
        """创建必要的目录"""
        directories = [
            self.UPLOAD_CONFIG['upload_folder'],
            self.UPLOAD_CONFIG['temp_folder'],
            'logs',
            'reports',
            'exports'
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                print(f"创建目录: {directory}")

# 全局配置实例
config = Config()

# 常用配置快捷访问
DEBUG = config.APP_CONFIG['debug']
SECRET_KEY = config.APP_CONFIG['secret_key']
OPENAI_API_KEY = config.API_CONFIG['openai_api_key']
UPLOAD_FOLDER = config.UPLOAD_CONFIG['upload_folder']
MAX_FILE_SIZE = config.UPLOAD_CONFIG['max_file_size']

# 环境变量模板（用于部署参考）
ENV_TEMPLATE = """
# JDC数据工具环境变量配置模板

# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=jdc_datatool
DB_USER=postgres
DB_PASSWORD=your_password

# OpenAI API配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_BASE_URL=https://api.openai.com/v1
MAX_TOKENS=2000
TEMPERATURE=0.7

# 应用配置
DEBUG=False
HOST=0.0.0.0
PORT=7701
SECRET_KEY=your_secret_key_here
CORS_ORIGINS=*

# Streamlit配置
STREAMLIT_PORT=7001
STREAMLIT_HOST=0.0.0.0

# 文件上传配置
MAX_FILE_SIZE=200
UPLOAD_FOLDER=uploads
TEMP_FOLDER=temp

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=app.log
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5

# 数据处理配置
MAX_ROWS=1000000
CHUNK_SIZE=10000
DEFAULT_ENCODING=utf-8
DATE_FORMAT=%Y-%m-%d
DECIMAL_PLACES=2

# 可视化配置
CHART_WIDTH=800
CHART_HEIGHT=600
CHART_DPI=300
COLOR_PALETTE=Set3
FONT_FAMILY=Microsoft YaHei
"""

def save_env_template(filename: str = '.env.template'):
    """保存环境变量模板文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(ENV_TEMPLATE)
    print(f"环境变量模板已保存到: {filename}")

if __name__ == "__main__":
    # 创建必要目录
    config.create_directories()
    
    # 验证配置
    validation = config.validate_config()
    print("配置验证结果:")
    for key, value in validation.items():
        status = "✅" if value else "❌"
        print(f"  {status} {key}: {value}")
    
    # 保存环境变量模板
    save_env_template()