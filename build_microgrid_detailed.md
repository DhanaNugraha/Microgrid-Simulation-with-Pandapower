# 🏗️ Detailed Explanation of build_microgrid.py

## 📚 Table of Contents
1. [Introduction](#introduction)
2. [Importing Libraries](#importing-libraries)
3. [Creating the Power Grid](#creating-the-power-grid)
4. [Adding Buses (Nodes)](#adding-buses-nodes)
5. [Adding Power Sources and Loads](#adding-power-sources-and-loads)
6. [Connecting Components with Lines](#connecting-components-with-lines)
7. [Running Power Flow Analysis](#running-power-flow-analysis)
8. [Visualizing the Results](#visualizing-the-results)
9. [Understanding the Output](#understanding-the-output)

## Introduction
This script simulates a small power grid using the `pandapower` library. It creates a microgrid with multiple components, performs power flow analysis, and visualizes the results.

## Importing Libraries
```python
import pandapower as pp
import pandapower.plotting as plot
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import networkx as nx
import warnings
```
- `pandapower`: Main library for power system modeling and analysis
- `matplotlib` and `plotly`: For visualization
- `networkx`: For graph-based network analysis
- `warnings`: To handle runtime warnings

## Creating the Power Grid
```python
net = pp.create_empty_network()
```
Creates an empty power grid network to which we'll add components.

## Adding Buses (Nodes)

### What are Buses?
Buses (or busbars) are the connection points in a power system where multiple electrical components meet. Think of them as the 'junctions' or 'hubs' of the power grid where electricity can be distributed in different directions.

### Bus Parameters
```python
# Add buses (nodes)
bus1 = pp.create_bus(net, vn_kv=20.0, name="Bus 1")
bus2 = pp.create_bus(net, vn_kv=20.0, name="Bus 2")
bus3 = pp.create_bus(net, vn_kv=20.0, name="Bus 3")
bus4 = pp.create_bus(net, vn_kv=20.0, name="Bus 4")
bus5 = pp.create_bus(net, vn_kv=20.0, name="Bus 5")
```
- **Function**: `pp.create_bus()` creates a new bus in the network
- **Parameters**:
  - `net`: The power grid network object
  - `vn_kv=20.0`: Nominal voltage of 20 kilovolts (kV)
  - `name`: Human-readable identifier for the bus
- **Key Points**:
  - Each bus is like a 'meeting point' for electrical connections
  - The same voltage level (20kV) is maintained across all buses in this example
  - Buses are automatically assigned unique numeric IDs (0, 1, 2, etc.)

## Adding the Grid Connection

### What is a Grid Connection?
A grid connection links our microgrid to the main power grid, acting as both a source and sink of power. It's like connecting your home's electrical system to the city's power supply.

### The Slack Bus Concept
The 'slack bus' is a special bus that:
- Maintains a constant voltage (1.0 per unit in this case)
- Balances any power mismatch in the system
- Acts as the reference point (0° phase angle) for all voltage calculations

### Code Implementation
```python
# Create external grid connection (slack bus) at Bus 1
pp.create_ext_grid(net, bus=bus1, vm_pu=1.0, name="Grid Connection")
```
- **Function**: `pp.create_ext_grid()` connects to the external power grid
- **Parameters**:
  - `net`: The power grid network
  - `bus=bus1`: Connects to Bus 1 (the first bus we created)
  - `vm_pu=1.0`: Sets voltage to 1.0 per unit (100% of 20kV = 20kV)
  - `name`: Descriptive name for the connection
- **Why Bus 1?**: The first bus is typically chosen as the slack bus by convention, but any bus could be used

## Adding Power Sources and Loads

### Understanding Power System Components

#### 1. Loads
- **What is it?** A device that consumes electrical power (like homes, factories, etc.)
- **In our grid**: A 2 MW load connected to Bus 3

```python
# Add load to bus 3
pp.create_load(net, bus=bus3, p_mw=2.0, name="Load")
```
- `p_mw=2.0`: Consumes 2 megawatts of active power
- Negative values would indicate power generation

#### 2. Solar Generator
- **What is it?** A renewable energy source that converts sunlight to electricity
- **In our grid**: A 3 MW solar farm connected to Bus 2

```python
# Add solar generator at bus 2
pp.create_sgen(net, bus=bus2, p_mw=3.0, name="Solar Generator")
```
- `p_mw=3.0`: Generates 3 megawatts of active power
- `sgen` stands for 'static generator' - used for renewable sources

#### 3. Battery Storage
- **What is it?** Energy storage that can both absorb and supply power
- **In our grid**: A battery system at Bus 4 with specific characteristics

```python
# Add battery storage unit at bus 4
pp.create_storage(net, bus=bus4, p_mw=1.0, max_e_mwh=5.0, 
                 min_e_mwh=0.5, soc_pu=0.5, name="Battery Storage")
```
- `p_mw=1.0`: Can charge/discharge at 1 MW rate
- `max_e_mwh=5.0`: Maximum energy storage of 5 MWh
- `min_e_mwh=0.5`: Minimum energy to always keep in storage
- `soc_pu=0.5`: Initial state of charge (50% full)

### Power Flow Balance
- The solar generator (3 MW) produces more than the load consumes (2 MW)
- The excess 1 MW can be used to charge the battery or flow back to the grid
- The grid connection at Bus 1 will balance any power mismatch

## Connecting Components with Lines

### What are Power Lines?
Power lines (or transmission/distribution lines) are the 'wires' that carry electricity between different parts of the grid. They have electrical properties that affect power flow.

### Line Parameters Explained
```python
# Add lines between buses
pp.create_line_from_parameters(net, from_bus=bus1, to_bus=bus2, 
                             length_km=10.0, r_ohm_per_km=0.05, 
                             x_ohm_per_km=0.1, c_nf_per_km=100, 
                             max_i_ka=10.0, name="Line 1-2")
```
- **Function**: Creates an electrical connection between two buses
- **Key Parameters**:
  - `from_bus`, `to_bus`: Which buses to connect
  - `length_km=10.0`: Physical length of the line (10 kilometers)
  - `r_ohm_per_km=0.05`: Resistance (Ω/km) - causes real power loss as heat
  - `x_ohm_per_km=0.1`: Reactance (Ω/km) - affects voltage drop and power factor
  - `c_nf_per_km=100`: Capacitance (nanoFarads/km) - affects voltage regulation
  - `max_i_ka=10.0`: Maximum current (kiloAmperes) before overload

### Why These Values Matter
- **Resistance (R)**: Causes real power loss (I²R losses)
- **Reactance (X)**: Causes voltage drop and phase shift
- **Capacitance (C)**: Affects voltage regulation, especially in long lines
- **Current Rating**: Determines how much power can safely flow

### Example Calculation
For Line 1-2 (10 km):
- Total resistance = 10 km × 0.05 Ω/km = 0.5 Ω
- Total reactance = 10 km × 0.1 Ω/km = 1.0 Ω
- These values affect how much power can be transferred and how much is lost as heat

## Running Power Flow Analysis

### What is Power Flow Analysis?
Power flow analysis calculates the steady-state operating conditions of a power system, including:
- Voltage magnitude and angle at each bus
- Real and reactive power flows in all lines
- Power losses in the system

### The Power Flow Solver
```python
# Run power flow analysis
pp.runpp(net)
```
- **Function**: `pp.runpp()` performs the power flow calculation
- **What it does**:
  1. Solves a system of nonlinear equations
  2. Finds the voltage magnitude and angle at each bus
  3. Calculates power flows in all lines
  4. Determines power generation/consumption at each bus

### Key Concepts in Power Flow
1. **Voltage Profile**: How voltage varies across the network
2. **Power Balance**: Generation must equal load plus losses
3. **Line Loading**: Percentage of maximum capacity being used
4. **Power Factors**: Ratio of real power to apparent power

### Understanding the Results
After running `pp.runpp(net)`, the results are stored in the `net` object:
- `net.res_bus`: Bus voltages and angles
- `net.res_line`: Power flows in lines
- `net.res_load`: Load power consumption
- `net.res_sgen`: Power generation from static generators
- `net.res_storage`: Battery state and power flows

## Visualizing the Results
### Interactive Plot (Plotly)
1. Creates a network graph using NetworkX
2. Calculates node positions using a spring layout
3. Creates an interactive visualization with:
   - Nodes representing buses
   - Edges representing power lines
   - Color coding for voltage levels
   - Hover information for detailed data

### Fallback Plot (Matplotlib)
If Plotly is not available, falls back to a simpler matplotlib plot.

## Understanding the Output
### Numerical Results
- **Bus Voltages**: Shows voltage magnitude (p.u.) and angle (degrees) at each bus
- **Line Loading**: Percentage of maximum capacity used in each line
- **Power Flow**: Active and reactive power flow in each line
- **Generation**: Power output from each source

### Visual Output
1. `results/microgrid_topology.html`: Interactive plot (if Plotly is available)
2. `results/microgrid_topology.png`: Static plot (if using matplotlib)

## Key Concepts
1. **Per Unit (p.u.) System**: Normalized values (1.0 = 100% of nominal)
2. **Slack Bus**: Reference bus that balances power in the system
3. **Power Flow**: Calculation of voltage magnitudes and angles in the grid
4. **Line Loading**: Percentage of maximum capacity being used

## Modifying the System
You can modify various parameters to see their effects:
- Change load values (`p_mw` in `create_load`)
- Adjust generation (`p_mw` in `create_sgen`)
- Modify line parameters (resistance, reactance)
- Change the battery's state of charge or capacity

## Troubleshooting
- Ensure all required packages are installed (`pandapower`, `plotly`, `networkx`)
- Check that the `results` directory exists or will be created
- Verify that all bus indices are valid when connecting components
