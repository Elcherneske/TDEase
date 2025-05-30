import streamlit as st
import pandas as pd
import numpy as np

class CalculateWidgets:
    def __init__(self):
        pass


    def apply_scale(self, series):
        """应用强度转换并归一化（从session_state获取log_scale）"""
        # 修正：从feature_state获取log_scale
        log_scale = st.session_state.feature_state['log_scale']

        # 原始转换
        if log_scale == 'log2':
            scaled = np.log2(series + 1)
        elif log_scale == 'ln':
            scaled = np.log(series + 1)
        elif log_scale == 'sqrt':
            scaled = np.sqrt(series + 1)
        elif log_scale == 'log10':
            scaled = np.log10(series + 1)
        else:
            scaled = series.copy()

        # 归一化（修复类型转换问题）
        min_val = scaled.min()
        max_val = scaled.max()
        return pd.to_numeric(
            (scaled - min_val) / (max_val - min_val) if (max_val - min_val) > 0 else scaled * 0,
            errors='coerce'
        ).fillna(0)

    def near_peak_process(self, data):
        """查找指定质量附近的邻近峰（从feature_state获取参数）"""
        if data.empty or pd.isna(st.session_state.feature_state.get('selected_mass')):
            return pd.DataFrame()

        # 从feature_state获取参数
        target_mass = float(st.session_state.feature_state['selected_mass'])
        neighbor_range = float(st.session_state.feature_state['neighbor_range'])
        neighbour_limit = float(st.session_state.feature_state['neighbour_limit'])
        mass_col = st.session_state.feature_state['mass_col']
        intensity_col = st.session_state.feature_state['intensity_col']

        # 生成相对强度百分比（显式类型转换）
        max_intensity = float(data[intensity_col].max())
        data['Relative Intensity (%)'] = pd.to_numeric(
            (data[intensity_col] / max_intensity * 100 if max_intensity != 0 else 0),
            errors='coerce'
        ).round(2)

        # 邻近峰筛选（显式类型转换）
        lower_bound = target_mass - neighbor_range
        upper_bound = target_mass + neighbor_range
        neighbors = data[
            (data[mass_col].astype(float).between(lower_bound, upper_bound)) &
            (data["Relative Intensity (%)"].astype(float) >= neighbour_limit)
        ].copy()

        if not neighbors.empty:
            neighbors["mass_diff"] = (neighbors[mass_col].astype(float) - target_mass).round(6)
        return neighbors.sort_values("mass_diff") if not neighbors.empty else neighbors


    def near_peak_match(self, neighbors):
        """邻近峰PTMs匹配（修复类型转换问题）"""
        if neighbors.empty:
            return pd.DataFrame()

        # 显式类型转换
        target_mass = float(st.session_state.feature_state['selected_mass'])
        ppm_threshold = float(st.session_state.feature_state['ppm_threshold'])
        
        # 从feature_state获取参数
        target_mass = st.session_state.feature_state['selected_mass']
        ptms_rules = st.session_state.ptms_list
        ppm_threshold = st.session_state.feature_state['ppm_threshold']
        intensity_col = st.session_state.feature_state['intensity_col']
        # 新增同位素偏移量参数获取 (例如: [0, 1, -1, 2, -2])
        isotope_offsets = st.session_state.feature_state.get('isotope_offsets', [0, 1, -1])  # 默认值保持原有逻辑

        def find_closest_ptms(row):
            mass_diff = row['mass_diff']
            if mass_diff == 0:
                return ("Base Peak", 0, "")  # 修改标注为Base Peak
            
            best_ppm = float('inf')
            best_name = ""
            ppm_values = []

            delta_values = [offset * 1 for offset in isotope_offsets]
            for delta in delta_values:
                adjusted_diff = mass_diff + delta
                current_ppm = min(
                    (abs(adjusted_diff - ptm['mass_diff']) / target_mass * 1e6 for ptm in ptms_rules),
                    default=float('inf')
                )
                current_name = next(
                    (ptm['name'] for ptm in ptms_rules 
                     if abs(adjusted_diff - ptm['mass_diff']) / target_mass * 1e6 <= ppm_threshold),
                    ""
                )
                ppm_values.append(current_ppm)
                if current_ppm < best_ppm and current_name:
                    best_ppm = current_ppm
                    best_name = current_name

            best_index = np.argmin(ppm_values)
            correction_type = f"{isotope_offsets[best_index]:+}" if isotope_offsets[best_index] != 0 else "0"

            return (
                best_name if best_ppm <= ppm_threshold else "",
                min(ppm_values),  # 直接返回最小ppm值
                correction_type
            )

        # 修改结果列名
        results = neighbors.apply(find_closest_ptms, axis=1)
        neighbors[['PTMS Modification', 'ppm', 'Correction_Type']] = \
            pd.DataFrame(results.tolist(), index=neighbors.index)

        # 移除原有的相对强度计算代码
        # neighbors['Relative Intensity (%)'] = (neighbors[intensity_col] / max_intensity * 100).round(2)
        
        # 直接使用已生成的列
        if 'Relative Intensity (%)' not in neighbors.columns:
            neighbors['Relative Intensity (%)'] = 0  # 防止空值

        # 列名映射修正（匹配实际列名）
        display_columns = {
            st.session_state.feature_state["mass_col"]: 'Mass (Da)',
            'mass_diff': 'Delta Mass(Da)',
            'PTMS Modification': 'PTMS',
            'ppm': 'ppm',  # 直接使用ppm列
            'Correction_Type': 'Isotopic Shift(Da)',
            'Relative Intensity (%)': 'Relative Intensity(%)', 
            st.session_state.feature_state["feature_col"]: 'Feature ID'
        }

        valid_columns = [col for col in display_columns.keys() if col in neighbors.columns]
        neighbors_diff = neighbors[valid_columns].rename(columns=display_columns)

        mask = neighbors_diff['PTMS'] != ''
        neighbors_diff.loc[~mask, ['ppm', 'Isotopic Shift(Da)']] = ''  # 移除了'Min ppm'列
        
        neighbors_diff = neighbors_diff.replace('', np.nan)
        
        # 强制转换数值列类型（增加float精度控制）
        numeric_cols = ['ppm', 'Relative Intensity(%)']  # 移除了'Min ppm'列
        for col in numeric_cols:
            if col in neighbors_diff.columns:
                neighbors_diff[col] = pd.to_numeric(neighbors_diff[col], errors='coerce').round(2)  # 增加二次舍入

        return neighbors_diff

    def process_integration(self, df):
        """积分数据处理（添加显式类型转换）"""
        if df is None:
            return pd.DataFrame()

        # 显式类型转换
        time_range = [float(x) for x in st.session_state.feature_state['time_range']]
        mass_range = [float(x) for x in st.session_state.feature_state['mass_range']]
        
        try:
            time_mask = df[st.session_state.feature_state['time_col']].astype(float).between(*sorted(time_range))
            mass_mask = df[st.session_state.feature_state['mass_col']].astype(float).between(*sorted(mass_range))
            
            integrated = df[time_mask & mass_mask].groupby(
                df[st.session_state.feature_state['mass_col']].astype(float)
            ).agg({
                st.session_state.feature_state['intensity_col']: lambda x: pd.to_numeric(x, errors='coerce').sum(),
                st.session_state.feature_state['feature_col']: lambda x: list(x.astype(str).unique())
            }).reset_index()
            
            return integrated if not integrated.empty else None
        except Exception as e:
            st.error(f"数据处理失败: {str(e)}")
            return None
