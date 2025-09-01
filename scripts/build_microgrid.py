import pandapower as pp
import pandapower.plotting as plot
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import networkx as nx
import warnings


# Create a new power grid
net = pp.create_empty_network()

# Add buses (nodes)
bus1 = pp.create_bus(net, vn_kv=20.0, name="Bus 1")
bus2 = pp.create_bus(net, vn_kv=20.0, name="Bus 2")
bus3 = pp.create_bus(net, vn_kv=20.0, name="Bus 3")
bus4 = pp.create_bus(net, vn_kv=20.0, name="Bus 4")
bus5 = pp.create_bus(net, vn_kv=20.0, name="Bus 5")

# Create external grid connection (slack bus) at Bus 1
pp.create_ext_grid(net, bus=bus1, vm_pu=1.0, name="Grid Connection")

# Add load to bus 3
pp.create_load(net, bus=bus3, p_mw=2.0, name="Load")

# Add solar generator at bus 2
pp.create_sgen(net, bus=bus2, p_mw=3.0, name="Solar Generator") #

# Add battery storage unit at bus 4
pp.create_storage(net, bus=bus4, p_mw=1.0, max_e_mwh=5.0, min_e_mwh=0.5, soc_pu=0.5, name="Battery Storage")

# Add lines
pp.create_line_from_parameters(net, from_bus=bus1, to_bus=bus2, length_km=10.0, r_ohm_per_km=0.05, x_ohm_per_km=0.1, c_nf_per_km=100, max_i_ka=10.0, name="Line 1-2")
pp.create_line_from_parameters(net, from_bus=bus2, to_bus=bus3, length_km=5.0, r_ohm_per_km=0.05, x_ohm_per_km=0.1, c_nf_per_km=100, max_i_ka=10.0, name="Line 2-3")
pp.create_line_from_parameters(net, from_bus=bus3, to_bus=bus4, length_km=3.0, r_ohm_per_km=0.05, x_ohm_per_km=0.1, c_nf_per_km=100, max_i_ka=10.0, name="Line 3-4")
pp.create_line_from_parameters(net, from_bus=bus4, to_bus=bus5, length_km=4.0, r_ohm_per_km=0.05, x_ohm_per_km=0.1, c_nf_per_km=100, max_i_ka=10.0, name="Line 4-5")

print("Network created successfully!")
print(net)

# Run power flow analysis
pp.runpp(net)

# Display results
print("Power flow results:")
print(net.res_bus)  # Bus voltages and angles
print(net.res_line)  # Line loading
print(net.res_load)  # Load results
print(net.res_sgen)  # Solar generator results
print(net.res_storage)  # Battery results


# Create interactive plot with Plotly
try:
    # Suppress Plotly's debug output
    pio.templates.default = "none"
    pio.renderers.default = "browser"

    # Suppress specific warnings if needed
    warnings.filterwarnings('ignore', category=UserWarning, module='plotly')
    
    # Create a figure with two subplots
    fig = make_subplots(rows=1, cols=1, subplot_titles=("Microgrid Topology",))
    
    # Get node positions using spring layout
    
    # Create a networkx graph from the pandapower network
    graph = nx.Graph()
    
    # Add nodes
    for idx, row in net.bus.iterrows():
        graph.add_node(idx, **row.to_dict())
    
    # Add edges
    for idx, row in net.line.iterrows():
        graph.add_edge(row['from_bus'], row['to_bus'], **row.to_dict())
    
    # Use spring layout for better node positioning
    pos = nx.spring_layout(graph, k=1.0, iterations=50)
    
    # Add edges
    edge_x = []
    edge_y = []
    for edge in graph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')
    
    # Add nodes
    node_x = []
    node_y = []
    node_text = []
    for node in graph.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_info = f"Bus {node}<br>"
        if node in net.bus.index:
            node_info += f"Voltage: {net.res_bus.vm_pu[node]:.3f} p.u.<br>"
            node_info += f"Angle: {net.res_bus.va_degree[node]:.2f}°"
        node_text.append(node_info)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=[f"{i}" for i in range(len(node_x))],
        textposition="top center",
        hoverinfo='text',
        hovertext=node_text,
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=20,
            color=[net.res_bus.vm_pu[i] if i in net.bus.index else 1.0 for i in range(len(node_x))],
            colorbar=dict(
                thickness=15,
                title='Voltage (p.u.)',
                xanchor='left',
                title_side='right'
            ),
            line_width=2))
    
    # Add the traces to the figure
    fig.add_trace(edge_trace, row=1, col=1)
    fig.add_trace(node_trace, row=1, col=1)
    
    # Update layout
    fig.update_layout(
        title='Microgrid Topology with Power Flow Results',
        title_x=0.5,
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20,l=5,r=5,t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=800
    )
    
    # Save the interactive plot
    fig.write_html("results/microgrid_topology.html")
    
    # Show the plot
    fig.show()
    
except ImportError:
    print("Plotly not available. Using matplotlib instead.")
    import matplotlib.pyplot as plt
    plt.figure(figsize=(12, 8))
    plot.simple_plot(net)
    plt.title("Microgrid Topology with Power Flow Results", fontsize=14, pad=20)
    plt.tight_layout()
    plt.savefig("../results/microgrid_topology.png", dpi=300, bbox_inches='tight')
    plt.show()

# Print a summary of the results
print("\nPower Flow Summary:")
print("-" * 50)
print("Bus Voltages (p.u.):")
print(net.res_bus.vm_pu.round(4))
print("\nLine Loading (%):")
print((net.res_line.loading_percent).round(2))
print("\nGeneration (MW):")
print(f"Solar Generation: {net.res_sgen.p_mw.values[0]:.2f} MW")
print(f"Grid Import: {net.res_ext_grid.p_mw.values[0]:.2f} MW")
