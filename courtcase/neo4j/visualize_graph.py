"""
Visualize CPC Knowledge Graph
Creates both interactive HTML and static PNG visualizations
"""
from neo4j import GraphDatabase
from pyvis.network import Network
import networkx as nx
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

NEO4J_URL = os.getenv("NEO4J_URL")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# Validate required environment variables
if not all([NEO4J_URL, NEO4J_USERNAME, NEO4J_PASSWORD]):
    raise ValueError(
        "Missing required environment variables. Please set:\n"
        "  - NEO4J_URL\n"
        "  - NEO4J_USERNAME\n"
        "  - NEO4J_PASSWORD\n"
        "in your .env file or environment."
    )


class CPCGraphVisualizer:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

        # Color scheme for different node types
        self.node_colors = {
            'Case': '#FF6B6B',         # Red
            'Judge': '#4ECDC4',        # Teal
            'Party': '#95E1D3',        # Light teal
            'Court': '#F38181',        # Pink
            'Section': '#FFD93D',      # Yellow
            'Statute': '#6C5CE7',      # Purple
            'Principle': '#A8E6CF',    # Light green
            'Topic': '#FF8B94',        # Light red
        }

        self.node_shapes = {
            'Case': 'star',
            'Judge': 'dot',
            'Party': 'dot',
            'Court': 'triangle',
            'Section': 'box',
            'Statute': 'database',
            'Principle': 'diamond',
            'Topic': 'ellipse',
        }

    def fetch_graph_data(self):
        """Fetch all nodes and relationships from Neo4j"""
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Get all nodes
            nodes_result = session.run("""
                MATCH (n)
                WHERE labels(n)[0] IN ['Case', 'Judge', 'Party', 'Court', 'Section', 'Statute', 'Principle', 'Topic']
                RETURN id(n) as id, labels(n)[0] as label, properties(n) as props
            """)

            nodes = []
            for record in nodes_result:
                node_data = {
                    'id': record['id'],
                    'label': record['label'],
                    'props': record['props']
                }
                nodes.append(node_data)

            # Get all relationships
            rels_result = session.run("""
                MATCH (source)-[r]->(target)
                WHERE labels(source)[0] IN ['Case', 'Judge', 'Party', 'Court', 'Section', 'Statute', 'Principle', 'Topic']
                  AND labels(target)[0] IN ['Case', 'Judge', 'Party', 'Court', 'Section', 'Statute', 'Principle', 'Topic']
                RETURN id(source) as source, id(target) as target, type(r) as type, properties(r) as props
            """)

            relationships = []
            for record in rels_result:
                rel_data = {
                    'source': record['source'],
                    'target': record['target'],
                    'type': record['type'],
                    'props': record['props']
                }
                relationships.append(rel_data)

            return nodes, relationships

    def create_html_visualization(self, nodes, relationships):
        """Create interactive HTML visualization using pyvis"""
        print("\n🎨 Creating interactive HTML visualization...")

        # Initialize network
        net = Network(
            height='800px',
            width='100%',
            bgcolor='#1a1a2e',
            font_color='white',
            directed=True
        )

        # Configure physics for better layout
        net.barnes_hut(
            gravity=-5000,
            central_gravity=0.3,
            spring_length=200,
            spring_strength=0.001
        )

        # Add nodes
        for node in nodes:
            node_id = node['id']
            node_label = node['label']
            props = node['props']

            # Get display name
            if 'name' in props:
                display_name = props['name']
            elif 'citation' in props:
                display_name = props['citation']
            elif 'section_id' in props:
                display_name = props['section_id']
            else:
                display_name = node_label

            # Truncate long names
            if len(display_name) > 40:
                display_name = display_name[:37] + "..."

            # Create hover title with details
            title = f"<b>{node_label}</b><br>"
            for key, value in props.items():
                if key not in ['id']:
                    title += f"{key}: {value}<br>"

            color = self.node_colors.get(node_label, '#95a5a6')
            shape = self.node_shapes.get(node_label, 'dot')

            # Set size based on node type
            if node_label == 'Case':
                size = 30
            elif node_label in ['Section', 'Principle']:
                size = 25
            else:
                size = 20

            net.add_node(
                node_id,
                label=display_name,
                title=title,
                color=color,
                shape=shape,
                size=size
            )

        # Add edges
        for rel in relationships:
            edge_label = rel['type'].replace('_', ' ')
            title = edge_label

            if rel['props']:
                title += "<br>" + ", ".join([f"{k}: {v}" for k, v in rel['props'].items()])

            net.add_edge(
                rel['source'],
                rel['target'],
                label=edge_label,
                title=title,
                arrows='to'
            )

        # Save as HTML
        output_file = 'cpc_graph.html'
        net.save_graph(output_file)

        print(f"✓ Saved interactive visualization to: {output_file}")
        print(f"  → Open in browser to explore the graph")

        return output_file

    def create_static_visualization(self, nodes, relationships):
        """Create static PNG visualization using networkx and matplotlib"""
        print("\n🎨 Creating static PNG visualization...")

        # Create networkx graph
        G = nx.DiGraph()

        # Add nodes
        node_labels = {}
        node_colors_list = []

        for node in nodes:
            node_id = node['id']
            node_label = node['label']
            props = node['props']

            # Get display name
            if 'name' in props:
                display_name = props['name']
            elif 'citation' in props:
                display_name = props['citation']
            elif 'section_id' in props:
                display_name = props['section_id']
            else:
                display_name = node_label

            # Truncate for readability
            if len(display_name) > 20:
                display_name = display_name[:17] + "..."

            G.add_node(node_id, label=node_label, name=display_name)
            node_labels[node_id] = display_name
            node_colors_list.append(self.node_colors.get(node_label, '#95a5a6'))

        # Add edges
        edge_labels = {}
        for rel in relationships:
            G.add_edge(rel['source'], rel['target'])
            edge_labels[(rel['source'], rel['target'])] = rel['type'].replace('_', ' ')

        # Create figure
        plt.figure(figsize=(20, 16))
        plt.title("CPC Knowledge Graph - Bangladesh Legal Cases", fontsize=20, fontweight='bold', pad=20)

        # Use spring layout for better visualization
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

        # Draw nodes
        nx.draw_networkx_nodes(
            G,
            pos,
            node_color=node_colors_list,
            node_size=800,
            alpha=0.9,
            edgecolors='black',
            linewidths=1.5
        )

        # Draw edges
        nx.draw_networkx_edges(
            G,
            pos,
            edge_color='#7f8c8d',
            arrows=True,
            arrowsize=15,
            arrowstyle='->',
            width=1.5,
            alpha=0.6
        )

        # Draw labels
        nx.draw_networkx_labels(
            G,
            pos,
            node_labels,
            font_size=7,
            font_weight='bold',
            font_family='sans-serif'
        )

        # Add legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=label)
            for label, color in self.node_colors.items()
        ]
        plt.legend(handles=legend_elements, loc='upper left', fontsize=10, title="Node Types", title_fontsize=12)

        plt.axis('off')
        plt.tight_layout()

        # Save as PNG
        output_file = 'cpc_graph.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"✓ Saved static visualization to: {output_file}")

        return output_file

    def visualize(self):
        """Create all visualizations"""
        print("\n📊 Fetching graph data from Neo4j...")
        nodes, relationships = self.fetch_graph_data()

        print(f"✓ Fetched {len(nodes)} nodes and {len(relationships)} relationships")

        # Create visualizations
        html_file = self.create_html_visualization(nodes, relationships)
        png_file = self.create_static_visualization(nodes, relationships)

        print("\n" + "="*60)
        print("✅ Visualization Complete!")
        print("="*60)
        print(f"\n📁 Files created:")
        print(f"  1. {html_file} - Interactive (open in browser)")
        print(f"  2. {png_file} - Static image")
        print(f"\n💡 Tips:")
        print(f"  - Zoom and drag in HTML file to explore")
        print(f"  - Click nodes to see details")
        print(f"  - Use Neo4j Browser for Cypher queries")
        print("="*60 + "\n")

    def close(self):
        self.driver.close()


if __name__ == "__main__":
    visualizer = CPCGraphVisualizer()
    try:
        visualizer.visualize()
    finally:
        visualizer.close()
