import streamlit as st
import plotly.graph_objects as go

import numpy as np
import pandas as pd

import io
import os
from ..Widgets.PTMsCalculator import PTMsCalculator
from ..Widgets.ControlWidgets import ControlWidgets
from ..Widgets.CalculateWidgets import CalculateWidgets
from ..Widgets.FeatureLoader import FeatureLoader
from ..Widgets.PTMsWidget import PTMsWidget

from ..Widgets.PTMsCalculator import PTMsCalculator

class Featuremap():
    def __init__(self, locale: dict) -> None:
        """初始化Featuremap类，设置基础参数和本地化配置"""
        self._init_session_state() 
        # 保留基础状态初始化

        column_map = {
            'feature': ['Feature_ID', 'Feature ID'],
            'mass': ['Monoisotopic_mass','Mass', 'Precursor_mz'],
            'start_time':['Start_time', 'Min_time'],
            'end_time':['End_time', 'Max_time'],
            'time': ['Apex_time', 'Retention_time', 'RT'],
            'intensity': ['Intensity', 'Height', 'Area']
        }
        #------对类进行实例化
        self.locale = locale
        self.control = ControlWidgets(locale)
        self.calculate = CalculateWidgets()
        self.loader=FeatureLoader(column_map,locale)
        self.PTMs=PTMsWidget(locale)
        self.PTMsCalculator = PTMsCalculator()  # Add unique key

    def _init_session_state(self):
        """Initialize all required session state variables"""
        if 'feature_state' not in st.session_state:
            st.session_state.feature_state = {
                # Basic visualization settings
                'view_type': '2D',
                'log_scale': 'log10',
                'binx': 100,
                'biny': 100,
                'data_limit': 1000,
                'data_ascend': False,
                # Integration ranges
                'time_range': None,
                'mass_range': None,
                # Comparison mode
                'compare_mode': False,
                'sample1_color': "#0000FF",
                'sample2_color': "#FF0000",
                # PTMs analysis
                'selected_mass': None,
                'neighbor_range': 200.0,
                'neighbour_limit': 3.00,
                'ptms_list': [{"mass_diff": 15.994915, "name": "Oxidation"},
                              {"mass_diff": 42.010565, "name": "Acetylation"}],
                'ppm_threshold': 2,
                # Data columns
                'mass_col': None,
                'time_col': None,
                'intensity_col': 'Intensity',
                'mass_col2': None,
                'time_col2': None,
                'intensity_col2': None,
                'isotope_offsets':[0],
            }

        # Initialize color config if missing
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

    def run(self) -> None:
        """运行页面主逻辑"""
        self.showpage()

    @st.fragment()
    def showpage(self):  
        header_text = self.locale.get("ms1_featuremap_header", "**MS1 Featuremap**")
        st.markdown(header_text)
        if self.loader.load_data():
            featuremap_caption = self.locale.get("featuremap_caption", " :material/star: featrureMap:** 展示特征的时间和质量分布! 请在图中进行框选以进行下一步!")
            st.markdown(f'<div style="color:gray; font-size:1.1em">{featuremap_caption}</div>', unsafe_allow_html=True)
            with st.container(border=True):
                self.control.featuremap_widgets()
                self._plot_heatmap()
            
            # 本地化积分说明
            integration_caption = self.locale.get("integration_caption", " :material/star: **2.Integratation:** 对Featuremap进行积分，得到指定范围的质谱图,请在图中框选以进行下一步!")
            st.markdown(f'<div style="color:gray; font-size:1.1em">{integration_caption}</div>', unsafe_allow_html=True)
            with st.container(border=True):
                # 从session_state获取范围状态
                if st.session_state.feature_state.get('time_range') and st.session_state.feature_state.get('mass_range'):
                    self.control.integrate_widget()
                    integrated_data = self.calculate.process_integration(self.loader.load_feature_data(st.session_state['user_select_file'], st.session_state['sample']))
                    # 将选中质量存储到session_state
                    st.session_state.feature_state['selected_mass'] = self._plot_spectrum(integrated_data)
            # 本地化PTMs说明
            ptms_caption = self.locale.get("ptms_caption", " :material/star: **3.PTMs:** 对选定范围内最强的峰进行PTMs匹配!")
            st.markdown(f'<div style="color:gray; font-size:1.1em">{ptms_caption}</div>', unsafe_allow_html=True)
            with st.container(border=True):

                if st.session_state.feature_state.get('selected_mass'):
                    self.PTMs.near_peak_widget(integrated_data)

                    with st.expander("**PTMs Calculator**", expanded=False):
                        self.PTMsCalculator.PTMsCalculator()

                    self.PTMs.PTMs_DIY()  

                    # 添加选中质量状态追踪
                    # 修改匹配条件检测逻辑
                    current_selected_mass = st.session_state.feature_state['selected_mass']
                    last_selected_mass = st.session_state.feature_state.get('last_selected_mass')
                    
                    # 新增状态检测参数
                    current_isotope = st.session_state.feature_state.get('isotope_offsets', [])
                    last_isotope = st.session_state.feature_state.get('last_isotope_offsets', [])
                    
                    # 扩展匹配条件检测范围
                    match_condition = (
                        current_selected_mass != last_selected_mass or 
                        st.session_state.feature_state.get('ptms_updated', False) or
                        current_isotope != last_isotope  # 检测同位素偏移变化
                    )
                    
                    # 修改匹配条件区块
                    if match_condition:
                        neighbor = self.calculate.near_peak_process(integrated_data)  
                        self.neighbor_diff = self.calculate.near_peak_match(neighbor)
                        
                        # 增加状态变更检测
                        if not self.neighbor_diff.equals(st.session_state.feature_state.get('ptms_data', pd.DataFrame())):
                            st.session_state.feature_state['ptms_data'] = self.neighbor_diff.copy()
                            st.session_state.feature_state['last_isotope_offsets'] = current_isotope.copy()
                        
                        # 延后重置更新标记
                        st.session_state.feature_state['ptms_updated'] = False
                    
                    # 修改同步回调
                    def sync_state():
                        if not hasattr(self, '_last_sync'):
                            self._last_sync = None
                        
                        # 添加变化检测
                        current = st.session_state.feature_state['isotope_offsets']
                        if current != self._last_sync:
                            st.session_state.feature_state['ptms_updated'] = True
                            self._last_sync = current.copy()
                    
                    # 对比样本处理同样添加状态追踪
                    if st.session_state.feature_state["compare_mode"] and st.session_state.get('sample2'):
                        sample2_df = self.loader.load_feature_data2(st.session_state['user_select_file2'], st.session_state['sample2'])
                        sample2_integrated = self.calculate.process_integration(sample2_df)
                        
                        # 对比样本选中质量变化检测
                        current_selected_mass2 = st.session_state.feature_state.get('selected_mass')
                        last_selected_mass2 = st.session_state.feature_state.get('last_selected_mass2')
                        
                        if current_selected_mass2 != last_selected_mass2:
                            sample2_neighbor = self.calculate.near_peak_process(sample2_integrated)
                            self.sample2_neighbor_diff = self.calculate.near_peak_match(sample2_neighbor)
                            st.session_state.feature_state['ptms_data2'] = self.sample2_neighbor_diff.copy()
                            st.session_state.feature_state['last_selected_mass2'] = current_selected_mass2

                    # 确保数据框始终存在（即使从未匹配过）
                    if 'ptms_data' not in st.session_state.feature_state:
                        st.session_state.feature_state['ptms_data'] = pd.DataFrame()
                    if 'ptms_data2' not in st.session_state.feature_state:
                        st.session_state.feature_state['ptms_data2'] = pd.DataFrame()

                    if st.session_state.feature_state["compare_mode"] and not self.sample2_neighbor_diff.empty:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(self.locale.get("main_sample_ptms", "**主样本PTMs匹配结果**"))
                            edited_main = st.data_editor(
                                st.session_state.feature_state['ptms_data'].fillna(''),
                                use_container_width=True,
                                hide_index=True,
                                column_config={  # 仅保留列类型配置，不限制可编辑性
                                    "PTMS": st.column_config.TextColumn(),
                                    "Mass (Da)": st.column_config.NumberColumn(),
                                    "select": st.column_config.CheckboxColumn(help="隐藏该PTM")
                                },
                                key="main_ptms_editor"  # 移除editable参数
                            )
                            if not edited_main.equals(st.session_state.feature_state['ptms_data']):
                                st.session_state.feature_state['ptms_data'] = edited_main
                                self.neighbor_diff = edited_main
                        with col2:
                            st.markdown(self.locale.get("compare_sample_ptms", "**对比样本PTMs匹配结果**"))
                            edited_compare = st.data_editor(
                                st.session_state.feature_state['ptms_data2'].fillna(''),
                                use_container_width=True,
                                hide_index=True,
                                column_config={  # 仅保留列类型配置，不限制可编辑性
                                    "PTMS": st.column_config.TextColumn(),
                                    "Mass (Da)": st.column_config.NumberColumn(),
                                    "select": st.column_config.CheckboxColumn(help="隐藏该PTM")
                                },
                                key="compare_ptms_editor"  # 移除editable参数
                            )
                            if not edited_compare.equals(st.session_state.feature_state['ptms_data2']):
                                st.session_state.feature_state['ptms_data2'] = edited_compare
                                self.sample2_neighbor_diff = edited_compare
                    else:
                        st.markdown(self.locale.get("single_sample_ptms", "**样本PTMs匹配结果**"))
                        edited_single = st.data_editor(
                            st.session_state.feature_state['ptms_data'].fillna(''),
                            use_container_width=True,
                            hide_index=True,
                            column_config={  # 仅保留列类型配置，不限制可编辑性
                                "PTMS": st.column_config.TextColumn(),
                                "Mass (Da)": st.column_config.NumberColumn(),
                                "select": st.column_config.CheckboxColumn(help="隐藏该PTM")
                            },
                            key="single_ptms_editor"  # 移除editable参数
                        )
                        if not edited_single.equals(st.session_state.feature_state['ptms_data']):
                            st.session_state.feature_state['ptms_data'] = edited_single
                            self.neighbor_diff = edited_single

                    # 添加状态同步装饰器
                    @st.fragment
                    def sync_state():
                        # 将session_state的值同步到类属性
                        #只有将self刷新了,整个组件才会独立刷新!!!
                        for key in st.session_state.feature_state:
                            if key in ['isotope_offsets', 'selected_mass']:  # 需要同步的关键参数
                                setattr(self, key, st.session_state.feature_state[key])
                        st.session_state.feature_state['ptms_updated'] = True  # 标记状态已更新

                    
                    
                    st.session_state.feature_state["isotope_offsets"] = st.multiselect(
                        self.locale.get("isotope_offsets_label", "select allowed isotope shifts"),
                        options=[0, 1, -1, 2, -2, 3, -3,+4,-4,+5,-5],
                        default=st.session_state.feature_state.get("isotope_offsets", [0, 1, -1]),
                        key='feature_state.isotope_offsets',
                        on_change=sync_state  # 添加状态同步回调
                    )

                    self.PTMs.request_feature_widget()

