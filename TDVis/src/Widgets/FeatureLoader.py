import pandas as pd
import streamlit as st
from ..Utils.FileUtils import FileUtils


class FeatureLoader:
    '''
    功能：
        1. 加载特征数据
        2. 加载PrSM数据
    直接从外部传入列名映射和本地化对象，从而确保解耦合

    '''
    def __init__(self, column_map,locale):
        self.locale = locale
        self.column_map = column_map

    @st.cache_data
    def load_feature_data(_self, selected_path, sample_name):    
        feature_path = FileUtils.get_file_path('_ms1.feature', selected_path=selected_path, sample_name=sample_name)
        if not feature_path:
            error_text = _self.locale.get("feature_file_not_found", "❌ 未找到特征文件")
            st.error(error_text)
            return None
        
        try:
            df = pd.read_csv(feature_path, sep='\t')
            required_columns = _self.column_map['mass'] + _self.column_map['time']
            if not any(col in df.columns for col in required_columns):
                missing_cols = [col for col in required_columns if col not in df.columns]
                error_text = _self.locale.get("missing_required_columns", "❌ 缺少必要质量/时间列: {0}").format(', '.join(missing_cols))
                st.error(error_text)
                return None
            return df

        except Exception as e:
            error_text = _self.locale.get("feature_load_failed", "⛔ 特征数据加载失败: {0}").format(str(e))
            st.error(error_text)
            return None
    
    @st.cache_data
    def load_feature_data2(_self, selected_path, sample_name):    
        feature_path = FileUtils.get_file_path('_ms1.feature', selected_path=selected_path, sample_name=sample_name)
        if not feature_path:
            # 替换为本地化错误提示
            error_text = _self.locale.get("feature_file_not_found", "❌ 未找到特征文件")
            st.error(error_text)
            return None
        try:
            return pd.read_csv(feature_path, sep='\t')
        except Exception as e:
            # 替换为本地化错误提示（支持格式化）
            error_text = _self.locale.get("feature_load_failed", "⛔ 特征数据加载失败: {0}").format(str(e))
            st.error(error_text)
            return None
        try:
            return pd.read_csv(feature_path, sep='\t')
        except Exception as e:
            # 替换为本地化错误提示（支持格式化）
            error_text = _self.locale.get("feature_load_failed", "⛔ 特征数据加载失败: {0}").format(str(e))
            st.error(error_text)
            return None

    @st.cache_data
    def load_prsm_data(_self, selected_path, sample_name):
        """加载PrSM数据并缓存"""
        prsm_path = FileUtils.get_file_path('_ms2_toppic_prsm_single.tsv', selected_path=selected_path, sample_name=sample_name)
        if not prsm_path:
            # 替换为本地化错误提示
            error_text = _self.locale.get("prsm_file_not_found", "❌ 未找到PrSM数据文件")
            st.error(error_text)
            return None

        try:
            with open(prsm_path, 'r') as f:
                empty_line_idx = None
                for i, line in enumerate(f):
                    if not line.strip():
                        empty_line_idx = i
                        break

            return pd.read_csv(
                prsm_path,
                sep='\t',
                skiprows=empty_line_idx + 1 if empty_line_idx is not None else 0,
                header=0,
                on_bad_lines='warn',
                dtype=str,
                engine='python',
                quoting=3
            ).dropna(how='all')
        except pd.errors.EmptyDataError:
            # 替换为本地化错误提示（支持文件名格式化）
            error_text = _self.locale.get("prsm_file_empty", "文件 {0} 内容为空").format(os.path.basename(prsm_path))
            st.error(error_text)
            return None
        except Exception as e:
            # 替换为本地化错误提示（支持文件名和错误信息格式化）
            error_text = _self.locale.get("prsm_load_failed", "加载 {0} 失败: {1}").format(os.path.basename(prsm_path), str(e))
            st.error(error_text)
            return None


    def load_data(self):
        """数据加载与校验（主方法）"""
        selected_path = st.session_state['user_select_file']
        sample_name = st.session_state['sample']
        
        df = self.load_feature_data(selected_path, sample_name)
        df2 = self.load_prsm_data(selected_path, sample_name)

        if df is None or df2 is None:
            return False

        # 将所有列名匹配结果存入session_state
        st.session_state.feature_state.update({
            'mass_col': self.find_column(self.column_map['mass'], df),
            'time_col': self.find_column(self.column_map['time'], df),
            'intensity_col': self.find_column(self.column_map['intensity'], df),
            'start_time_col': self.find_column(self.column_map['start_time'], df),
            'end_time_col': self.find_column(self.column_map['end_time'], df),
            'feature_col': self.find_column(self.column_map['feature'], df)
        })
        
        # 类型转换和校验
        if st.session_state.feature_state['mass_col']:
            df[st.session_state.feature_state['mass_col']] = df[st.session_state.feature_state['mass_col']].astype(float)
            
            # 从session_state获取列名
            required_cols = ['mass_col', 'time_col', 'intensity_col', 'start_time_col', 'end_time_col']
            if not all(st.session_state.feature_state.get(col) for col in required_cols):
                missing = [
                    f"{col.split('_')[0]} ({', '.join(self.column_map[col.split('_')[0]])})"
                    for col in required_cols 
                    if not st.session_state.feature_state.get(col)
                ]
                error_text = self.locale.get("missing_required_columns", "❌ 缺少必要列: {0}").format(', '.join(missing))
                st.error(error_text)
                return False
        return True

    def load_data2(self):
        """数据加载与校验（对比样本）"""
        selected_path = st.session_state['user_select_file2']
        sample_name = st.session_state['sample2']

        df = self.load_feature_data2(selected_path, sample_name)
        
        # 将对比样本列名全部存入session_state
        st.session_state.feature_state.update({
            'mass_col2': self.find_column(self.column_map['mass'], df),
            'time_col2': self.find_column(self.column_map['time'], df),
            'intensity_col2': self.find_column(self.column_map['intensity'], df),
            'start_time_col2': self.find_column(self.column_map['start_time'], df),
            'end_time_col2': self.find_column(self.column_map['end_time'], df)
        })
        
        if st.session_state.feature_state['mass_col2']:
            df[st.session_state.feature_state['mass_col2']] = df[st.session_state.feature_state['mass_col2']].astype(float)
        
        return True

    def find_column(self, candidates, df):
        """在数据框中查找候选列名（支持列名格式容错）"""
        for col in candidates:
            # 统一去除特殊字符后匹配
            normalized_col = col.replace(' ', '_').lower()
            for df_col in df.columns:
                if df_col.replace(' ', '_').lower() == normalized_col:
                    return df_col
        return None