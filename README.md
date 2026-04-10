## MultiVis-Agent: A Multi-Agent Framework with Logic Rules for Reliable and Comprehensive Cross-Modal Data Visualization

[![arXiv](https://img.shields.io/badge/arXiv-2601.18320-b31b1b.svg)](https://arxiv.org/abs/2601.18320)

MultiVis-Agent is a multi-agent framework with explicit logic rules for **reliable, comprehensive cross-modal data visualization**, supporting inputs such as natural language, code, and images. This repository contains both the research artifact for the SIGMOD 2026 paper and the interactive demo artifact presented at SIGMOD 2026 Demo. It also provides a **web-based demonstration** and **video presentation** of MultiVis-Agent, **MultiVis-Bench**, a benchmark for text-to-vis and visualization modification tasks, and an automatic **metric suite** for visualization quality.

## Publications

- **SIGMOD 2026 (Research Track)**: *MultiVis-Agent: A Multi-Agent Framework with Logic Rules for Reliable and Comprehensive Cross-Modal Data Visualization*
- **SIGMOD 2026 (Demonstration Track)**: *Demonstration of MultiVis-Agent: Interactively Generating Reliable Visualizations via Logic-Rule Agents*

## Demonstration
https://github.com/user-attachments/assets/b9304f0c-2d9e-4286-ba5a-fcc4f8bfeea6

## Repository Overview

- **`MultiVis-Agent/`**: Core multi-agent system (coordinator, tool manager, config, database/query and validation agents).
- **`MultiVis-Agent_demo/`**: Front-end of multi-agent system.
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

Edit `MultiVis-Agent/utils/Config.py`, `MultiVis-Agent_demo/vis_system/utils/Config.py` and replace the placeholder `"xxx"` values in `MODEL_CONFIGS` with your own API keys and endpoints.

## Quick Start

- **Run a sample visualization generation case**

```bash
python run_system.py
```

The script creates log and temporary folders and runs a sample item through the `CoordinatorAgent`, logging intermediate steps and final visualization code.

- **Run Front-end of multi-agent system**

```bash
cd MultiVis-Agent_demo
python app.py
```

The script starts the frontend on a local port and users can interact with multi-agent system on the web page.

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
- For the databases in `MultiVis-Bench/database/`, download the Spider dataset from [Google Drive](https://drive.google.com/file/d/1403EGqzIDoHMdQF4c9Bkyl7dZLZ5Wt6J/view) and extract **all database files** into the `MultiVis-Bench/database/` directory.

## License

- Source code in this repository is released under the **MIT License**. This includes the framework under `MultiVis-Agent/`, metric scripts, top-level runnable scripts, and Python reference implementations under `MultiVis-Bench/code/` and `MultiVis-Bench/vis_modify/`. See [LICENSE](LICENSE).
- Benchmark data and annotations distributed with this repository are released under **CC BY 4.0**. This includes the JSON benchmark files under `MultiVis-Bench/` and other benchmark assets distributed with the repository unless otherwise noted. See [LICENSE-DATA](LICENSE-DATA).
- Third-party resources that must be downloaded separately, including the Spider databases placed under `MultiVis-Bench/database/`, are **not** covered by the licenses above and remain subject to their original licenses and terms.

## Citation

If you find this project useful in your research, please cite:

```bibtex
@article{lu2026multivis,
  author    = {Lu, Jinwei and Song, Yuanfeng and Zhang, Chen and Wong, Raymond Chi-Wing},
  title     = {MultiVis-Agent: A Multi-Agent Framework with Logic Rules for Reliable and Comprehensive Cross-Modal Data Visualization},
  journal   = {Proc. ACM Manag. Data},
  volume    = {4},
  number    = {1},
  articleno = {56},
  year      = {2026},
  month     = {feb},
  publisher = {ACM},
  doi       = {10.1145/3786670}
}

@inproceedings{lu2026demonstration,
  title={Demonstration of MultiVis-Agent: Interactively Generating Reliable Visualizations via Logic-Rule Agents},
  author={Lu, Jinwei and Lu, Jiawei and Zhang, Chen and Song, Yuanfeng and Wong, Raymond Chi-Wing},
  booktitle={Companion of the 2026 International Conference on Management of Data},
  year={2026}
}
```
