from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory, Response
from datetime import datetime
import os
import json
import threading
import time
import shutil
import glob
from vis_system.coordinator_agent import CoordinatorAgent
from vis_system.code_generation_agent import CodeGenerationAgent

app = Flask(__name__)
app.secret_key = os.urandom(24)

# 创建必要目录
os.makedirs("./logs", exist_ok=True)
os.makedirs("./test_tmp", exist_ok=True)
os.makedirs("./history", exist_ok=True)
os.makedirs("./history/input", exist_ok=True)
os.makedirs("./history/chart_result", exist_ok=True)
os.makedirs("./history/chart_json", exist_ok=True)

coordinator = CoordinatorAgent(use_log=True)

# 模型名称映射函数
def map_model_name(frontend_model: str) -> str:
    """将前端模型名称映射为后端模型格式"""
    model_mapping = {
        "claude-4-sonnet": "claude-4-sonnet@claude-4-sonnet",
        "gpt-5": "gpt-5@gpt-5",
        "gemini-2.5-pro": "gemini-2.5-pro@gemini-2.5-pro",
        "gemini-2.5-flash": "gemini-2.5-flash@gemini-2.5-flash",
        "gemini-2.0-flash": "gemini-2.0-flash@gemini-2.0-flash",
        "gpt-5-mini": "gpt-5-mini@gpt-5-mini",
        "gpt-5-nano": "gpt-5-nano@gpt-5-nano"
    }
    return model_mapping.get(frontend_model, "gemini-2.0-flash@gemini-2.0-flash")

# 全局进度追踪
progress_data = {}
progress_lock = threading.Lock()

def update_progress(session_id, step, status, data=None):
    """更新进度信息"""
    with progress_lock:
        if session_id not in progress_data:
            progress_data[session_id] = []
        progress_data[session_id].append({
            'step': step,
            'status': status,
            'data': data,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })

def get_progress(session_id):
    """获取进度信息"""
    with progress_lock:
        return progress_data.get(session_id, [])

def clear_progress(session_id):
    """清空进度信息"""
    with progress_lock:
        if session_id in progress_data:
            del progress_data[session_id]

# 辅助函数：获取历史记录文件路径
def get_history_file():
    return os.path.join('./history', 'history.json')

# 辅助函数：获取历史
def get_history():
    history_file = get_history_file()
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                return history[:20]  # 最多返回20条
        except Exception as e:
            print(f"读取历史记录失败: {e}")
            return []
    return []

# 辅助函数：保存历史到文件
def save_history(history):
    history_file = get_history_file()
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history[:20], f, ensure_ascii=False, indent=2)  # 最多保存20条
    except Exception as e:
        print(f"保存历史记录失败: {e}")

# 辅助函数：添加历史
def add_history(db_name, query, results=None, uploaded_image_name=None, original_image_name=None):
    history = get_history()
    history_item = {
        'db_name': db_name,
        'query': query,
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'results': results or {},
        'uploaded_image_name': uploaded_image_name,  # 备份文件名（如：1.jpg）
        'original_image_name': original_image_name   # 原始文件名（如：screenshot.jpg）
    }
    history.insert(0, history_item)
    save_history(history)

# 辅助函数：更新历史记录的结果
def update_history_results(db_name, query, results):
    history = get_history()
    # 找到匹配的历史记录并更新结果
    for item in history:
        if item['db_name'] == db_name and item['query'] == query:
            item['results'] = results
            break
    save_history(history)

# 辅助函数：备份用户上传的图片到history/input文件夹
def backup_input_image(image_path, history_index):
    """将用户上传的图片备份到history/input文件夹"""
    if not image_path or not os.path.exists(image_path):
        return None
    
    try:
        # 获取文件扩展名
        _, ext = os.path.splitext(image_path)
        backup_filename = f"{history_index + 1}{ext}"  # 历史记录索引从1开始命名
        backup_path = os.path.join('./history/input', backup_filename)
        
        # 复制文件
        shutil.copy2(image_path, backup_path)
        print(f"用户上传图片已备份到: {backup_path}")
        return backup_filename
    except Exception as e:
        print(f"备份用户上传图片失败: {e}")
        return None

# 辅助函数：备份用户上传的图片到history/input文件夹（使用指定编号）
def backup_input_image_with_number(image_path, file_number):
    """将用户上传的图片备份到history/input文件夹，使用指定的文件编号"""
    if not image_path or not os.path.exists(image_path):
        return None
    
    try:
        # 获取文件扩展名
        _, ext = os.path.splitext(image_path)
        backup_filename = f"{file_number}{ext}"  # 使用指定的文件编号
        backup_path = os.path.join('./history/input', backup_filename)
        
        # 复制文件
        shutil.copy2(image_path, backup_path)
        print(f"用户上传图片已备份到: {backup_path}")
        return backup_filename
    except Exception as e:
        print(f"备份用户上传图片失败: {e}")
        return None

