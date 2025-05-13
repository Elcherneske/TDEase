import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json
import uuid  # 为了确保PTMS不会被刷新掉
from ..Utils.FileUtils import FileUtils
import io
import os
#本地版本用来打开窗口进行查看
import tkinter as tk
from tkinter import filedialog



class Featuremap():
    def __init__(self, locale: dict) -> None:
        """初始化Featuremap类，设置基础参数和本地化配置"""
        # 作图初始化
        self.time_range: tuple[float, float] | None = None      # 积分时间范围
        self.mass_range: tuple[float, float] | None = None    # 积分质量范围 
        self.log_scale: str = 'None'      # 强度显示方式
        self.language: str = st.session_state.get('language', "zh")
        self.locale: dict = locale

        self.sample2_color = "#FF0000"
        self.sample1_color = "#0000FF"
        self.compare_mode = False

        if 'color_config' not in st.session_state:
            st.session_state.color_config = {
                'use_custom': False,
                'nodes': 3,
                'custom_colors': [
                    [0.0, "#FF0000"], 
                    [0.5, "#0000FF"], 
                    [1.0, "#00FF00"]
                ],
                'color_scale': [[0.00, "#FFFFFF"], [0.4, "#0000FF"], [0.5, "#FF0000"], [1.00, "#FF0000"]]
            }

        self.data_limit=1000
        self.data_ascend=False

        #数据读取列名初始化
        self.column_map = {
        'feature': ['Feature_ID', 'Feature ID'],
        'mass': ['Mass', 'Monoisotopic_mass', 'Precursor_mz'],
        'start_time':['Start_time', 'Min_time'],
        'end_time':['End_time', 'Max_time'],
        'time': ['Apex_time', 'Retention_time', 'RT'],
        'intensity': ['Intensity', 'Height', 'Area']
        }

        self.feature_col=None
        self.mass_col = None  # 实际质量列名
        self.start_time_col = None  # 实际起始时间列名
        self.end_time_col = None    # 实际结束时间列名
        self.time_col = None  # 实际时间列名
        self.intensity_col = None  # 实际强度列名

        self.mass_col2 = None  # 实际质量列名
        self.start_time_col2 = None  # 实际起始时间列名
        self.end_time_col2 = None    # 实际结束时间列名
        self.time_col2 = None  # 实际时间列名
        self.intensity_col2 = None  # 实际强度列名

        #PTMs匹配参数初始化
        self.selected_mass = None  # 存储用户选择的质量
        self.neighbor_range = 20  # 默认邻近峰质量范围
        self.neighbour_limit = 0  # 默认邻近峰强度阈值
        self.ptms = [{"mass_diff": 15.994915, "name": "氧化"},
                    {"mass_diff": 42.010565, "name": "乙酰化"}]  # 存储用户输入的PTMs
        self.ppm_threshold = 5.00
    


    def run(self) -> None:
        """运行页面主逻辑"""
        self.showpage()

    @st.fragment()
    def showpage(self):  
        header_text = self.locale.get("ms1_featuremap_header", "**MS1 Featuremap**")
        st.markdown(header_text)

        if self._load_data():

            featuremap_caption = self.locale.get("featuremap_caption", " :material/star: featrureMap:** 展示特征的时间和质量分布! 请在图中进行框选以进行下一步!")
            st.caption(featuremap_caption)
            with st.container(border=True):
                self._featuremap_widgets()
                self._plot_heatmap()
            
            # 本地化积分说明
            integration_caption = self.locale.get("integration_caption", " :material/star: **2.Integratation:** 对Featuremap进行积分，得到指定范围的质谱图,请在图中框选以进行下一步!")
            st.caption(integration_caption)
            with st.container(border=True):
                if self.time_range and self.mass_range:
                    self._integrate_widget()
                    integrated_data = self._process_integration(self._load_feature_data(st.session_state['user_select_file'], st.session_state['sample']))
                    self.selected_mass = self._plot_spectrum(integrated_data)
            
            # 本地化PTMs说明
            ptms_caption = self.locale.get("ptms_caption", " :material/star: **3.PTMs:** 对选定范围内最强的峰进行PTMs匹配!")
            st.caption(ptms_caption)
            with st.container(border=True):
                if self.selected_mass:
                    self._near_peak_widget(integrated_data)
                    self._PTMs_DIY()
                    neighbor = self._near_peak_process(self.selected_mass, integrated_data)
                    neighbor_diff = self._near_peak_match(self.selected_mass,neighbor)
                    # 本地化邻近峰标题
                    neighbor_display_text = self.locale.get("neighbor_display", "**邻近峰展示**:")
                    st.write(neighbor_display_text)
                    st.dataframe(neighbor_diff, use_container_width=True)
                    self._request_feature_widget()

