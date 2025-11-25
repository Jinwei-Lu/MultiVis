## MultiVis-Agent: A Multi-Agent Framework with Logic Rules for Reliable and Comprehensive Cross-Modal Data Visualization

MultiVis-Agent is a multi-agent framework with explicit logic rules for **reliable, comprehensive cross-modal data visualization**, supporting inputs such as natural language, code, and images. This repository also provides **MultiVis-Bench**, a benchmark for text-to-vis and visualization modification tasks, and an automatic **metric suite** for visualization quality.

## Repository Overview

- **`MultiVis-Agent/`**: Core multi-agent system (coordinator, tool manager, config, database/query and validation agents).
- **`MultiVis-Bench/`**: Benchmark datasets and reference implementations for text-to-vis and vis-modify tasks.
- **`metric/`**: Visualization evaluation metrics used in the paper.
- **`run_system.py`**: Example entry script to run the multi-agent visualization system on a sample.
- **`run_metric.py`**: Script to compute metrics over saved results.

## Installation

- **Set up environment**

```bash
git clone https://github.com/Jinwei-Lu/MultiVis.git
cd MultiVis
pip install -r requirements.txt
```

- **Configure LLM APIs**

Edit `MultiVis-Agent/utils/Config.py` and replace the placeholder `"xxx"` values in `MODEL_CONFIGS` with your own API keys and endpoints.

## Quick Start

- **Run a sample visualization generation case**

```bash
python run_system.py
```

The script creates log and temporary folders and runs a sample item through the `CoordinatorAgent`, logging intermediate steps and final visualization code.

- **Evaluate generated results**

Organize your results under `./results/{method_type}/{model_type}/{data_type}/results.json` following the structure in `run_metric.py`, then run:

```bash
python run_metric.py
```

This produces `metric.json`, `wrong_results.json`, and `correct_results.json` for each data type.

## Benchmark Data

MultiVis-Bench provides benchmark files:

- **`text2vis.json`**, **`vis_modify.json`**, **`text2vis_with_img.json`**, **`text2vis_with_code.json`** under `MultiVis-Bench/`.
- **`database/`** and **`img/`** subdirectories with databases and images used in benchmark tasks.

## Citation

If you find this project useful in your research, please cite:

```bibtex
@inproceedings{lu2026multivisagent,
  title     = {MultiVis-Agent: A Multi-Agent Framework with Logic Rules for Reliable and Comprehensive Cross-Modal Data Visualization},
  author    = {Lu, Jinwei and Song, Yuanfeng and Zhang, Chen and Wong, Raymond Chi-Wing},
  booktitle = {Proceedings of the ACM SIGMOD International Conference on Management of Data (SIGMOD)},
  year      = {2026}
}
```