# 辅助函数：备份结果图表到history/chart_result文件夹
def backup_result_chart(chart_path, history_index):
    """将结果图表备份到history/chart_result文件夹"""
    if not chart_path:
        return None
        
    # 处理chart_path，移除开头的斜杠和反斜杠
    normalized_path = chart_path.lstrip('./')
    full_chart_path = os.path.join('.', normalized_path)
    
    if not os.path.exists(full_chart_path):
        print(f"结果图表文件不存在: {full_chart_path}")
        return None
    
    try:
        backup_filename = f"{history_index + 1}.png"  # 历史记录索引从1开始命名
        backup_path = os.path.join('./history/chart_result', backup_filename)
        
        # 复制文件
        shutil.copy2(full_chart_path, backup_path)
        print(f"结果图表已备份到: {backup_path}")
        return backup_filename
    except Exception as e:
        print(f"备份结果图表失败: {e}")
        return None

# 辅助函数：备份结果图表到history/chart_result文件夹（使用指定编号）
def backup_result_chart_with_number(chart_path, file_number):
    """将结果图表备份到history/chart_result文件夹，使用指定的文件编号"""
    if not chart_path:
        return None
        
    # 处理chart_path，移除开头的斜杠和反斜杠
    normalized_path = chart_path.lstrip('./')
    full_chart_path = os.path.join('.', normalized_path)
    
    if not os.path.exists(full_chart_path):
        print(f"结果图表文件不存在: {full_chart_path}")
        return None
    
    try:
        backup_filename = f"{file_number}.png"  # 使用指定的文件编号
        backup_path = os.path.join('./history/chart_result', backup_filename)
        
        # 复制文件
        shutil.copy2(full_chart_path, backup_path)
        print(f"结果图表已备份到: {backup_path}")
        return backup_filename
    except Exception as e:
        print(f"备份结果图表失败: {e}")
        return None

# 辅助函数：备份JSON图表到history/chart_json文件夹（使用指定编号）
def backup_chart_json_with_number(json_path, file_number):
    """将JSON图表备份到history/chart_json文件夹，使用指定的文件编号"""
    if not json_path:
        return None
        
    # 处理json_path，移除开头的斜杠和反斜杠
    normalized_path = json_path.lstrip('./')
    full_json_path = os.path.join('.', normalized_path)
    
    if not os.path.exists(full_json_path):
        print(f"JSON图表文件不存在: {full_json_path}")
        return None
    
    try:
        backup_filename = f"{file_number}.vega.json"  # 使用指定的文件编号
        backup_path = os.path.join('./history/chart_json', backup_filename)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        # 复制文件
        shutil.copy2(full_json_path, backup_path)
        print(f"JSON图表已备份到: {backup_path}")
        return backup_filename
    except Exception as e:
        print(f"备份JSON图表失败: {e}")
        return None

# 辅助函数：删除历史记录对应的备份文件
def delete_history_backup_files(history_index):
    """删除指定历史记录索引对应的备份文件"""
    try:
        # 获取当前历史记录来计算正确的文件编号
        current_history = get_history()
        if history_index >= len(current_history):
            return
            
        # 计算文件编号：总数 - 索引
        total_count = len(current_history)
        file_number = total_count - history_index
        
        input_dir = './history/input'
        chart_result_dir = './history/chart_result'
        chart_json_dir = './history/chart_json'
        
        # 查找并删除input文件夹中的文件（可能有不同扩展名）
        if os.path.exists(input_dir):
            for file in os.listdir(input_dir):
                if file.startswith(f"{file_number}."):
                    input_file_path = os.path.join(input_dir, file)
                    os.remove(input_file_path)
                    print(f"已删除备份的输入图片: {input_file_path}")
        
        # 删除chart_result文件夹中的文件
        chart_file_path = os.path.join(chart_result_dir, f"{file_number}.png")
        if os.path.exists(chart_file_path):
            os.remove(chart_file_path)
            print(f"已删除备份的结果图表: {chart_file_path}")
        
        # 删除chart_json文件夹中的文件
        json_file_path = os.path.join(chart_json_dir, f"{file_number}.vega.json")
        if os.path.exists(json_file_path):
            os.remove(json_file_path)
            print(f"已删除备份的JSON文件: {json_file_path}")
            
    except Exception as e:
        print(f"删除备份文件失败: {e}")