#-------------------绘图组件---------------------
    def _plot_heatmap(self):
        """支持双样本比对的3D/2D热图"""
        fig = go.Figure()
        main_df = self._load_feature_data(st.session_state['user_select_file'], st.session_state['sample'])
        sorted_df = main_df.sort_values(by=self.intensity_col, ascending=self.data_ascend)
        sorted_df = sorted_df.head(self.data_limit)  # 限制数据量
        
        # 新增第二样本数据加载
        if self.compare_mode and st.session_state.get('sample2'):
            sample2_df = self._load_feature_data2(st.session_state['user_select_file2'], st.session_state['sample2'])
            sorted_sample2_temp = sample2_df.sort_values(by=self.intensity_col2, ascending=False)
            sorted_sample2 = sorted_sample2_temp.head(self.data_limit)  # 限制第二样本数据量
        
        if hasattr(self, 'view_type') and self.view_type == '3D':

            x = sorted_df[self.time_col].values
            y = sorted_df[self.mass_col].values
            z = self._apply_scale(sorted_df[self.intensity_col])
            
            # 使用histogram2d聚合数据
            hist, xedges, yedges = np.histogram2d(x, y, 
                bins=(self.binx, self.biny), 
                weights=z)
            
            # 主要样本的3D热图绘制
            main_colorscale = (
                [[0, '#FFFFFF'], [1, self.sample1_color]] if self.compare_mode 
                else st.session_state.color_config['color_scale']
            )

            fig = go.Figure(data=[go.Surface(
                z=hist.T,
                x=xedges,
                y=yedges,
                colorscale=main_colorscale,
                hoverinfo='skip',
                showscale=False
            )])
            
            # 3D坐标轴设置
            fig.update_layout(
                scene=dict(
                    xaxis_title='Retention Time',
                    yaxis_title='Mass (Da)', 
                    zaxis_title='Intensity',
                    camera=dict(eye=dict(x=1.5, y=1.5, z=0.5))
                ),
                margin=dict(l=0, r=0, b=0, t=30)
            )
            if self.compare_mode and 'sorted_sample2' in locals():
                hist2, xedges2, yedges2 = np.histogram2d(
                    sorted_sample2[self.time_col2].values,
                    sorted_sample2[self.mass_col2].values,
                    bins=(self.binx, self.biny),
                    weights=self._apply_scale(sorted_sample2[self.intensity_col2])
                )
                fig.add_trace(go.Surface(
                    z=hist2.T,
                    x=xedges2,
                    y=yedges2,
                    colorscale=[[0, '#FFFFFF'], [1, self.sample2_color]],  # 白到样本2颜色的渐变
                    opacity=0.7,
                    showscale=False
                ))

        #二维绘制
        else:
            # 根据样本数量选择配色方案
            if self.compare_mode:
                # 使用固定颜色替代透明度渐变
                color1 = self.sample1_color
                color2 = self.sample2_color
            else:
                #单样本保持原有配色逻辑 
                marker_color = self._apply_scale(sorted_df[self.intensity_col])

            # 主样本绘制
            fig.add_trace(go.Bar(
                y=sorted_df[self.mass_col],
                x=sorted_df[self.end_time_col] - sorted_df[self.start_time_col],
                base=sorted_df[self.start_time_col],
                orientation='h',
                marker=dict(
                    color=color1 if self.compare_mode else marker_color,
                    colorscale=None if self.compare_mode else st.session_state.color_config['color_scale'],  # 比较模式关闭渐变
                    opacity=0.5 if self.compare_mode else 0.3,  # 使用固定透明度
                    line=dict(width=0)
                ),

                hoverinfo='text',
                width=1.6,
                showlegend = False  
            ))

            # 第二样本绘制（仅在比较模式时）
            if self.compare_mode and 'sample2_df' in locals():
                fig.add_trace(go.Bar(
                    y=sorted_sample2[self.mass_col2],
                    x=sorted_sample2[self.end_time_col2] - sorted_sample2[self.start_time_col2],
                    base=sorted_sample2[self.start_time_col2],
                    orientation='h',
                    marker=dict(
                        color=color2,  # 直接使用颜色值
                        opacity=0.5,  # 固定透明度
                        line=dict(width=0)
                    ),
                    showlegend=False,  # 移除图例标注
                    width=1.6
                ))

            # 获取本地化的轴标题和图表标题
            xaxis_title = self.locale.get("heatmap_xaxis_title", "Retention Time Range")
            yaxis_title = self.locale.get("heatmap_yaxis_title", "Mass (Da)")
            title = self.locale.get("heatmap_title", "Feature Heatmap")

            # Axis formatting
            fig.update_layout(
                xaxis_title=xaxis_title,
                yaxis_title=yaxis_title,
                bargap=0.1,
                title=title,
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.2)',
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.2)'
                ),
                hovermode='closest',
            )
            fig.update_layout(
                dragmode='select',  
            )

        event_data = st.plotly_chart(fig, 
            key="feature_heatmap" ,  # 添加唯一标识
            on_select="rerun",
            use_container_width=True,
            theme="streamlit",
            config={
                'modeBarButtonsToRemove': [
                    'toImage',          # 移除截图按钮
                    'lasso2d',   
                    'plotlyLogo'      # 移除套索选择
                ],
                'displayModeBar': True  # 保持工具栏可见
            })
            
        # 新增导出按钮（放在图表渲染之后）
        col1, col2 = st.columns([1, 3])
        with col1:
            self._export_featuremap_html(fig)

        # 获取本地化的文本和链接提示
        # 本地化exbasy相关提示文本
        exbasy_text = self.locale.get("exbasy_text", "📃可以使用exbasy工具来计算您目标蛋白的大致位置")
        exbasy_button_label = self.locale.get("exbasy_button_label", "exbasy:计算蛋白质精确质量")
        exbasy_tip = self.locale.get("exbasy_tip", "❗对于高分辨的质谱,需要在点击其中的Monoisotopic选项来计算")
        with col2:
            st.markdown(exbasy_text)
            st.link_button(label=exbasy_button_label, url="https://web.expasy.org/compute_pi/")
            st.markdown(exbasy_tip)

        # 处理选择事件
        if event_data.selection:
            try:
                # 直接获取第一个有效框选范围并添加5%边界缓冲
                box = next(b for b in event_data.selection.get('box', []) if b.get('xref') == 'x' and b.get('yref') == 'y')
                
                # 时间范围处理（x轴）
                time_min, time_max = sorted([box['x'][0], box['x'][1]])
                buffer = (time_max - time_min) * 0.05  # 5%边界缓冲
                self.time_range = (time_min - buffer, 
                                time_max + buffer)
                
                # 质量范围处理（y轴）
                mass_min, mass_max = sorted([box['y'][0], box['y'][1]])
                buffer = (mass_max - mass_min) * 0.05  # 5%边界缓冲
                self.mass_range = (mass_min - buffer,
                                mass_max + buffer)
                
            except (StopIteration, KeyError, TypeError):
                pass  # 保持当前范围不重置
            except ValueError as e:
                # 获取本地化的错误提示
                error_text = self.locale.get("range_value_error", f"范围值错误: {str(e)}")
                st.error(error_text)

    def _plot_spectrum(self, data):
        if data is None:
            return
        
        # 主样本数据处理
        max_intensity = data[self.intensity_col].max()
        if max_intensity == 0:
            st.warning(self.locale.get("all_zero_intensity_warning", "所有强度值为零，无法进行归一化"))
            return
        
        data['Normalized Intensity'] = (data[self.intensity_col] / max_intensity) * 100

        # 第二样本数据处理
        sample2_data = None
        if self.compare_mode and st.session_state.get('sample2'):
            sample2_df = self._load_feature_data2(st.session_state['user_select_file2'], st.session_state['sample2'])
            sample2_data = self._process_integration(sample2_df)  # 使用统一的积分处理方法

            if sample2_data is not None and not sample2_data.empty:
                sample2_max = sample2_data[self.intensity_col].max()
                if sample2_max > 0:
                    sample2_data['Normalized Intensity'] = (sample2_data[self.intensity_col] / sample2_max) * 100


        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=data[self.mass_col],
            y=data['Normalized Intensity'],
            marker=dict(
                color=data['Normalized Intensity'],
                colorscale='Bluered',
            ),
            name="sample1",
            hoverinfo='x+y',
            showlegend=False 
        ))

        # 仅在比较模式时添加第二样本镜像
        if self.compare_mode and sample2_data is not None and not sample2_data.empty:
            fig.add_trace(go.Bar(
                x=sample2_data[self.mass_col],
                y=-sample2_data['Normalized Intensity'],  # 负值实现镜像
                marker=dict(
                    color=-sample2_data['Normalized Intensity'],
                    colorscale='Bluered',
                ),
                name=self.locale.get("compare_sample", "比对样本"),
                hoverinfo='x+y',
                showlegend=False  # 隐藏图例
            ))

        fig.update_layout(
            xaxis_title=self.locale.get("spectrum_xaxis_title", "质量 (Da)"),
            yaxis_title=self.locale.get("spectrum_yaxis_title", "强度(%)"),
            title=self.locale.get("spectrum_title", '积分图'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hoverdistance=30,
            dragmode='pan' if self.compare_mode else 'select',
        )

        # 根据对比模式调整布局
        if self.compare_mode:
            fig.update_layout(
                yaxis=dict(
                    tickvals=np.arange(-100, 101, 20),
                    ticktext=[f"{abs(x)}" for x in np.arange(-100, 101, 20)],
                    range=[-110, 110]
                )
            )
            # 添加镜像分隔线
            fig.add_shape(
                type="line",
                x0=data[self.mass_col].min(),
                x1=data[self.mass_col].max(),
                y0=0,
                y1=0,
                line=dict(color="gray", width=2)
            )
        else:
            fig.update_layout(
                yaxis=dict(
                    tickvals=np.arange(0, 101, 20),
                    range=[0, 110]
                )
            )


        # 只在有选中质量时才添加邻近峰标注
        current_selected_mass = self.selected_mass  # 保存当前选中质量,避免状态被刷新!

        if current_selected_mass:
            neighbor = self._near_peak_process(current_selected_mass, data)
            neighbor_diff = self._near_peak_match(current_selected_mass,neighbor)
            annotations = []
            # Add null check before using .empty
            if neighbor_diff is not None and not neighbor_diff.empty:  # <-- Fix here
                for _, row in neighbor_diff.iterrows():
                    if abs(row['Mass Diff (Da)']) < 1e-6:
                        continue
                    
                    if row['PTMS Modification']:
                        # Use the actual mass column name stored in self.mass_col
                        mass_value = row[self.mass_col] if self.mass_col in row else row['Mass (Da)']
                        # Check if normalized intensity column exists
                        intensity_value = row.get('Normalized Intensity', row.get(self.intensity_col, 0)) + 2
                        
                        text = (f"<b>{row.get('PTMS Modification', '')}</b><br>")
                        annotations.append(
                            dict(
                                x=mass_value,
                                y=intensity_value,
                                text=text,
                                showarrow=True,
                                arrowhead=2,
                                arrowsize=1,
                                ax=0,
                                ay=-50,
                                bgcolor="rgba(173,216,230,0.9)",
                                bordercolor="rgba(200,200,200,0.8)",
                                borderwidth=1,
                                font=dict(
                                    size=12,
                                    color="black"
                                ),
                                xanchor='center',
                                yanchor='middle'
                            )
                        )
                fig.update_layout(annotations=annotations)

        # 渲染图表
        event_data = st.plotly_chart(fig, 
            use_container_width=True, 
            key="spectrum",
            on_select="rerun",
            theme="streamlit",
            config={
                'modeBarButtonsToRemove': [
                    'toImage', 
                    'lasso2d',
                    'plotlyLogo'
                ]+ 
                (['select2d'] if self.compare_mode else []),  # 比较模式额外移除选择按钮
            }
        )
        col1, col2 = st.columns([1, 3])
        with col1:
            self._export_spectrum_html(fig)

        # 处理选择事件
        if event_data.selection:
            try:
                box = next(b for b in event_data.selection.get('box', []) if b.get('xref') == 'x')
                mass_min, mass_max = sorted([box['x'][0], box['x'][1]])
                
                mask = data[self.mass_col].between(mass_min, mass_max)
                selected_data = data[mask]
                if not selected_data.empty:
                    self.selected_mass = selected_data.loc[selected_data['Normalized Intensity'].idxmax(), self.mass_col]
                else:
                    # 获取本地化的警告提示
                    warning_text = self.locale.get("no_valid_data_warning", "选择范围内无有效数据")
                    st.warning(warning_text)
                    return current_selected_mass  # 返回之前保存的值
                return self.selected_mass
            
            except (StopIteration, KeyError):
                return current_selected_mass  # 异常时返回之前保存的值

        # 如果没有选择事件，保持当前选中质量
        return current_selected_mass

    @st.fragment
    def _export_spectrum_html(self, fig):
        """HTML导出功能组件"""
        # 获取本地化的按钮标签
        button_label = self.locale.get("export_spectrum_button_label", "💾 导出交互式积分图")
        st.download_button(
            label=button_label,
            data=io.BytesIO(fig.to_html(
                include_plotlyjs="cdn",
                full_html=True
            ).encode('utf-8')).getvalue(),
            file_name="integrated_spectrum.html",
            mime="text/html",
            key="export_spectrum_html"
        )

    def _export_featuremap_html(self, fig):
        """HTML导出功能组件"""
        # 获取本地化的按钮标签
        button_label = self.locale.get("export_featuremap_button_label", "💾 导出交互式Featuremap")
        st.download_button(
            label=button_label,
            data=io.BytesIO(fig.to_html(
                include_plotlyjs="cdn",
                full_html=True
            ).encode('utf-8')).getvalue(),   
            file_name="featuremap.html",
            mime="text/html",
            key="export_featuremap_html"
        )

    def _near_peak_match(self, selected_mass, neighbors):
        """
        根据widget所给出的参数,进行临近峰的展示
        Args:
            neighbors (DataFrame): 筛选后的邻近峰数据
            selected_mass (float): 当前选中的峰的质量
        """
        # 合并PTMS匹配逻辑到展示方法
        if not neighbors.empty and self.ptms:
            # 定义内部匹配函数
            def find_closest_ptms(row):
                mass_diff = abs(row['mass_diff'])
                if mass_diff == 0:
                    return ("", float('inf'))
                
                ppm_values = [
                    (ptm['name'], abs(abs(mass_diff) - abs(ptm['mass_diff'])) / self.selected_mass * 1e6)
                    for ptm in self.ptms
                ]
                best_match = min(ppm_values, key=lambda x: x[1]) if ppm_values else ("", float('inf'))
                # 新增阈值判断：仅当ppm低于阈值时显示修饰名称
                return (best_match[0], best_match[1]) if best_match[1] <= self.ppm_threshold else ("", best_match[1])

            # 执行匹配计算
            results = neighbors.apply(find_closest_ptms, axis=1)
            neighbors[['PTMS Modification', 'Match(ppm)']] = pd.DataFrame(results.tolist(), index=neighbors.index)
            neighbors['Match(ppm)'] = neighbors['Match(ppm)'].round(2)

        if not neighbors.empty and not pd.isna(selected_mass):
            if selected_mass in neighbors[self.mass_col].values:
                base_intensity = neighbors.loc[neighbors[self.mass_col] == selected_mass, self.intensity_col].iloc[0]
                neighbors['Relative Intensity (%)'] = (neighbors[self.intensity_col] / base_intensity * 100).round(2)
            else:
                neighbors['Relative Intensity (%)'] = 0.00


        # 显示处理后的数据
        if not neighbors.empty and self.mass_col and self.feature_col:
            display_columns = {
                self.mass_col: 'Mass (Da)',
                'mass_diff': 'Mass Diff (Da)',
                'PTMS Modification': 'PTMS Modification',
                'Match(ppm)': 'Match(ppm)',
                'Relative Intensity (%)': 'Relative Intensity (%)',  # 新增列
                self.feature_col: 'Feature ID'
            }

            # 确保列存在并格式化ppm
            valid_columns = [col for col in display_columns.keys() if col in neighbors.columns]
            neighbors_diff = neighbors[valid_columns].rename(columns=display_columns)
            neighbors_diff['Match(ppm)'] = neighbors_diff['Match(ppm)'].round(2)
            
            # 隐藏无PTMs匹配的ppm值
            neighbors_diff['Match(ppm)'] = neighbors_diff.apply(
                lambda row: f"{row['Match(ppm)']:.2f}" if row['PTMS Modification'] else '', 
                axis=1
            )
            
            return neighbors_diff

        else:
            # Return empty DataFrame instead of showing warning
            warning_text = self.locale.get("no_near_peaks_warning", "在指定范围内未找到邻近峰")
            st.warning(warning_text)
            return pd.DataFrame()  # <-- Return empty DataFrame
            
        # Add default return
        return pd.DataFrame()


    def _featuremap_widgets(self):
        """
        初始化并显示Featuremap相关的控件
        """

        expander_text = self.locale.get("heatmap_settings_expander", "**热力图基本设置**")

        with st.expander(expander_text):
            # 新增3D视图切换
            view_type_label = self.locale.get("view_type_label", "视图模式")
            self.view_type = st.selectbox(
                view_type_label,
                options=['2D', '3D'],
                index=0,
                key='view_type_selector'
            )
            selectbox_label = self.locale.get("intensity_process", "强度处理方式")
            self.log_scale = st.selectbox(
                selectbox_label,
                options=['log10','None', 'log2', 'ln','sqrt'],
                index=0
            )
            x_pixel_label = self.locale.get("x_pixel_label", "x 轴像素")
            self.binx=st.number_input(x_pixel_label, min_value=10,max_value=9999,value=100)
            y_pixel_label = self.locale.get("y_pixel_label", "y 轴像素")
            self.biny=st.number_input(y_pixel_label, min_value=10,max_value=9999,value=100)
            data_limit_label = self.locale.get("data_limit_label", "显示数据点数量")
            data_limit_help = self.locale.get("data_limit_help", "按照强度从高到低排序,显示最强的前n个点以清晰化其图像")
            self.data_limit = st.number_input(
                data_limit_label, 
                min_value=100, 
                max_value=9999, 
                value=1000,
                help=data_limit_help
            )
            data_ascend_label = self.locale.get("data_ascend_label", "逆序排布")
            self.data_ascend = st.checkbox(data_ascend_label, value=False)


        advanced_expander_text = self.locale.get("advanced_color_settings_expander", "**高级颜色设置**")

        with st.expander(advanced_expander_text):

            # 使用会话状态管理配色状态
            self.use_custom = st.checkbox(
                self.locale.get("custom_color_checkbox", "启用自定义配色"),  # 修正国际化标签
                value=st.session_state.color_config['use_custom'],
                key='use_custom_color'
            )
            st.session_state.color_config['use_custom'] = self.use_custom
            
            #用self.use_custom是为了避免复杂的状态调用
            if self.use_custom:
                # 增加颜色配置验证
                if not st.session_state.color_config['custom_colors'] or \
                len(st.session_state.color_config['custom_colors']) != st.session_state.color_config['nodes']:
                    st.session_state.color_config['custom_colgers'] = [
                        [i/(st.session_state.color_config['nodes']-1), "#FFFFFF"] 
                        for i in range(st.session_state.color_config['nodes'])
                    ]

                cols = st.columns([1,1,2])
                with cols[0]:
                    if st.button(self.locale.get("add_node_button","➕ 添加节点")) and st.session_state.color_config['nodes'] < 6:
                        st.session_state.color_config['nodes'] += 1
                        # 添加新节点时自动生成合理的位置
                        new_pos = min(1.0, st.session_state.color_config['custom_colors'][-1][0] + 0.2)
                        st.session_state.color_config['custom_colors'].append([new_pos, "#FFFFFF"])
                with cols[1]:
                    if st.button(self.locale.get("remove_node_button","➖ 减少节点")) and st.session_state.color_config['nodes'] > 2:
                        st.session_state.color_config['nodes'] -= 1
                        st.session_state.color_config['custom_colors'].pop()
                
                # 动态生成颜色选择器
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
                                min_value=0.0,
                                max_value=1.0,
                                value=st.session_state.color_config['custom_colors'][i][0],
                                step=0.01,
                                key=f"pos_{i}"
                            )
                        updated_colors.append([new_pos, new_color])
                
                st.session_state.color_config['custom_colors'] = updated_colors
                
                # 更新并排序颜色配置（使用最新的custom_colors）
                st.session_state.color_config['color_scale'] = [
                    [pos, color] for pos, color in sorted(
                        st.session_state.color_config['custom_colors'],
                        key=lambda x: x[0]
                    )
                ]
                
        # 新增多样本展示控制
        compare_expander_text = self.locale.get("compare_settings_expander", "**多样本展示设置**")
        with st.expander(compare_expander_text):
            self.compare_mode = st.checkbox(
                self.locale.get("compare_mode_checkbox", "启用多样本展示"),
                value=False,
                key='compare_mode_checkbox'
            )
            if self.compare_mode:

                #如果是用户从网页端进入,则根据用户的权限来进行数据的比对
                if st.session_state.authentication_role=='user':
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

                    if st.session_state.get('user_select_file2'):
                        st.session_state.sample2 = st.selectbox(
                            self.locale.get("sample2_selector", "选择比对样本"),
                            options=FileUtils.list_samples(st.session_state['user_select_file2']),
                            index=0,
                            key='sample2_selector'
                        )
                        self._load_data2()
                else:

                    if st.button(self.locale.get("selectFolder", "📁 Select Report Folder"), key="select_folder2"):
                        selected_dir = self._open_directory_dialog()
                        if selected_dir:
                            st.session_state["user_select_file2"] = selected_dir
                            # 选择比对样本
                    if st.session_state.get('user_select_file2'):
                        st.session_state.sample2 = st.selectbox(
                            "选择比对样本",
                            options=FileUtils.list_samples(st.session_state['user_select_file2']),
                            index=0,
                            key='sample2_selector'
                        )
                        self._load_data2()

                col1, col2 = st.columns(2)
                with col1:

                        self.sample1_color = st.color_picker(
                            self.locale.get("sample1_color_picker", "主样本颜色"),
                            value=self.sample1_color,
                            key='sample1_color_picker'
                        )
                with col2:
                        self.sample2_color = st.color_picker(
                            self.locale.get("sample2_color_picker", "对比样本颜色"), 
                            value=self.sample2_color,
                            key='sample2_color_picker'
                        )


    def _integrate_widget(self):
        """手动设置积分范围--小组件"""
        with st.container():
            # 获取本地化的展开器标题
            expander_title = self.locale.get("integration_manual_settings_expander", "**积分范围手动设置**")
            checkbox_label = self.locale.get("integration_manual_checkbox", "手动设置积分范围")
            checkbox_help = self.locale.get("integration_manual_help", "如果您对于Featuremap的框选范围不满意,可以手动设置积分范围。框选后启用")
            # 质量范围和时间范围设置容器
            with st.expander(expander_title):
                manual=st.checkbox(checkbox_label, value=False, key='manual', help=checkbox_help)
                if manual:
                    df = self._load_feature_data(st.session_state['user_select_file'], st.session_state['sample'])
                    mass_min0 = float(df[self.mass_col].min())
                    mass_max0 = float(df[self.mass_col].max())

                    col1, col2 = st.columns(2)
                    with col1:
                        # 获取本地化的文本和标签
                        mass_range_text = self.locale.get("mass_range_text", "质量范围设置")
                        mass_max_label = self.locale.get("mass_max_label", "积分质量上界")
                        mass_min_label = self.locale.get("mass_min_label", "积分质量下界")
                        st.write(mass_range_text)
                        mass_min0 = float(df[self.mass_col].min())
                        mass_max0 = float(df[self.mass_col].max())
                        mass_max = st.number_input(mass_max_label, 
                            min_value=mass_min0, 
                            max_value=mass_max0, 
                            value=mass_max0,
                            key='mass_max')
                        mass_min = st.number_input(mass_min_label, 
                            min_value=mass_min0, 
                            max_value=mass_max0, 
                            value=mass_min0,
                            key='mass_min')
                        self.mass_range = (mass_min, mass_max)

                    # 时间范围设置列
                    with col2:
                        # 获取本地化的文本和标签
                        time_range_text = self.locale.get("time_range_text", "时间范围设置")
                        time_max_label = self.locale.get("time_max_label", "积分时间上界")
                        time_min_label = self.locale.get("time_min_label", "积分时间下界")
                        st.write(time_range_text)
                        time_min0 = float(df[self.time_col].min())
                        time_max0 = float(df[self.time_col].max())
                        time_max = st.number_input(time_max_label, 
                                                min_value=time_min0, 
                                                max_value=time_max0, 
                                                value=time_max0,
                                                key='time_max')
                        time_min = st.number_input(time_min_label, 
                                                min_value=time_min0, 
                                                max_value=time_max0, 
                                                value=time_min0,
                                                key='time_min')
                        self.time_range = (time_min, time_max)

    def _request_feature_widget(self):
        """
        根据featureid来给出prsm的链接信息!
        """
        # 获取本地化文本
        expander_title = self.locale.get("prsm_query_expander", "**Prsm查询**")
        input_label = self.locale.get("featureid_input_label", "输入您感兴趣的FeatureID")
        input_help = self.locale.get("featureid_input_help", '会返回一个带有链接的表格,E-value越小,置信度越高')
        button_label = self.locale.get("prsm_query_button", "查询")
        no_prsm_info_warning = self.locale.get("no_prsm_info_warning", "未找到相关PrSM信息")
        prsm_link_column = self.locale.get("prsm_link_column", "prsm链接")
        prsm_link_help = self.locale.get("prsm_link_help", "点击查看详细prsm信息")

        with st.expander(expander_title, expanded=True):
            featureid = st.number_input(input_label, step=1, key='neighbor_range', help=input_help)
            if st.button(button_label):
                prsmid = self._get_prsm_id(featureid)
                
                if prsmid.empty:
                    st.warning(no_prsm_info_warning)
                    return
                
                st.dataframe(
                    prsmid[['URL', 'E-value']],
                    column_config={
                        "URL": st.column_config.LinkColumn(
                            prsm_link_column,
                            help=prsm_link_help,
                            validate="^http",
                            max_chars=100
                        ),
                        "E-value": st.column_config.NumberColumn(
                            format="%.2e",
                            disabled=True
                        )
                    },
                    hide_index=True,
                    use_container_width=True
                )

    def _near_peak_widget(self, data):
        """添加邻近峰筛选的控制功能"""
        # 获取本地化的展开器标题、标签和帮助文本
        expander_title = self.locale.get("near_peak_expander", " **邻近峰筛选:** 以框选区域强度最高的峰作为基准")
        manual_mass_label = self.locale.get("manual_mass_label", "手动设置目标质量 (Da)")
        current_peak_text = self.locale.get("current_peak_text", "当前选中峰的质量: ")
        neighbor_range_label = self.locale.get("neighbor_range_label", "质量范围 (±Da)")
        intensity_threshold_label = self.locale.get("intensity_threshold_label", "强度阈值控制(%)")
        intensity_threshold_help = self.locale.get("intensity_threshold_help", "是为修饰邻近峰的阈值,单位为%。如果该峰的强度低于该阈值,则不会被视为邻近峰。")
        help_text = self.locale.get("near_peak_help", "峰之间的距离可以体现其PTMs信息")
        unimod_text = self.locale.get("unimod_text", "可以在下方的unimod中进行查询")
        unimod_button_label = self.locale.get("unimod_button_label", "PTMs数据库:unimod")
        with st.expander(expander_title):
            # 添加主峰和邻近峰标注
            col1, col2 = st.columns(2)
            with col1:
                # 添加手动输入质量功能
                if not data.empty:
                    current_min = float(data[self.mass_col].min())
                    current_max = float(data[self.mass_col].max())
                    clamped_value = min(max(float(self.selected_mass), current_min), current_max)
                    manual_mass = st.number_input(
                        manual_mass_label,
                        min_value=current_min,
                        max_value=current_max,
                        value=clamped_value,
                        key="manual_mass"
                    )
                    if manual_mass:
                        self.selected_mass = manual_mass
                    st.caption(f"{current_peak_text}{self.selected_mass:.4f} Da")

                self.neighbor_range = st.number_input(
                    neighbor_range_label,
                    min_value=0.1,
                    max_value=10000.0,
                    value=500.0,
                    step=0.1
                )
                self.neighbour_limit = st.number_input(
                    intensity_threshold_label,
                    min_value=0.00,
                    value=1.00,
                    max_value=100.00,
                    step=0.01,
                    help=intensity_threshold_help
                )
            
            with col2:
                st.markdown(help_text)
                st.markdown(unimod_text)
                st.link_button(label=unimod_button_label, url="https://www.unimod.org/modifications_list.php?")

    def _PTMs_DIY(self):
        """自定义PTMs质量差匹配规则"""
        # 初始化时从self.ptms同步到session_state
        if 'ptms_list' not in st.session_state:
            st.session_state.ptms_list = [{'uuid': str(uuid.uuid4()), **item} for item in self.ptms]
            
        # 获取本地化的展开器标题、按钮标签、输入标签和错误提示
        expander_title = self.locale.get("custom_ptms_expander", "**自定义PTMs匹配库**")
        add_button_label = self.locale.get("add_ptms_button", "➕ 添加PTMs规则")
        add_button_help = self.locale.get("add_ptms_help", "可以自定义修饰类型,比如将修饰进行组合后再查询")
        del_button_label = self.locale.get("del_ptms_button", "➖ 删除选中项")
        mass_diff_label = self.locale.get("mass_diff_label", "Mass Diff(Da)")
        ptms_type_label = self.locale.get("ptms_type_label", "PTMs Type")
        batch_input_button = self.locale.get("batch_input_button", "批量输入")
        parse_error = self.locale.get("parse_error", "解析失败: {0}，请确保输入格式为合法JSON数组")
        correct_format =  '''正确输入格式:[{"mass_diff": 15.9949, "name": "氧化"}, 
{"mass_diff": 74.02100, "name": "乙酰化"}]'''
        ppm_threshold_label = self.locale.get("ppm_threshold_label", "匹配精度阈值 (ppm)")
        ppm_threshold_help = self.locale.get("ppm_threshold_help", "若精度高于该阈值,则认为超出质谱精度容忍范围,无匹配的修饰")
        with st.expander(expander_title):
            # 在session_state中初始化PTMs存储
            if 'ptms_list' not in st.session_state:
                st.session_state.ptms_list = [{'uuid': str(uuid.uuid4()), **item} for item in self.ptms]
            col_add, col_del, _ = st.columns([1,1,3])
            with col_add:
                if st.button(add_button_label, help=add_button_help) and len(st.session_state.ptms_list) < 10:
                    st.session_state.ptms_list.append({"mass_diff": 0.0, "name": "", "uuid": str(uuid.uuid4())})
            with col_del:
                if st.button(del_button_label) and len(st.session_state.ptms_list) > 1:
                    # 通过checkbox选择要删除的项
                    selected_indices = [i for i, item in enumerate(st.session_state.ptms_list) if st.session_state.get(f'del_{item["uuid"]}')]
                    for i in reversed(selected_indices):
                        del st.session_state.ptms_list[i]
            
            updated_entries = []
            for item in st.session_state.ptms_list:
                with st.container(border=True):
                    cols = st.columns([2, 2, 1])
                    with cols[0]:
                        new_mass = st.number_input(
                            mass_diff_label,
                            min_value=-1000.0,
                            value=item["mass_diff"],
                            step=0.00001,  # 步长缩小到1e-5
                            format="%.5f",  # 显示5位有效数字
                            key=f"ptms_mass_{item['uuid']}"
                        )
                    with cols[1]:
                        new_name = st.text_input(
                            ptms_type_label,
                            value=item["name"],
                            key=f"ptms_name_{item['uuid']}"
                        )
                    with cols[2]:
                        st.checkbox("delete", key=f"del_{item['uuid']}")
                updated_entries.append({"mass_diff": new_mass, "name": new_name, "uuid": item['uuid']})
            
            # 双向同步数据（session_state <-> self.ptms）
            st.session_state.ptms_list = updated_entries

            # 批量输入时直接操作self.ptms
            ptm_text = st.text_area(self.locale.get("batch_input_PTMs","批量输入PTMs规则"),value=correct_format,height=150,help=correct_format)
            if st.button(batch_input_button):
                try:
                    if ptm_text.strip():
                        new_ptms = json.loads(ptm_text)
                        # 转换所有mass_diff为float类型
                        for item in new_ptms:
                            item['mass_diff'] = float(item['mass_diff'])

                        st.session_state.ptms_list = [
                            {'uuid': str(uuid.uuid4()), **item} 
                            for item in new_ptms
                        ]
                    st.success("批量输入成功")
                except Exception as e:
                    st.error(parse_error.format(str(e)))
                    st.json(correct_format)

            self.ppm_threshold = st.select_slider(
                ppm_threshold_label,
                options=[2,5,10],
                help=ppm_threshold_help
            )

