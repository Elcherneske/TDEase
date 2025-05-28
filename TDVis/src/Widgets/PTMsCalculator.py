import streamlit as st
from pyteomics import mass
import itertools
import json

class PTMsCalculator:

    @st.fragment
    def PTMsCalculator(self):  # Add self parameter here
        ptm_entries = []
        for i in range(5):
            if i == 0 or f"ptm_{i-1}_filled" in st.session_state:
                with st.container(border=True):
                    cols = st.columns([1, 2, 1])
                    with cols[0]:
                        name = st.text_input(f"PTMs Name {i+1}", key=f"name_{i}")
                    with cols[1]:
                        formula = st.text_input(f"Chemical Formula {i+1}", key=f"formula_{i}", 
                                            help="Such As: C6H12O6-H2O (Must be Uppercase Characters),or a correct float number")
                    with cols[2]:
                        count = st.number_input(f"Max Amount", min_value=1, value=1, 
                                            key=f"count_{i}")
                    
                    # 修改后的验证逻辑
                    if formula:
                        try:
                            # 先尝试数字转换
                            try:
                                calc_mass = float(formula)
                            except ValueError:
                                # 不是数字则处理化学式
                                # 支持加法和减法混合运算
                                parts = []
                                current_part = ""
                                for char in formula:
                                    if char in ('+', '-'):
                                        if current_part:
                                            parts.append(current_part)
                                        parts.append(char)
                                        current_part = ""
                                    else:
                                        current_part += char
                                if current_part:
                                    parts.append(current_part)

                                calc_mass = mass.calculate_mass(formula=parts[0])
                                j = 1  # 修改变量名为j
                                while j < len(parts):
                                    operator = parts[j]
                                    sub_formula = parts[j + 1]
                                    if operator == '+':
                                        calc_mass += mass.calculate_mass(formula=sub_formula)
                                    elif operator == '-':
                                        calc_mass -= mass.calculate_mass(formula=sub_formula)
                                    j += 2  # 使用j代替i
                            st.caption(f"Single Mass: {calc_mass:.6f} Da")
                            st.session_state[f"ptm_{i}_filled"] = True
                        except Exception as e:
                            st.error("Invalid formula!!! e.g. C6H12O6-H2O (Must be Uppercase Characters),or a correct float number")
                            st.session_state.pop(f"ptm_{i}_filled", None)
                    else:
                        st.session_state.pop(f"ptm_{i}_filled", None)  # 空值时清除标记

        if st.button("Generate PTMs Configuration", type="primary"):
            valid_ptms = []
            for i in range(5):
                # 添加键存在性校验
                if not all(key in st.session_state for key in [f"formula_{i}", f"count_{i}", f"name_{i}"]):
                    continue  # 跳过未初始化的条目
                
                if st.session_state.get(f"ptm_{i}_filled"):
                    try:
                        # 使用get方法安全获取值
                        formula = st.session_state.get(f"formula_{i}", "")
                        count = st.session_state.get(f"count_{i}", 0)
                        name = st.session_state.get(f"name_{i}", "")
                        
                        # 增加空值校验
                        if not formula.strip() or not name.strip():
                            st.error(f" The formula of {i+1} item cannot be empty.")
                            return
                        

                        # 修改后的数字校验逻辑
                        try:
                            # 直接尝试转换为浮点数
                            mass_per = float(formula)
                            st.caption(f"Single Mass: {mass_per:.6f} Da")
                        except ValueError:
                            # 不是数字则按化学式计算（使用与输入验证相同的处理逻辑）
                            parts = []
                            current_part = ""
                            for char in formula:
                                if char in ('+', '-'):
                                    if current_part:
                                        parts.append(current_part)
                                    parts.append(char)
                                    current_part = ""
                                else:
                                    current_part += char
                            if current_part:
                                parts.append(current_part)
                            
                            mass_per = mass.calculate_mass(formula=parts[0])
                            j = 1
                            while j < len(parts):
                                operator = parts[j]
                                sub_formula = parts[j + 1]
                                if operator == '+':
                                    mass_per += mass.calculate_mass(formula=sub_formula)
                                elif operator == '-':
                                    mass_per -= mass.calculate_mass(formula=sub_formula)
                                j += 2
                            st.caption(f"Single Mass: {mass_per:.6f} Da")
            # 新增代码块结束
                        valid_ptms.append({
                            "mass": mass_per,
                            "count_options": range(0, count + 1),  # 从0开始生成组合
                            "name": name.strip()
                        })
                    except Exception as e:
                        st.error(f"The {i+1} Item Wrong: {str(e)}")
                        return
            # 新增代码块结束

            if not valid_ptms:
                st.error("Please Input Valid PTMs Configuration!")
                return

            # 生成组合（替换原有结果生成代码）
            all_combinations = itertools.product(*(ptm["count_options"] for ptm in valid_ptms))
            
            results = []
            for counts in all_combinations:
                total_mass = 0.0
                name_parts = []
                for ptm, count in zip(valid_ptms, counts):
                    total_mass += ptm["mass"] * count
                    if count > 0:  # 跳过0次的情况
                        name_parts.append(f"{count}×{ptm['name']}")
                
                if name_parts:  # 至少有一个修饰被应用
                    results.append({
                        "mass_diff": round(total_mass, 6),
                        "name": "+".join(name_parts)
                    })

            # 输出结果（更新原有输出代码）
            if results:
                code = json.dumps(results, indent=4, ensure_ascii=False)
                st.success(f"{len(results)} PTMs Combinations Generated! Please Copy the Json into the PTMs Batch Input Box.")
                st.code(code)

