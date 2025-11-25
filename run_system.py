import time

from vis_system_no_rule.coordinator_agent import CoordinatorAgent
# from ablation.without_val.coordinator_agent import CoordinatorAgent
# from ablation.without_db.coordinator_agent import CoordinatorAgent


if __name__ == '__main__':
        # 测试协调器智能体
    import sys
    import os
    
    # 创建日志目录
    os.makedirs("./logs", exist_ok=True)
    os.makedirs("./test_tmp", exist_ok=True)
    
    # 初始化协调器智能体
    coordinator = CoordinatorAgent(model_type="gemini-2.0-flash@gemini-2.0-flash", agent_id=59, use_log=True)
    
    print("\n===== 测试 CoordinatorAgent =====")
    
    item = {
        "type": "type_A",
        "db_id": "activity_1",
        "chart_category": "Advanced Calculations",
        "chart_type": "calculate_residuals",
        "NLQ": "Can you create a scatter plot showing how each activity's average student age differs from the overall average? Put activity names on the x-axis and the age difference in years on the y-axis. Title it \"Difference in Average Age by Activity\" and color-code the points using a red-blue scheme where red shows activities with younger-than-average students and blue shows older-than-average students.",
        "code": "import sqlite3\nimport pandas as pd\nimport altair as alt\n\nconn = sqlite3.connect('database/activity_1.sqlite')\n\nquery = '''\nSELECT \n    A.activity_name,\n    AVG(S.Age) AS Avg_Age\nFROM \n    Activity AS A\nJOIN \n    Participates_in AS P ON A.actid = P.actid\nJOIN \n    Student AS S ON P.stuid = S.StuID\nGROUP BY \n    A.actid, A.activity_name\n'''\n\ndf = pd.read_sql_query(query, conn)\nconn.close()\n\noverall_avg_age = df['Avg_Age'].mean()\n\nchart = (\n    alt.Chart(df)\n    .mark_point()\n    .transform_calculate(\n        Age_Delta=\"datum.Avg_Age - \" + str(overall_avg_age)\n    )\n    .encode(\n        x=alt.X(\"activity_name:N\").title(\"Activity Name\"),\n        y=alt.Y(\"Age_Delta:Q\").title(\"Age Delta (Years)\"),\n        color=alt.Color(\"Age_Delta:Q\")\n        .title(\"Age Delta\")\n        .scale(domainMid=0, scheme=\"redblue\"),\n    )\n    .properties(title=\"Difference in Average Age by Activity\")\n)\n\nchart"
    }

    start_time = time.time()
    result = coordinator.process_item(item)
    end_time = time.time()
    execution_time = end_time - start_time

    coordinator._log(f"完成状态:\n{result['status']}")
    coordinator._log(f"最终可视化代码:\n{result['prediction']}")
    coordinator._log(f"执行时间: {execution_time:.2f} 秒")

    print("\n===== 测试完成 =====") 