#----------------后端计算----------------

    def _apply_scale(self, series):
        """应用强度转换并归一化"""
        # 原始转换
        if self.log_scale == 'log2':
            scaled = np.log2(series + 1)
        elif self.log_scale == 'ln':
            scaled = np.log(series + 1)
        elif self.log_scale == 'sqrt':
            scaled = np.sqrt(series + 1)
        elif self.log_scale == 'log10':
            scaled = np.log10(series + 1)
        else:
            scaled = series.copy()

        # 归一化到0-1范围
        min_val = scaled.min()
        max_val = scaled.max()
        
        if max_val - min_val > 0:
            return (scaled - min_val) / (max_val - min_val)
        else:
            return scaled * 0  

    @st.cache_data
    def _load_feature_data(_self, selected_path, sample_name):    
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
    def _load_feature_data2(_self, selected_path, sample_name):    
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
    def _load_prsm_data(_self, selected_path, sample_name):
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


    def _load_data(self):
        """数据加载与校验（主方法）"""
        selected_path = st.session_state['user_select_file']
        sample_name = st.session_state['sample']
        
        df = self._load_feature_data(selected_path, sample_name)
        df2 = self._load_prsm_data(selected_path, sample_name)

        if df is None or df2 is None:
            return False

        # 列名映射（保持原有逻辑不变）
        self.mass_col = self._find_column(self.column_map['mass'],df)
        if self.mass_col:
            df[self.mass_col] = df[self.mass_col].astype(float)
            self.feature_col = self._find_column(self.column_map['feature'],df)
            self.time_col = self._find_column(self.column_map['time'],df)
            self.intensity_col = self._find_column(self.column_map['intensity'],df)
            self.start_time_col = self._find_column(self.column_map['start_time'],df)
            self.end_time_col = self._find_column(self.column_map['end_time'],df)

            if not all([self.mass_col, self.time_col, self.intensity_col, self.start_time_col, self.end_time_col]):
                missing = []
                if not self.mass_col: missing.append(f"mass ({', '.join(self.column_map['mass'])})")
                if not self.time_col: missing.append(f"time ({', '.join(self.column_map['time'])})")
                if not self.intensity_col: missing.append(f"intensity ({', '.join(self.column_map['intensity'])})")
                if not self.start_time_col: missing.append(f"start_time ({', '.join(self.column_map['start_time'])})")
                if not self.end_time_col: missing.append(f"end_time ({', '.join(self.column_map['end_time'])})")
                # 替换为本地化错误提示（支持缺失列格式化）
                error_text = self.locale.get("missing_required_columns", "❌ 缺少必要列: {0}").format(', '.join(missing))
                st.error(error_text)
                return False
        return True

    def _load_data2(self):
        """数据加载与校验（主方法）"""
        selected_path = st.session_state['user_select_file2']
        sample_name = st.session_state['sample2']

        df = self._load_feature_data2(selected_path, sample_name)

        self.mass_col2 = self._find_column(self.column_map['mass'],df)
        if self.mass_col2:
            df[self.mass_col2] = df[self.mass_col2].astype(float)
            self.time_col2 = self._find_column(self.column_map['time'],df)
            self.intensity_col2 = self._find_column(self.column_map['intensity'],df)
            self.start_time_col2 = self._find_column(self.column_map['start_time'],df)
            self.end_time_col2 = self._find_column(self.column_map['end_time'],df)

        return True


    def _find_column(self, candidates, df):
        """在数据框中查找候选列名"""
        # 修复：使用传入的df参数而非重新加载数据
        for col in candidates:
            if col in df.columns:
                return col
        return None

    def _near_peak_process(self, target_mass, data):
        """查找指定质量附近的邻近峰"""

        if data.empty or pd.isna(target_mass):
            return pd.DataFrame()
        # 获取邻近峰数据（±neighbor_range范围）
        mass_col = self.mass_col
        lower_bound = target_mass - self.neighbor_range
        upper_bound = target_mass + self.neighbor_range
        neighbors = data[
            (data[mass_col].between(lower_bound, upper_bound)) &
            (data["Normalized Intensity"] >= self.neighbour_limit) # 排除主峰
            ].copy()

        if neighbors.empty:
            return neighbors

        # 计算精确质量差（保留6位小数）
        neighbors["mass_diff"] = (neighbors[mass_col] - target_mass).round(6)
        
        # 按质量差差绝对值排序并截断结果
        return neighbors.sort_values("mass_diff")

    def _find_neighbors_in_sample(self, target_mass, data):
        """在单个样本中查找邻近峰"""
        mass_col = self.mass_col
        lower_bound = target_mass - self.neighbor_range
        upper_bound = target_mass + self.neighbor_range
        
        neighbors = data[
            (data[mass_col].between(lower_bound, upper_bound)) &
            (data["Normalized Intensity"] >= self.neighbour_limit)
        ].copy()
        
        if not neighbors.empty:
            neighbors["mass_diff"] = (neighbors[mass_col] - target_mass).round(6)
            neighbors['Sample'] = '主样本'  # 添加样本来源标识
        
        return neighbors

    def _get_prsm_id(self, ID):
        """根据featureID查询prsmID"""

        df2 = self._load_prsm_data(st.session_state['user_select_file'], st.session_state['sample'])
        if df2.empty:
            return pd.DataFrame()
        
        # 添加列名检查和类型转换
        feature_col = 'Feature ID' if 'Feature ID' in df2.columns else self.feature_col
        prsm_col = 'Prsm ID' if 'Prsm ID' in df2.columns else 'Prsm_ID'
        evalue_col = next((col for col in ['E-value', 'E_value', 'E Value'] if col in df2.columns), None)

        # 转换ID类型为与数据框一致
        try:
            matches = df2[df2[feature_col].astype(int) == int(ID)].copy()  
        except KeyError:
            return pd.DataFrame()

        if matches.empty:
            return pd.DataFrame()

        # 创建包含链接的DataFrame
        result_df = matches[[prsm_col, evalue_col]].copy() if evalue_col else matches[[prsm_col]].copy()  # 显式保留关键列
        result_df['URL'] = result_df[prsm_col].apply(
            lambda x: f"http://localhost:8000/topmsv/visual/prsm.html?folder=../../toppic_proteoform_cutoff/data_js&protein={x}"
        )


        if evalue_col:
            return result_df[['URL', evalue_col]].rename(columns={evalue_col: 'E-value'})
        return result_df[['URL']]
        
    # 计算所有PTMS规则的ppm值
    def find_closest_ptms(row):
        """
        pandas apply函数,是为一种操作规则
        """
        mass_diff = abs(row['mass_diff'])
        if mass_diff == 0:
            return ("", float('inf'))
        
        # 计算ppm：|Δm| / 目标质量 * 1e6
        ppm_values = [
            (ptm['name'], abs(abs(mass_diff) - abs(ptm['mass_diff'])) / target_mass * 1e6)
            for ptm in self.ptms
        ]
        # 找到ppm最小的修饰
        return min(ppm_values, key=lambda x: x[1]) if ppm_values else ("", float('inf'))

    def _process_integration(self,df):

        if df is None:  # 避免读取不到数据
            df = self._load_feature_data(st.session_state['user_select_file'], st.session_state['sample'])

        try:
            time_mask = df[self.time_col].between(*sorted(self.time_range))
            mass_mask = df[self.mass_col].between(*sorted(self.mass_range))
            integrated = df[time_mask & mass_mask].groupby(self.mass_col).agg({
                self.intensity_col: 'sum',
                self.feature_col: lambda x: list(x.unique())
            }).reset_index()
            if integrated.empty:
                # 替换为本地化警告提示
                warning_text = self.locale.get("integration_no_data_warning", "积分区间无有效数据，请调整范围设置")
                st.warning(warning_text)
                return None
            return integrated
            
        except Exception as e:
            st.error(f"数据处理失败: {str(e)}")
            return None
        


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
