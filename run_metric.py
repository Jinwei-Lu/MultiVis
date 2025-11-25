import json

from metric.metric import VisualizationMetrics


if __name__ == "__main__":
    model_type = "gpt-4o-mini@gpt-4o-mini"
    model_type = model_type.replace("@", "___")
    method_type = "nvAgent2"
    results_path = './results/{}/{}/{}/results.json'

    # for data_type in ['text2vis']:
    for data_type in ['text2vis', 'vis_modify', 'text2vis_with_img', 'text2vis_with_code']:
        with open(results_path.format(method_type, model_type, data_type), 'r', encoding='utf-8') as f:
            results = json.load(f)

        metrics = VisualizationMetrics()
        metrics_result, wrong_results, correct_results = metrics.evaluate_parallel(results, num_workers=20, use_high_level_metrics=True, use_low_level_metrics=True)

        with open('./results/{}/{}/{}/metric.json'.format(method_type, model_type, data_type), 'w', encoding='utf-8') as f:
            json.dump(metrics_result, f, indent=4, ensure_ascii=False)
        with open('./results/{}/{}/{}/wrong_results.json'.format(method_type, model_type, data_type), 'w', encoding='utf-8') as f:
            json.dump(wrong_results, f, indent=4, ensure_ascii=False)
        with open('./results/{}/{}/{}/correct_results.json'.format(method_type, model_type, data_type), 'w', encoding='utf-8') as f:
            json.dump(correct_results, f, indent=4, ensure_ascii=False)

    # model_type = "gemini-2.0-flash___gemini-2.0-flash"
    # model_type = model_type.replace("@", "___")
    # results_path = './results/ablation/without_val/{}/{}/results.json'

    # # for data_type in ['vis_modify', 'text2vis', 'text2vis_with_img', 'text2vis_with_code']:
    # for data_type in ['text2vis_with_code']:
    #     with open(results_path.format(model_type, data_type), 'r', encoding='utf-8') as f:
    #         results = json.load(f)

    #     results_new = []
    #     for result in results:
    #         if isinstance(result['prediction'], dict):
    #             result['prediction'] = ""
    #         results_new.append(result)
        
    #     results = results_new

    #     metrics = VisualizationMetrics()
    #     metrics_result, wrong_results, correct_results = metrics.evaluate_parallel(results, num_workers=20, use_high_level_metrics=True, use_low_level_metrics=True)

    #     with open('./results/ablation/without_val/{}/{}/metric.json'.format(model_type, data_type), 'w', encoding='utf-8') as f:
    #         json.dump(metrics_result, f, indent=4, ensure_ascii=False)
    #     with open('./results/ablation/without_val/{}/{}/wrong_results.json'.format(model_type, data_type), 'w', encoding='utf-8') as f:
    #         json.dump(wrong_results, f, indent=4, ensure_ascii=False)
    #     with open('./results/ablation/without_val/{}/{}/correct_results.json'.format(model_type, data_type), 'w', encoding='utf-8') as f:
    #         json.dump(correct_results, f, indent=4, ensure_ascii=False)

    # results_path = './results/instructing_LLM_gemini/{}/results.json'

    # for data_type in ['text2vis']:
    # # for data_type in ['text2vis', 'vis_modify', 'text2vis_with_img', 'text2vis_with_code']:
    #     with open(results_path.format(data_type), 'r', encoding='utf-8') as f:
    #         results = json.load(f)

    #     metrics = VisualizationMetrics()
    #     metrics_result, wrong_results, correct_results = metrics.evaluate_parallel(results, num_workers=20, use_high_level_metrics=True, use_low_level_metrics=True)

    #     with open('./results/instructing_LLM_gemini/{}/metric.json'.format(data_type), 'w', encoding='utf-8') as f:
    #         json.dump(metrics_result, f, indent=4, ensure_ascii=False)
    #     with open('./results/instructing_LLM_gemini/{}/wrong_result.json'.format(data_type), 'w', encoding='utf-8') as f:
    #         json.dump(wrong_results, f, indent=4, ensure_ascii=False)
    #     with open('./results/instructing_LLM_gemini/{}/correct_results.json'.format(data_type), 'w', encoding='utf-8') as f:
    #         json.dump(correct_results, f, indent=4, ensure_ascii=False)

    # results_path = './results/workflow_gpt_4o_mini/{}/results.json'

    # # for data_type in ['text2vis']:
    # for data_type in ['vis_modify', 'text2vis', 'text2vis_with_img', 'text2vis_with_code']:
    #     with open(results_path.format(data_type), 'r', encoding='utf-8') as f:
    #         results = json.load(f)

    #     metrics = VisualizationMetrics()
    #     metrics_result, wrong_results, correct_results = metrics.evaluate_parallel(results, num_workers=20, use_high_level_metrics=True, use_low_level_metrics=True)

    #     with open('./results/workflow_gpt_4o_mini/{}/metric.json'.format(data_type), 'w', encoding='utf-8') as f:
    #         json.dump(metrics_result, f, indent=4, ensure_ascii=False)
    #     with open('./results/workflow_gpt_4o_mini/{}/wrong_results.json'.format(data_type), 'w', encoding='utf-8') as f:
    #         json.dump(wrong_results, f, indent=4, ensure_ascii=False)
    #     with open('./results/workflow_gpt_4o_mini/{}/correct_results.json'.format(data_type), 'w', encoding='utf-8') as f:
    #         json.dump(correct_results, f, indent=4, ensure_ascii=False)
