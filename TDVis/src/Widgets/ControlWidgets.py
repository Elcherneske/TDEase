import streamlit as st
import tkinter as tk
from tkinter import filedialog
import uuid
import json
import os
from ..Utils.FileUtils import FileUtils  # Assuming FileUtils is in this path
from ..Widgets.FeatureLoader import FeatureLoader

class ControlWidgets:
    def __init__(self, locale: dict):
        self.locale = locale  # Accept localization dictionary
        column_map = {
            'feature': ['Feature_ID', 'Feature ID'],
            'mass': ['Monoisotopic_mass','Mass', 'Precursor_mz'],
            'start_time':['Start_time', 'Min_time'],
            'end_time':['End_time', 'Max_time'],
            'time': ['Apex_time', 'Retention_time', 'RT'],
            'intensity': ['Intensity', 'Height', 'Area']
        }
        self.FeatureLoader = FeatureLoader(column_map,locale)  # Initialize FeatureLoader with locale


    def featuremap_widgets(self):
        """Initialize and display Featuremap-related controls"""
        expander_text = self.locale.get("heatmap_settings_expander", "**热力图基本设置**")

        with st.expander(expander_text):
            # View type selector
            st.session_state.feature_state['view_type'] = st.selectbox(
                self.locale.get("view_type_label", "视图模式"),
                options=['2D', '3D'],
                index=0 if st.session_state.feature_state['view_type'] == '2D' else 1,
                key='view_type_selector'
            )

            # Intensity processing
            st.session_state.feature_state['log_scale'] = st.selectbox(
                self.locale.get("intensity_process", "强度处理方式"),
                options=['log10','None', 'log2', 'ln','sqrt'],
                index=['log10','None', 'log2', 'ln','sqrt'].index(st.session_state.feature_state['log_scale']),
                key='log_scale_selector'
            )

            # Pixel settings
            st.session_state.feature_state['binx'] = st.number_input(
                self.locale.get("x_pixel_label", "x 轴像素"),
                min_value=10, max_value=9999,
                value=st.session_state.feature_state['binx'],
                key='binx_input'
            )
            st.session_state.feature_state['biny'] = st.number_input(
                self.locale.get("y_pixel_label", "y 轴像素"),
                min_value=10, max_value=9999,
                value=st.session_state.feature_state['biny'],
                key='biny_input'
            )

            # Data limit controls
            st.session_state.feature_state['data_limit'] = st.number_input(
                self.locale.get("data_limit_label", "显示数据点数量"),
                min_value=100, max_value=9999,
                value=st.session_state.feature_state['data_limit'],
                help=self.locale.get("data_limit_help", "按照强度从高到低排序,显示最强的前n个点以清晰化其图像"),
                key='data_limit_input'
            )
            st.session_state.feature_state['data_ascend'] = st.checkbox(
                self.locale.get("data_ascend_label", "逆序排布"),
                value=st.session_state.feature_state['data_ascend'],
                key='data_ascend_checkbox'
            )

        # Advanced color settings (existing code with state fixes)
        advanced_expander_text = self.locale.get("advanced_color_settings_expander", "**高级颜色设置**")
        with st.expander(advanced_expander_text):
            self.use_custom = st.checkbox(
                self.locale.get("custom_color_checkbox", "启用自定义配色"),
                value=st.session_state.color_config['use_custom'],
                key='use_custom_color'
            )
            st.session_state.color_config['use_custom'] = self.use_custom
            
            if self.use_custom:
                # Fix typo: custom_colgers -> custom_colors
                if not st.session_state.color_config['custom_colors'] or \
                len(st.session_state.color_config['custom_colors']) != st.session_state.color_config['nodes']:
                    st.session_state.color_config['custom_colors'] = [
                        [i/(st.session_state.color_config['nodes']-1), "#FFFFFF"] 
                        for i in range(st.session_state.color_config['nodes'])
                    ]

                # Node management buttons (existing code)
                cols = st.columns([1,1,2])
                with cols[0]:
                    if st.button(self.locale.get("add_node_button","➕ 添加节点")) and st.session_state.color_config['nodes'] < 6:
                        st.session_state.color_config['nodes'] += 1
                        new_pos = min(1.0, st.session_state.color_config['custom_colors'][-1][0] + 0.2)
                        st.session_state.color_config['custom_colors'].append([new_pos, "#FFFFFF"])
                with cols[1]:
                    if st.button(self.locale.get("remove_node_button","➖ 减少节点")) and st.session_state.color_config['nodes'] > 2:
                        st.session_state.color_config['nodes'] -= 1
                        st.session_state.color_config['custom_colors'].pop()
                
                # Color pickers (existing code)
                updated_colors = []
                for i in range(st.session_state.color_config['nodes']):
                    with st.container(border=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            new_color = st.color_picker(
                                f"node {i+1} color",
                                value=st.session_state.color_config['custom_colors'][i][1],
                                key=f"color_{i}"
                            )
                        with col2:
                            new_pos = st.number_input(
                                f"node {i+1} position",
                                min_value=0.0, max_value=1.0,
                                value=st.session_state.color_config['custom_colors'][i][0],
                                step=0.01,
                                key=f"pos_{i}"
                            )
                        updated_colors.append([new_pos, new_color])
                
                st.session_state.color_config['custom_colors'] = updated_colors
                st.session_state.color_config['color_scale'] = [
                    [pos, color] for pos, color in sorted(updated_colors, key=lambda x: x[0])
                ]

        # Comparison mode controls (existing code with state fixes)
        compare_expander_text = self.locale.get("compare_settings_expander", "**多样本展示设置**")
        with st.expander(compare_expander_text):
            st.session_state.feature_state['compare_mode'] = st.checkbox(
                self.locale.get("compare_mode_checkbox", "启用多样本展示"),
                value=st.session_state.feature_state['compare_mode'],
                key='compare_mode_checkbox'
            )
            if st.session_state.feature_state['compare_mode']:
                # File selection logic (existing code)
                if 'authentication_role' in st.session_state:
                    if st.session_state.authentication_role == 'user':
                        df = FileUtils.query_files(st.session_state.authentication_username)
                        if not df.empty:
                            df = df.drop_duplicates(subset=['文件名'])
                            df.index = df.index + 1
                            st.session_state['user_select_file2'] = st.selectbox(
                                self.locale.get("selectFolder", "📁 选择报告文件夹"),
                                df['文件名'],
                                index=None,
                                key="file_radio"
                            )
                    else:
                        if st.button(self.locale.get("selectFolder", "📁 Select Report Folder"), key="select_folder2"):
                            selected_dir = self._open_directory_dialog()
                            if selected_dir:
                                st.session_state["user_select_file2"] = selected_dir
                        if st.session_state.get('user_select_file2'):
                            st.session_state.sample2 = st.selectbox(
                                self.locale.get("sample2_selector", "选择对比样本"),
                                options=FileUtils.list_samples(st.session_state['user_select_file2']),
                                index=0,
                                key='sample2_selector'
                            )
                            # Assuming _load_data2 is implemented elsewhere
                            self.FeatureLoader.load_data2()
                else:
                    if st.button(self.locale.get("selectFolder", "📁 Select Report Folder"), key="select_folder2"):
                        selected_dir = self._open_directory_dialog()
                        if selected_dir:
                            st.session_state["user_select_file2"] = selected_dir
                    if st.session_state.get('user_select_file2'):
                        st.session_state.sample2 = st.selectbox(
                            self.locale.get("sample2_selector", "选择对比样本"),
                            options=FileUtils.list_samples(st.session_state['user_select_file2']),
                            index=0,
                            key='sample2_selector'
                        )
                        self.FeatureLoader.load_data2()

                # Color pickers
                col1, col2 = st.columns(2)
                with col1:
                    st.session_state.feature_state['sample1_color'] = st.color_picker(
                        self.locale.get("sample1_color_picker", "主样本颜色"),
                        value=st.session_state.feature_state['sample1_color'],
                        key='sample1_color_picker'
                    )
                with col2:
                    st.session_state.feature_state['sample2_color'] = st.color_picker(
                        self.locale.get("sample2_color_picker", "对比样本颜色"), 
                        value=st.session_state.feature_state['sample2_color'],
                        key='sample2_color_picker'
                    )

    def integrate_widget(self):
        """Manual integration range controls"""
        with st.container():
            expander_title = self.locale.get("integration_manual_settings_expander", "**积分范围手动设置**")
            checkbox_label = self.locale.get("integration_manual_checkbox", "手动设置积分范围")
            checkbox_help = self.locale.get("integration_manual_help", "如果您对于Featuremap的框选范围不满意,可以手动设置积分范围。框选后启用")
            
            with st.expander(expander_title):
                manual = st.checkbox(checkbox_label, value=False, key='manual', help=checkbox_help)
                if manual:
                    # Assuming _load_feature_data is implemented elsewhere
                    df = FeatureLoader.load_feature_data(self, st.session_state['user_select_file'], st.session_state['sample'])
                    mass_min0 = float(df[st.session_state.feature_state['mass_col']].min())
                    mass_max0 = float(df[st.session_state.feature_state['mass_col']].max())

                    col1, col2 = st.columns(2)
                    with col1:
                        # Mass range controls (existing code with state updates)
                        st.session_state.feature_state['mass_range'] = (
                            st.number_input(
                                self.locale.get("mass_min_label", "积分质量下界"),
                                min_value=mass_min0, max_value=mass_max0,
                                value=mass_min0,
                                format="%.6f",
                                key='mass_min'
                            ),
                            st.number_input(
                                self.locale.get("mass_max_label", "积分质量上界"),
                                min_value=mass_min0, max_value=mass_max0,
                                value=mass_max0,
                                format="%.6f",
                                key='mass_max'
                            )
                        )
                    with col2:
                        # Time range controls (existing code with state updates)
                        time_min0 = float(df[st.session_state.feature_state['time_col']].min())
                        time_max0 = float(df[st.session_state.feature_state['time_col']].max())
                        st.session_state.feature_state['time_range'] = (
                            st.number_input(
                                self.locale.get("time_min_label", "积分时间下界"),
                                min_value=time_min0, max_value=time_max0,
                                value=time_min0,
                                format="%.6f",
                                key='time_min'
                            ),
                            st.number_input(
                                self.locale.get("time_max_label", "积分时间上界"),
                                min_value=time_min0, max_value=time_max0,
                                value=time_max0,
                                format="%.6f",
                                key='time_max'
                            )
                        )


    def _open_directory_dialog(self):
        """Open system directory dialog using Tkinter"""
        import tkinter as tk
        from tkinter import filedialog
        
        root = tk.Tk()
        root.wm_attributes('-topmost', 1)  # Add this line
        root.withdraw()
        
        # Force focus on the dialog
        root.update_idletasks()
        folder_path = filedialog.askdirectory(parent=root)
        
        # Cleanup
        root.destroy()
        
        return os.path.normpath(folder_path) if folder_path else None

