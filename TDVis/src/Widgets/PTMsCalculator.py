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
                        formula = st.session_state.get(f"formula_{i}", "")
                        count = st.session_state.get(f"count_{i}", 0)
                        name = st.session_state.get(f"name_{i}", "")

                        if not formula.strip() or not name.strip():
                            st.error(f"第 {i+1} 项的公式或名称不能为空")
                            return

                        # 新的混合计算逻辑
                        parts = []
                        current = ""
                        for c in formula:
                            if c in ('+', '-'):
                                if current:
                                    parts.append(current.strip())
                                parts.append(c)
                                current = ""
                            else:
                                current += c
                        if current:
                            parts.append(current.strip())

                        # 处理空表达式或无效格式
                        if not parts:
                            raise ValueError("空表达式")

                        # 支持表达式以符号开头（如 -100+C6H12O6）
                        if parts[0] in ('+', '-'):
                            mass_per = 0.0
                            index = 0
                        else:
                            # 处理第一个元素（可能是数字或化学式）
                            try:
                                mass_per = float(parts[0])
                            except ValueError:
                                mass_per = mass.calculate_mass(formula=parts[0])
                            index = 1

                        # 遍历剩余部分进行混合计算
                        while index < len(parts):
                            if index + 1 >= len(parts):
                                raise ValueError("不完整的表达式")

                            operator = parts[index]
                            element = parts[index + 1]

                            try:
                                value = float(element)
                            except ValueError:
                                value = mass.calculate_mass(formula=element)

                            if operator == '+':
                                mass_per += value
                            elif operator == '-':
                                mass_per -= value
                            else:
                                raise ValueError("无效的操作符")

                            index += 2

                        valid_ptms.append({
                            "mass": mass_per,
                            "count_options": range(0, count + 1),
                            "name": name.strip()
                        })

                    except Exception as e:
                        st.error(f"第 {i+1} 项错误: {str(e)}")
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