# 辅助函数：重新编号所有备份文件
def renumber_backup_files():
    """重新编号所有备份文件以保持编号连续性"""
    try:
        input_dir = './history/input'
        chart_result_dir = './history/chart_result'
        chart_json_dir = './history/chart_json'
        
        # 获取当前历史记录
        history = get_history()
        total_count = len(history)
        
        # 创建临时映射来追踪文件重命名
        temp_suffix = '_temp'
        
        # 重新编号input文件夹中的文件
        if os.path.exists(input_dir):
            # 第一步：将所有文件重命名为临时名称
            input_files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
            for file in input_files:
                if temp_suffix not in file:  # 避免重复处理
                    old_path = os.path.join(input_dir, file)
                    temp_name = file + temp_suffix
                    temp_path = os.path.join(input_dir, temp_name)
                    os.rename(old_path, temp_path)
            
            # 第二步：按照新的编号方案重命名
            for i, item in enumerate(history):
                correct_file_number = total_count - i  # 计算正确的文件编号
                uploaded_image = item.get('uploaded_image_name')
                
                if uploaded_image:
                    # 查找对应的临时文件
                    temp_filename = uploaded_image + temp_suffix
                    temp_path = os.path.join(input_dir, temp_filename)
                    
                    if os.path.exists(temp_path):
                        # 获取扩展名
                        _, ext = os.path.splitext(uploaded_image)
                        new_filename = f"{correct_file_number}{ext}"
                        new_path = os.path.join(input_dir, new_filename)
                        
                        os.rename(temp_path, new_path)
                        # 更新历史记录中的文件名
                        item['uploaded_image_name'] = new_filename
                        print(f"重命名输入图片: {uploaded_image} -> {new_filename}")
        
        # 重新编号chart_result文件夹中的文件
        if os.path.exists(chart_result_dir):
            # 第一步：将所有文件重命名为临时名称
            chart_files = [f for f in os.listdir(chart_result_dir) if f.endswith('.png')]
            for file in chart_files:
                if temp_suffix not in file:  # 避免重复处理
                    old_path = os.path.join(chart_result_dir, file)
                    temp_name = file.replace('.png', temp_suffix + '.png')
                    temp_path = os.path.join(chart_result_dir, temp_name)
                    os.rename(old_path, temp_path)
            
            # 第二步：按照新的编号方案重命名
            for i, item in enumerate(history):
                correct_file_number = total_count - i  # 计算正确的文件编号
                chart_backup_name = item.get('results', {}).get('chart_backup_name')
                
                if chart_backup_name:
                    # 查找对应的临时文件
                    temp_filename = chart_backup_name.replace('.png', temp_suffix + '.png')
                    temp_path = os.path.join(chart_result_dir, temp_filename)
                    
                    if os.path.exists(temp_path):
                        new_filename = f"{correct_file_number}.png"
                        new_path = os.path.join(chart_result_dir, new_filename)
                        
                        os.rename(temp_path, new_path)
                        # 更新历史记录中的文件名
                        item['results']['chart_backup_name'] = new_filename
                        print(f"重命名结果图表: {chart_backup_name} -> {new_filename}")
        
        # 重新编号chart_json文件夹中的JSON文件
        if os.path.exists(chart_json_dir):
            # 第一步：将所有文件重命名为临时名称
            json_files = [f for f in os.listdir(chart_json_dir) if f.endswith('.vega.json')]
            for file in json_files:
                if temp_suffix not in file:  # 避免重复处理
                    old_path = os.path.join(chart_json_dir, file)
                    temp_name = file.replace('.vega.json', temp_suffix + '.vega.json')
                    temp_path = os.path.join(chart_json_dir, temp_name)
                    os.rename(old_path, temp_path)
            
            # 第二步：按照新的编号方案重命名
            for i, item in enumerate(history):
                correct_file_number = total_count - i  # 计算正确的文件编号
                chart_json_backup_name = item.get('results', {}).get('chart_json_backup_name')
                
                if chart_json_backup_name:
                    # 查找对应的临时文件
                    temp_filename = chart_json_backup_name.replace('.vega.json', temp_suffix + '.vega.json')
                    temp_path = os.path.join(chart_json_dir, temp_filename)
                    
                    if os.path.exists(temp_path):
                        new_filename = f"{correct_file_number}.vega.json"
                        new_path = os.path.join(chart_json_dir, new_filename)
                        
                        os.rename(temp_path, new_path)
                        # 更新历史记录中的文件名
                        item['results']['chart_json_backup_name'] = new_filename
                        print(f"重命名JSON文件: {chart_json_backup_name} -> {new_filename}")
        
        # 保存更新的历史记录
        save_history(history)
        
    except Exception as e:
        print(f"重新编号备份文件失败: {e}")

# 辅助函数：删除指定索引的历史记录
def delete_history_item(index):
    try:
        history = get_history()
        if 0 <= index < len(history):
            # 先删除对应的备份文件
            delete_history_backup_files(index)
            
            # 删除指定索引的项目
            history.pop(index)
            save_history(history)
            
            # 重新编号剩余的备份文件
            renumber_backup_files()
            
            return True
        else:
            print(f"无效的历史记录索引: {index}")
            return False
    except Exception as e:
        print(f"删除历史记录项失败: {e}")
        return False

# 辅助函数：清空历史
def clear_history():
    history_file = get_history_file()
    if os.path.exists(history_file):
        try:
            os.remove(history_file)
        except Exception as e:
            print(f"删除历史记录文件失败: {e}")
    
    # 清空备份文件夹
    try:
        # 清空history/input文件夹
        input_dir = './history/input'
        if os.path.exists(input_dir):
            for file in os.listdir(input_dir):
                file_path = os.path.join(input_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"已删除输入备份文件: {file_path}")
        
        # 清空history/chart_result文件夹  
        chart_result_dir = './history/chart_result'
        if os.path.exists(chart_result_dir):
            for file in os.listdir(chart_result_dir):
                file_path = os.path.join(chart_result_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"已删除结果备份文件: {file_path}")
        
        # 清空history/chart_json文件夹
        chart_json_dir = './history/chart_json'
        if os.path.exists(chart_json_dir):
            for file in os.listdir(chart_json_dir):
                file_path = os.path.join(chart_json_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"已删除JSON备份文件: {file_path}")
                    
    except Exception as e:
        print(f"清空备份文件夹失败: {e}")