#-------------------绘图组件---------------------
    def _plot_heatmap(self):
        """支持双样本比对的3D/2D热图"""
        fig = go.Figure()
        state = st.session_state.feature_state
        
        # 通过FeatureLoader获取数据
        main_df = self.loader.load_feature_data(
            st.session_state['user_select_file'], 
            st.session_state['sample']
        )
        # 从session_state获取列名和参数配置
        sorted_df = main_df.sort_values(
            by=state['intensity_col'], 
            ascending=state['data_ascend']
        ).head(state['data_limit'])

        # 新增第二样本数据加载（通过FeatureLoader接口）
        if state['compare_mode'] and 'sample2' in st.session_state:
            sample2_df = self.loader.load_feature_data2(
                st.session_state['user_select_file2'],
                st.session_state['sample2']
            )
            sorted_sample2 = sample2_df.sort_values(
                by=state['intensity_col2'], 
                ascending=False
            ).head(state['data_limit'])

        # 通过配置获取可视化参数
        view_config = {
            'colorscale': st.session_state.color_config['color_scale'],
            'sample1_color': state['sample1_color'],
            'sample2_color': state['sample2_color'],
            'bin_size': (state['binx'], state['biny']),
            'log_scale': state['log_scale']
        }

        if state["view_type"] == '3D':

            x = sorted_df[state["time_col"]].values  # 确保使用state中的time_col
            y = sorted_df[state["mass_col"]].values    # 使用state中的mass_col
            z = self.calculate.apply_scale(sorted_df[state["intensity_col"]])  # 使用state中的intensity_col

            # 使用state中的分箱参数
            hist, xedges, yedges = np.histogram2d(x, y, 
                bins=(state['binx'], state['biny']), 
                weights=z)
            
            # 使用state中的颜色配置
            main_colorscale = (
                [[0, '#FFFFFF'], [1, state["sample1_color"]]] if state["compare_mode"]
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
            if state["compare_mode"] and 'sorted_sample2' in locals():
                hist2, xedges2, yedges2 = np.histogram2d(
                    sorted_sample2[state["time_col2"]].values,
                    sorted_sample2[state["mass_col2"]].values,
                    bins=(state['binx'], state['biny']),  # 修正：使用state中的分箱参数
                    weights=self.calculate.apply_scale(sorted_sample2[state['intensity_col2']])  # 修正：使用calculate实例的方法
                )
                fig.add_trace(go.Surface(
                    z=hist2.T,
                    x=xedges2,
                    y=yedges2,
                    colorscale=[[0, '#FFFFFF'], [1, state["sample2_color"]]],  # 白到样本2颜色的渐变
                    opacity=0.7,
                    showscale=False
                ))

        #二维绘制
        else:
            # 主样本绘制
            fig.add_trace(go.Bar(
                y=sorted_df[state["mass_col"]],  # 使用state中的mass_col
                x=sorted_df[state["end_time_col"]] - sorted_df[state["start_time_col"]],  # 使用state中的时间列
                base=sorted_df[state["start_time_col"]],  # 使用state中的start_time_col
                orientation='h',
                marker=dict(
                    color=state["sample1_color"] if state["compare_mode"] else self.calculate.apply_scale(sorted_df[state["intensity_col"]]),
                    colorscale=None if state["compare_mode"] else st.session_state.color_config['color_scale'],
                    opacity=0.5 if state["compare_mode"] else 0.3,
                    line=dict(width=0)
                ),
                hoverinfo='text',
                width=1.6,
                showlegend = False  
            ))

            # 第二样本绘制（仅在比较模式时）
            if state["compare_mode"] and 'sample2_df' in locals():
                fig.add_trace(go.Bar(
                    y=sorted_sample2[state["mass_col2"]],  # 改为state中的mass_col2
                    x=sorted_sample2[state["end_time_col2"]] - sorted_sample2[state["start_time_col2"]],  # 使用state中的时间列
                    base=sorted_sample2[state["start_time_col2"]],
                    orientation='h',
                    marker=dict(
                        color=state["sample2_color"],  # 直接使用state中的颜色配置
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

        # 处理选择事件
        if event_data.selection:
            try:
                # 直接获取第一个有效框选范围并添加5%边界缓冲
                box = next(b for b in event_data.selection.get('box', []) if b.get('xref') == 'x' and b.get('yref') == 'y')
                
                # 时间范围处理（x轴）
                time_min, time_max = sorted([box['x'][0], box['x'][1]])
                buffer = (time_max - time_min) * 0.05  # 5%边界缓冲
                time_range = (time_min - buffer, 
                                time_max + buffer)
                
                # 质量范围处理（y轴）
                mass_min, mass_max = sorted([box['y'][0], box['y'][1]])
                buffer = (mass_max - mass_min) * 0.05  # 5%边界缓冲
                mass_range = (mass_min - buffer,
                                mass_max + buffer)

                st.session_state.feature_state.update({
                    'time_range': time_range,
                    'mass_range': mass_range
                })
            except (StopIteration, KeyError, TypeError):
                pass  # 保持当前范围不重置
            except ValueError as e:
                # 获取本地化的错误提示
                error_text = self.locale.get("range_value_error", f"范围值错误: {str(e)}")
                st.error(error_text)


    def _plot_spectrum(self, data):
        if data is None:
            return
            
        state = st.session_state.feature_state
        
        # 使用state中的列名
        max_intensity = data[state['intensity_col']].max()
        data = data.assign(**{'Normalized Intensity': (data[state['intensity_col']] / max_intensity) * 100})

        fig = go.Figure()

        # 修改主样本颜色为单色，使用热图中设定的颜色
        fig.add_trace(go.Bar(
            x=data[state['mass_col']],
            y=data['Normalized Intensity'],
            marker=dict(
                color=state["sample1_color"],  # 使用热图中设定的主样本颜色
                opacity=0.7,
                line=dict(width=0)
            ),
            name="sample1",
            hoverinfo='x+y',
            showlegend=False 
        ))

        # 对比样本处理
        if state['compare_mode'] and st.session_state.get('sample2'):
            sample2_df = self.loader.load_feature_data2(
                st.session_state['user_select_file2'],
                st.session_state['sample2']
            )
            sample2_data = self.calculate.process_integration(sample2_df)
            
            if sample2_data is not None:
                sample2_max = sample2_data[state['intensity_col2']].max()
                sample2_data = sample2_data.assign(**{
                    'Normalized Intensity': (sample2_data[state['intensity_col2']] / sample2_max) * 100
                })
                
                # 修改对比样本颜色为热图中设定的对比颜色
                fig.add_trace(go.Bar(
                    x=sample2_data[state['mass_col2']],
                    y=-sample2_data['Normalized Intensity'],
                    marker=dict(
                        color=state["sample2_color"],  # 使用热图中设定的对比样本颜色
                        opacity=0.7,
                        line=dict(width=0)
                    ),
                    name=self.locale.get("compare_sample", "比对样本"),
                    hoverinfo='x+y',
                    showlegend=False
                ))

        fig.update_layout(
            xaxis_title=self.locale.get("spectrum_xaxis_title", "质量 (Da)"),
            yaxis_title=self.locale.get("spectrum_yaxis_title", "强度(%)"),
            title=self.locale.get("spectrum_title", '积分图'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hoverdistance=30,
            dragmode='pan' if st.session_state.feature_state["compare_mode"] else 'select',
        )

        # 根据对比模式调整布局
        if st.session_state.feature_state["compare_mode"]:
            fig.update_layout(
                yaxis=dict(
                    tickvals=np.arange(-100, 101, 10),  # 更细的y轴刻度
                    ticktext=[f"{abs(x)}" for x in np.arange(-100, 101, 10)],
                    range=[-110, 110],
                    tickmode='auto',
                    nticks=22,  # 期望的刻度数量
                    autorange=True,  # 支持自动缩放
                )
            )
            # 添加镜像分隔线
            fig.add_shape(
                type="line",
                x0=data[state["mass_col"]].min(),
                x1=data[state["mass_col"]].max(),
                y0=0,
                y1=0,
                line=dict(color="gray", width=2)
            )
        else:
            fig.update_layout(
                yaxis=dict(
                    tickvals=np.arange(0, 101, 10),  # 更细的y轴刻度
                    range=[0, 110],
                    tickmode='auto',
                    nticks=12,  # 期望的刻度数量
                    autorange=True,  # 支持自动缩放
                )
            )

        # 只在有选中质量时才添加邻近峰标注
        current_selected_mass = st.session_state.feature_state['selected_mass']  # 保存当前选中质量,避免状态被刷新!

        if current_selected_mass:
            # 使用session_state中的持久化数据（已包含表格编辑后的最新值）
            main_ptms_data = st.session_state.feature_state['ptms_data']  # 从session_state读取最新编辑数据
            sample2_ptms_data = st.session_state.feature_state['ptms_data2']  # 从session_state读取最新编辑数据

            # 生成主样本标注（使用main_ptms_data）
            annotations = []
            if not main_ptms_data.empty:
                for _, row in main_ptms_data.iterrows():
                    # 添加有效性检查
                    if pd.notna(row['PTMS']) and row['PTMS'].strip() != '' \
                        and pd.notna(row['Mass (Da)']) \
                        and pd.notna(row.get('Relative Intensity(%)', 0)):
                        
                        mass_value = row['Mass (Da)']
                        intensity_value = row.get('Relative Intensity(%)', 0)
                        
                        # 添加数值有效性验证
                        if not np.isfinite(mass_value) or not np.isfinite(intensity_value):
                            continue
                            
                        annotations.append(
                            dict(
                                x=mass_value,
                                y=intensity_value,
                                text=f"<b>{row['PTMS']}</b>",
                                showarrow=True,
                                arrowhead=2,
                                arrowsize=1,
                                font=dict(size=16),
                                ax=0,
                                ay=-40,
                                bgcolor="rgba(173,216,230,0.3)",
                                bordercolor="rgba(200,200,200,0.2)"
                            )
                        )

            # 生成对比样本标注（添加相同的校验逻辑）
            sample2_annotations = []
            if state["compare_mode"] and not sample2_ptms_data.empty:
                for _, row in sample2_ptms_data.iterrows():
                    if pd.notna(row['PTMS']) and row['PTMS'].strip() != '' \
                        and pd.notna(row['Mass (Da)']) \
                        and pd.notna(row.get('Relative Intensity(%)', 0)):
                        
                        mass_value = row['Mass (Da)']
                        intensity_value = -row.get('Relative Intensity(%)', 0)
                        
                        if not np.isfinite(mass_value) or not np.isfinite(intensity_value):
                            continue
                            
                        sample2_annotations.append(
                            dict(
                                x=mass_value,
                                y=intensity_value,
                                text=f"<b>{row['PTMS']}</b>",
                                showarrow=True,
                                arrowhead=2,
                                arrowsize=1,
                                font=dict(size=16),
                                ax=0,
                                ay=40,
                                bgcolor="rgba(255,0,0,0.3)",
                                bordercolor="rgba(200,0,0,0.2)"
                            )
                        )
            fig.update_layout(annotations=annotations + sample2_annotations)

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
                ],
                'scrollZoom': True,  # 支持滚轮缩放
                'displayModeBar': True,
                'modeBarButtonsToAdd': ['autoScale2d']  # 增加自动缩放按钮
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
                
                mask = data[state["mass_col"]].between(mass_min, mass_max)
                selected_data = data[mask]
                if not selected_data.empty:
                    # 将选中质量存入session_state
                    st.session_state.feature_state['selected_mass'] = selected_data.loc[
                        selected_data['Normalized Intensity'].idxmax(), 
                        state["mass_col"]
                    ]
                else:
                    warning_text = self.locale.get("no_valid_data_warning", "选择范围内无有效数据")
                    st.warning(warning_text)
                    return current_selected_mass
                return st.session_state.feature_state['selected_mass']  # 返回session状态
            
            except (StopIteration, KeyError):
                return current_selected_mass

        # 返回当前session状态中的选中质量
        return st.session_state.feature_state.get('selected_mass')

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

    @st.fragment
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
            key="export_featuremap_html")
