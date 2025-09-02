# 数据处理、清洗、特征工程逻辑
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
import logging

class DataProcessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.imputer = SimpleImputer(strategy='mean')
        
    def load_data(self, file_path):
        """加载数据文件"""
        try:
            if file_path.endswith('.csv'):
                return pd.read_csv(file_path)
            elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                return pd.read_excel(file_path)
            else:
                raise ValueError("不支持的文件格式")
        except Exception as e:
            logging.error(f"数据加载失败: {e}")
            return None
    
    def clean_data(self, df):
        """数据清洗"""
        # 删除重复行
        df = df.drop_duplicates()
        
        # 处理缺失值
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = self.imputer.fit_transform(df[numeric_columns])
        
        return df
    
    def feature_engineering(self, df):
        """特征工程"""
        # 标准化数值特征
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            df[numeric_columns] = self.scaler.fit_transform(df[numeric_columns])
        
        # 编码分类特征
        categorical_columns = df.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
            df[col] = self.label_encoders[col].fit_transform(df[col].astype(str))
        
        return df
    
    def get_data_summary(self, df):
        """获取数据摘要信息"""
        summary = {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'basic_stats': df.describe().to_dict()
        }
        return summary