# 清理文件夹函数
def clear_folders():
    """清空logs、temp、test_tmp文件夹中的所有文件"""
    folders_to_clear = ['logs', 'temp', 'test_tmp']
    
    for folder in folders_to_clear:
        try:
            if os.path.exists(folder):
                # 清空文件夹内的所有文件和子文件夹
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            os.remove(file_path)
                            print(f"已删除文件: {file_path}")
                        except Exception as e:
                            print(f"删除文件失败 {file_path}: {e}")
                    
                    # 删除空的子文件夹（从最深层开始）
                    for dir_path in [os.path.join(root, d) for d in dirs]:
                        try:
                            if os.path.exists(dir_path) and not os.listdir(dir_path):
                                os.rmdir(dir_path)
                                print(f"已删除空文件夹: {dir_path}")
                        except Exception as e:
                            print(f"删除文件夹失败 {dir_path}: {e}")
                
                print(f"文件夹 {folder} 清理完成")
            else:
                print(f"文件夹 {folder} 不存在，跳过清理")
        except Exception as e:
            print(f"清理文件夹 {folder} 时出错: {e}")

def process_async(session_id, db_name, nl_query, ref_code, mod_code, ref_image_path, model_type):
    """异步处理可视化生成"""
    try:
        update_progress(session_id, 'start', 'info', 'Starting visualization generation...')
        
        # 创建一个带回调的coordinator
        class ProgressCoordinator(CoordinatorAgent):
            def __init__(self, session_id, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.session_id = session_id
            
            def _generate_sql_from_query_tool(self):
                try:
                    update_progress(self.session_id, 'sql_generation', 'processing', 'Generating SQL query...')
                    result = super()._generate_sql_from_query_tool()
                    if result.get('status'):
                        update_progress(self.session_id, 'sql_generation', 'success', 'SQL query generated successfully')
                    else:
                        update_progress(self.session_id, 'sql_generation', 'error', f"Failed to generate SQL query: {result.get('message', 'Unknown error')}")
                    return result
                except Exception as e:
                    update_progress(self.session_id, 'sql_generation', 'error', f'SQL generation error: {str(e)}')
                    return {"status": False, "message": str(e)}
            
            def _generate_visualization_code_tool(self):
                try:
                    update_progress(self.session_id, 'code_generation', 'processing', 'Generating visualization code...')
                    result = super()._generate_visualization_code_tool()
                    if result.get('status'):
                        update_progress(self.session_id, 'code_generation', 'success', 'Visualization code generated successfully')
                        # 发送当前代码
                        if hasattr(self, 'visualization_code') and self.visualization_code:
                            update_progress(self.session_id, 'code_update', 'info', self.visualization_code)
                    else:
                        update_progress(self.session_id, 'code_generation', 'error', f"Failed to generate visualization code: {result.get('message', 'Unknown error')}")
                    return result
                except Exception as e:
                    update_progress(self.session_id, 'code_generation', 'error', f'Code generation error: {str(e)}')
                    return {"status": False, "message": str(e)}
            
            def _evaluate_visualization_tool(self):
                try:
                    update_progress(self.session_id, 'evaluation', 'processing', 'Evaluating visualization...')
                    result = super()._evaluate_visualization_tool()
                    # 检查evaluation_success字段（如果存在）或默认为True（表示成功调用）
                    success = result.get('evaluation_success', True) if isinstance(result, dict) else True
                    if success:
                        update_progress(self.session_id, 'evaluation', 'success', 'Evaluation completed successfully')
                    else:
                        update_progress(self.session_id, 'evaluation', 'error', f"Evaluation failed: {result.get('message', 'Unknown error')}")
                    
                    # 注释：评估结果只在最终结果中显示，不在进度更新中发送
                    # try:
                    #     if hasattr(self, 'evaluation_result') and self.evaluation_result:
                    #         formatted_eval = self._format_evaluation_result()
                    #         update_progress(self.session_id, 'evaluation_result', 'info', formatted_eval)
                    # except Exception as eval_format_error:
                    #     print(f"评估结果格式化错误: {eval_format_error}")
                    #     # 如果格式化失败，至少发送原始评估数据
                    #     if hasattr(self, 'evaluation_result') and self.evaluation_result:
                    #         update_progress(self.session_id, 'evaluation_result', 'info', str(self.evaluation_result))
                    
                    return result
                except Exception as e:
                    update_progress(self.session_id, 'evaluation', 'error', f'Evaluation error: {str(e)}')
                    return {"evaluation_success": False, "message": str(e)}
            
            def _execute_visualization_code(self, code: str, iteration: int) -> str:
                """重写执行方法，添加进度更新"""
                try:
                    update_progress(self.session_id, 'iteration_execution', 'processing', f'Executing iteration {iteration} visualization code...')
                    
                    # 调用父类方法执行代码
                    chart_path = super()._execute_visualization_code(code, iteration)
                    
                    if chart_path:
                        # 发送迭代代码更新
                        update_progress(self.session_id, 'code_iteration', 'info', {
                            'iteration': iteration,
                            'code': code,
                            'chart_path': chart_path.replace('\\', '/').lstrip('./'),
                            'timestamp': datetime.now().strftime('%H:%M:%S')
                        })
                        update_progress(self.session_id, 'iteration_execution', 'success', f'Iteration {iteration} chart generated successfully')
                    else:
                        update_progress(self.session_id, 'iteration_execution', 'error', f'Failed to generate chart for iteration {iteration}')
                    
                    return chart_path
                except Exception as e:
                    update_progress(self.session_id, 'iteration_execution', 'error', f'Iteration {iteration} execution error: {str(e)}')
                    return None
        
        progress_coordinator = ProgressCoordinator(session_id, model_type=model_type, use_log=True)
        
        update_progress(session_id, 'coordinator_created', 'info', 'Progress coordinator created successfully')
        
        result = progress_coordinator.process(
            db_name=db_name,
            nl_query=nl_query,
            ref_code=ref_code,
            mod_code=mod_code,
            ref_image_path=ref_image_path
        )
        
        update_progress(session_id, 'process_finished', 'info', 'Process method completed')
        
        # 调试信息
        update_progress(session_id, 'debug_result', 'info', f'Result keys: {list(result.keys()) if result else "None"}')
        if result and 'chart_img' in result:
            update_progress(session_id, 'debug_chart', 'info', f'Chart image path: {result["chart_img"]}')
        else:
            update_progress(session_id, 'debug_chart', 'error', 'No chart_img in result')
        
        # 发送最终结果
        update_progress(session_id, 'complete', 'success', result)
        
        # 更新历史记录的结果（而不是新增）
        if db_name and nl_query:
            # 备份结果图表和JSON文件
            chart_backup_name = None
            chart_json_backup_name = None
            if result.get('chart_img'):
                # 找到对应的历史记录索引（最新的一条）
                current_history = get_history()
                history_index = None
                for i, item in enumerate(current_history):
                    if item['db_name'] == db_name and item['query'] == nl_query:
                        history_index = i
                        break
                
                if history_index is not None:
                    # 使用历史记录的实际位置来决定文件编号
                    # 历史记录是倒序的，所以索引0是最新的（应该是编号最大的）
                    # 编号应该是：总数 - 索引
                    total_count = len(current_history)
                    file_number = total_count - history_index  # 这样第一条记录（索引0）就是最大编号
                    chart_backup_name = backup_result_chart_with_number(result.get('chart_img'), file_number)
                    
                    # 如果有JSON文件，也备份它
                    if result.get('chart_json'):
                        chart_json_backup_name = backup_chart_json_with_number(result.get('chart_json'), file_number)
            
            # 根据代码类型决定如何存储代码
            code_content = ref_code or mod_code
            is_database_code = bool(mod_code)
            
            results = {
                'vis_code': result.get('vis_code'),
                'vis_code_iter': result.get('vis_code_iter'),
                'chart_img': result.get('chart_img'),
                'chart_json': result.get('chart_json'),  # 添加JSON图表路径
                'sql': result.get('sql'),
                'sql_iter': result.get('sql_iter'),
                'eval_result': result.get('eval_result'),
                'ref_code': ref_code,
                'mod_code': mod_code,
                'code': code_content,
                'is_database_code': is_database_code,
                'chart_backup_name': chart_backup_name,
                'chart_json_backup_name': chart_json_backup_name  # 添加JSON备份文件名
            }
            update_history_results(db_name, nl_query, results)
            update_progress(session_id, 'history_updated', 'success', 'History record updated with results')
        
    except Exception as e:
        update_progress(session_id, 'error', 'error', f'Error: {str(e)}')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 在查询开始前清理文件夹
        print("正在清理文件夹...")
        clear_folders()
        print("文件夹清理完成")
        
        # 生成唯一的session ID
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # 获取表单数据
        db_name = request.form.get('db_name', '').strip()
        nl_query = request.form.get('nl_query', '').strip()
        code = request.form.get('code', '').strip()
        model_type = map_model_name(request.form.get('model_type', 'gemini-2.0-flash').strip())
        is_database_code = 'is_database_code' in request.form
        
        # 获取上传文件
        db_file = request.files.get('db_file')
        ref_image = request.files.get('ref_image')
        code_file = request.files.get('code_file')
        
        # 处理数据库文件上传
        db_file_path = None
        if db_file and db_file.filename:
            db_name = db_file.filename  # 使用上传的数据库文件名
            db_file_path = os.path.join('database', db_file.filename)
            os.makedirs(os.path.dirname(db_file_path), exist_ok=True)
            db_file.save(db_file_path)
            print(f"数据库文件已保存到: {db_file_path}")

        # 处理图片上传
        ref_image_path = None
        uploaded_image_name = None
        original_image_name = None
        if ref_image and ref_image.filename:
            original_image_name = ref_image.filename  # 保存原始文件名
            ref_image_path = os.path.join('static', 'uploads', ref_image.filename)
            os.makedirs(os.path.dirname(ref_image_path), exist_ok=True)
            ref_image.save(ref_image_path)
            
            # 立即备份用户上传的图片到history/input文件夹
            # 先获取当前历史记录数量作为新记录的编号
            current_history = get_history()
            file_number = len(current_history) + 1  # 新记录应该是下一个编号
            uploaded_image_name = backup_input_image_with_number(ref_image_path, file_number)

        # 处理代码文件上传
        def process_code_file(code_file):
            """处理上传的代码文件，返回代码内容"""
            if not code_file or not code_file.filename:
                return ""
            
            try:
                content = code_file.read().decode('utf-8')
                
                # 如果是Jupyter notebook文件，提取代码单元格
                if code_file.filename.endswith('.ipynb'):
                    notebook = json.loads(content)
                    extracted_code = ""
                    
                    if 'cells' in notebook and isinstance(notebook['cells'], list):
                        for i, cell in enumerate(notebook['cells']):
                            if cell.get('cell_type') == 'code' and cell.get('source'):
                                extracted_code += f"# Cell {i + 1}\n"
                                
                                # 处理source内容（可能是字符串或字符串列表）
                                source = cell['source']
                                if isinstance(source, list):
                                    source = ''.join(source)
                                
                                extracted_code += source
                                if not source.endswith('\n'):
                                    extracted_code += '\n'
                                extracted_code += '\n'
                    
                    return extracted_code.strip()
                
                # 普通Python文件直接返回内容
                return content
                
            except Exception as e:
                print(f"处理代码文件时出错: {e}")
                return ""
        
        # 如果上传了代码文件，处理并覆盖文本框内容
        if code_file and code_file.filename:
            uploaded_code = process_code_file(code_file)
            if uploaded_code:
                code = uploaded_code
                
        # 根据勾选框状态决定使用哪一种代码类型
        ref_code = ''
        mod_code = ''
        if code:
            if is_database_code:
                # 如果代码基于当前数据库，则作为mod_code处理
                mod_code = code
            else:
                # 如果代码不基于当前数据库，则作为ref_code处理
                ref_code = code

        # 在会话中保存参考信息，供结果页 Reference Preview 使用
        try:
            session['uploaded_image_name'] = uploaded_image_name or ''
            session['original_image_name'] = original_image_name or ''
            session['uploaded_code'] = code or ''
        except Exception:
            pass

        # 立即添加历史记录（不包含结果）
        if db_name and nl_query:
            add_history(db_name, nl_query, results=None, uploaded_image_name=uploaded_image_name, original_image_name=original_image_name)
        
        # 清空之前的进度
        clear_progress(session_id)
        
        # 启动异步处理
        thread = threading.Thread(target=process_async, args=(session_id, db_name, nl_query, ref_code, mod_code, ref_image_path, model_type))
        thread.daemon = True
        thread.start()
        
        # 重定向到结果页面
        return redirect(url_for('result', session_id=session_id, db_name=db_name, nl_query=nl_query))
    
    # 只返回查询表单，不包含结果部分
    return render_template('index.html', history=get_history())

@app.route('/load_history/<int:index>', methods=['GET'])
def load_history(index):
    """加载历史记录中的特定查询结果"""
    history = get_history()
    if 0 <= index < len(history):
        item = history[index]
        
        # 构建备份图片的路径
        chart_img_path = item.get('results', {}).get('chart_img', '')
        chart_backup_name = item.get('results', {}).get('chart_backup_name')
        if chart_backup_name:
            # 使用备份的图表文件
            chart_img_path = f'/history/chart_result/{chart_backup_name}'
        
        # 获取JSON图表路径
        chart_json_path = item.get('results', {}).get('chart_json', '')
        chart_json_backup_name = item.get('results', {}).get('chart_json_backup_name')
        if chart_json_backup_name:
            # 使用备份的JSON文件
            chart_json_path = f'/history/chart_json/{chart_json_backup_name}'
        
        # 获取代码内容和类型
        code = item.get('results', {}).get('code', '')
        if not code:
            # 兼容旧的历史记录格式
            ref_code = item.get('results', {}).get('ref_code', '')
            mod_code = item.get('results', {}).get('mod_code', '')
            code = ref_code or mod_code
            is_database_code = bool(mod_code)
        else:
            is_database_code = item.get('results', {}).get('is_database_code', False)
        
        # 获取可视化代码
        vis_code = item.get('results', {}).get('vis_code', '')
        
        # 获取评估结果，并简单清理
        eval_result = item.get('results', {}).get('eval_result', '')
        if eval_result:
            import re
            # 移除可能导致HTML渲染问题的控制字符
            eval_result = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', eval_result)
        
        # 获取SQL查询
        sql = item.get('results', {}).get('sql', '')
        sql_iter = item.get('results', {}).get('sql_iter', '')
        
        # 获取其他字段
        uploaded_image_name = item.get('uploaded_image_name', '')
        original_image_name = item.get('original_image_name', '')
        
        # 如果历史记录中的code字段是JSON文件路径，尝试读取并处理JSON内容
        reference_preview_data = None
        if code and code.startswith('/history/chart_json/') and code.endswith('.json'):
            try:
                # 构建实际文件路径
                json_file_path = code.lstrip('/').replace('/', os.sep)
                full_json_path = os.path.join('.', json_file_path)
                
                if os.path.exists(full_json_path):
                    with open(full_json_path, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                    
                    reference_preview_data = {
                        'json_content': json_data,
                        'json_path': code,
                        'has_json': True
                    }
                    print(f"成功加载历史记录中的JSON文件: {full_json_path}")
                else:
                    print(f"历史记录中的JSON文件不存在: {full_json_path}")
            except Exception as e:
                print(f"读取历史记录JSON文件失败: {e}")
        
        # 我们仍然需要返回JSON格式的数据，因为这是API调用
        # 但是，我们会尽量简化数据结构，避免复杂的嵌套
        response_data = {
            'success': True,
            'db_name': item['db_name'],
            'nl_query': item['query'],
            'ref_code': item.get('results', {}).get('ref_code', ''),
            'mod_code': item.get('results', {}).get('mod_code', ''),
            'code': code,
            'is_database_code': is_database_code,
            'vis_code': vis_code,
            'vis_code_iter': item.get('results', {}).get('vis_code_iter', ''),
            'chart_img': chart_img_path,
            'chart_json': chart_json_path,
            'sql': sql,
            'sql_iter': sql_iter,
            'eval_result': eval_result,
            'uploaded_image_name': uploaded_image_name,
            'original_image_name': original_image_name,
            'is_history_result': True
        }
        
        # 如果有Reference Preview数据，添加到响应中
        if reference_preview_data:
            response_data['reference_preview'] = reference_preview_data
        
        return jsonify(response_data)
    else:
        return jsonify({'success': False, 'error': 'History item not found'})

@app.route('/get_history', methods=['GET'])
def get_history_route():
    """获取最新的历史记录"""
    return jsonify({'success': True, 'history': get_history()})

@app.route('/delete_history/<int:index>', methods=['DELETE'])
def delete_history_route(index):
    """删除指定索引的历史记录"""
    try:
        success = delete_history_item(index)
        if success:
            return jsonify({'success': True, 'message': 'History record deleted successfully!'})
        else:
            return jsonify({'success': False, 'error': '无效的历史记录索引或删除失败'})
    except Exception as e:
        print(f"删除历史记录API错误: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/clear_history', methods=['POST'])
def clear_history_route():
    clear_history()
    return redirect(url_for('index'))

@app.route('/progress/<session_id>')
def progress_stream(session_id):
    """Server-Sent Events端点，实时推送进度"""
    def generate():
        last_count = 0
        max_wait_time = 60  # 最大等待时间60秒
        wait_count = 0
        
        # 发送初始连接确认
        yield f"data: {json.dumps({'step': 'connected', 'status': 'info', 'data': 'Connected to progress stream'})}\n\n"
        
        while wait_count < max_wait_time * 2:  # 每0.5秒检查一次
            progress = get_progress(session_id)
            
            # 只发送新的进度更新
            if len(progress) > last_count:
                for item in progress[last_count:]:
                    yield f"data: {json.dumps(item)}\n\n"
                last_count = len(progress)
                wait_count = 0  # 重置等待计数
            
            # 检查是否完成
            if progress and progress[-1]['step'] in ['complete', 'error']:
                yield f"data: {json.dumps({'step': 'end', 'status': 'info', 'data': 'Stream ended'})}\n\n"
                break
                
            time.sleep(0.5)  # 500ms间隔检查
            wait_count += 1
            
            # 发送心跳信号
            if wait_count % 10 == 0:  # 每5秒发送一次心跳
                yield f"data: {json.dumps({'step': 'heartbeat', 'status': 'info', 'data': f'Waiting for progress... ({wait_count//2}s)'})}\n\n"
        
        # 超时处理
        if wait_count >= max_wait_time * 2:
            yield f"data: {json.dumps({'step': 'timeout', 'status': 'error', 'data': 'Stream timeout after 60 seconds'})}\n\n"
    
    response = Response(generate(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/test_progress')
def test_progress():
    """测试进度更新功能"""
    session_id = "test_session"
    clear_progress(session_id)
    
    def test_async():
        time.sleep(1)
        update_progress(session_id, 'test_start', 'info', 'Test started')
        time.sleep(2)
        update_progress(session_id, 'test_middle', 'processing', 'Test in progress')
        time.sleep(2)
        update_progress(session_id, 'test_end', 'success', 'Test completed')
        time.sleep(1)
        update_progress(session_id, 'complete', 'success', {'test': 'data'})
    
    thread = threading.Thread(target=test_async)
    thread.daemon = True
    thread.start()
    
    return render_template('index.html', history=get_history(), session_id=session_id, processing=True)

@app.route('/debug_chart')
def debug_chart():
    """调试图表显示问题"""
    chart_path = "test_tmp/generated_chart.png"
    file_exists = os.path.exists(chart_path)
    file_size = os.path.getsize(chart_path) if file_exists else 0
    
    debug_info = {
        'chart_path': chart_path,
        'file_exists': file_exists,
        'file_size': file_size,
        'url_path': f'/test_tmp/generated_chart.png',
        'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return jsonify(debug_info)

@app.route('/test_tmp/<path:filename>')
def serve_test_tmp_file(filename):
    """服务test_tmp目录中的任何文件（包括PNG和JSON文件）"""
    return send_from_directory('test_tmp', filename)

@app.route('/history/input/<filename>')
def serve_input_image(filename):
    """服务历史记录中的用户上传图片"""
    return send_from_directory('history/input', filename)

@app.route('/history/chart_result/<filename>')
def serve_result_chart(filename):
    """服务历史记录中的结果图表"""
    return send_from_directory('history/chart_result', filename)

@app.route('/history/chart_json/<filename>')
def serve_chart_json(filename):
    """服务历史记录中的JSON格式图表"""
    return send_from_directory('history/chart_json', filename)

@app.route('/result')
def result():
    """显示查询结果的页面"""
    session_id = request.args.get('session_id')
    db_name = request.args.get('db_name', '')
    nl_query = request.args.get('nl_query', '')
    
    # 如果有session_id，说明是新的查询请求
    if session_id:
        # 从会话读取参考信息供 Reference Preview 使用
        uploaded_image_name = session.get('uploaded_image_name', '')
        original_image_name = session.get('original_image_name', '')
        uploaded_code = session.get('uploaded_code', '')
        return render_template('result.html', session_id=session_id, db_name=db_name, nl_query=nl_query,
                               uploaded_image_name=uploaded_image_name,
                               original_image_name=original_image_name,
                               uploaded_code=uploaded_code)
    
    # 如果没有session_id但有db_name和nl_query，尝试从历史记录中查找结果
    if db_name and nl_query:
        history = get_history()
        for i, item in enumerate(history):
            if item['db_name'] == db_name and item['query'] == nl_query:
                # 找到匹配的历史记录，获取其结果
                results = item.get('results', {})
                
                # 构建图表路径
                chart_img_path = results.get('chart_img', '')
                chart_backup_name = results.get('chart_backup_name')
                if chart_backup_name:
                    chart_img_path = f'/history/chart_result/{chart_backup_name}'
                
                # 获取JSON图表路径
                chart_json_path = results.get('chart_json', '')
                chart_json_backup_name = results.get('chart_json_backup_name')
                if chart_json_backup_name:
                    chart_json_path = f'/history/chart_json/{chart_json_backup_name}'
                
                # 渲染结果页面，并传递历史结果数据
                # 获取各个字段，单独传递给模板，避免JSON序列化问题
                vis_code = results.get('vis_code', '')
                eval_result = results.get('eval_result', '')
                
                # 不再需要对评估结果进行JSON序列化，因为它将作为单独的变量传递
                # 但仍然可以清理一下文本，以防在HTML渲染时出现问题
                if eval_result:
                    import re
                    # 移除可能导致HTML渲染问题的控制字符
                    eval_result = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', eval_result)
                
                # 计算上传的参考代码（若存在）
                uploaded_code = results.get('code') or results.get('ref_code') or results.get('mod_code') or ''

                return render_template(
                    'result.html', 
                    db_name=db_name, 
                    nl_query=nl_query,
                    # 不再使用history_results对象，而是单独传递每个字段
                    chart_img=chart_img_path,
                    chart_json=chart_json_path,
                    vis_code=vis_code,
                    eval_result=eval_result,
                    uploaded_image_name=item.get('uploaded_image_name', ''),
                    original_image_name=item.get('original_image_name', ''),
                    uploaded_code=uploaded_code,
                    # 添加一个标志，表示这是从历史记录加载的
                    is_history_result=True
                )
    
    # 如果无法找到匹配的历史记录或没有提供足够的参数，重定向到首页
    return redirect(url_for('index'))

@app.route('/execute_reference_preview', methods=['POST'])
def execute_reference_preview():
    """执行用户上传的参考代码，返回可预览资源路径
    - Altair 代码：返回 PNG 和对应的 Vega-Lite JSON（若生成）
    - Matplotlib 代码：仅返回 PNG
    """
    try:
        data = request.get_json(force=True, silent=True) or {}
        code = data.get('code', '')
        if not code or not isinstance(code, str) or not code.strip():
            return jsonify({"success": False, "error": "Empty code"}), 400

        # 输出路径（带时间戳避免覆盖）
        ts = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        png_path = f"./test_tmp/ref_preview_{ts}.png"

        agent = CodeGenerationAgent(model_type="gemini-2.0-flash@gemini-2.0-flash", use_log=False)

        # 简单检测代码类型
        is_matplotlib = ('matplotlib' in code) or ('plt.' in code)
        is_altair = ('altair' in code) or ('alt.' in code) or ('Chart(' in code)

        result = None
        json_path = None
        if is_altair and not is_matplotlib:
            result = agent._execute_altair_code(code, png_path)
            if result.get('status') == 'success':
                # Altair 执行实现中会将 JSON 保存为同名 .vega.json
                json_candidate = png_path.replace('.png', '.vega.json')
                if os.path.exists(json_candidate):
                    json_path = '/' + json_candidate.replace('\\', '/').lstrip('./')
        else:
            # 默认使用 Matplotlib 执行
            result = agent._execute_matplotlib_code(code, png_path)

        if result.get('status') != 'success':
            return jsonify({
                "success": False,
                "error": result.get('info', 'Execution failed')
            }), 200

        # 构造可访问 URL
        img_url = '/' + png_path.replace('\\', '/').lstrip('./')

        return jsonify({
            "success": True,
            "img_path": img_url,
            "json_path": json_path
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/data/<path:filename>')
def serve_altair_data(filename):
    """服务Altair生成的数据JSON文件（altair-data-*.json）"""
    # 只允许访问 altair-data- 开头的 JSON 文件
    if filename.startswith('altair-data-') and filename.endswith('.json'):
        if os.path.exists(filename):
            return send_from_directory('.', filename)
    from flask import abort
    abort(404)

if __name__ == '__main__':
    app.run(debug=True, threaded=True) 
