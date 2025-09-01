🔧 Project 3: Microgrid Simulation with Pandapower

Goal: Model a 5-bus power grid with solar generation and a battery storage system. You'll analyze power flow under different conditions.

microgrid_simulation/
├── data/
│   └── component_parameters.csv
├── scripts/
│   ├── build_microgrid.py
│   └── scenario_analysis.py
├── results/
│   └── power_flow_results/
└── README.md

🚀 Step-by-Step Implementation
1. Build a Simple 5-Bus Power Grid

We'll create a minimal grid with:

    5 buses (nodes)

    1 external grid connection (slack bus)

    1 load

    1 solar generator

    1 battery storage unit

    Lines connecting them


Startup
1. python -m venv .venv
2. .\.venv\Scripts\Activate.ps1
3. pip install -r requirements.txt

