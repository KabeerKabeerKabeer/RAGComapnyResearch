from graph import get_graph
from utils.logger import get_logger
import os

logger = get_logger("GraphVisualizer")


def generate_graph_visualization():
    """
    Generate Mermaid visualization of the research graph.
    Saves to assets/graph_diagram.png
    """
    try:
        logger.info("[GraphVisualizer] Generating graph visualization")
        
        # Ensure assets directory exists
        os.makedirs("assets", exist_ok=True)
        
        # Get compiled graph
        graph = get_graph()
        
        # Generate Mermaid PNG
        graph_png = graph.get_graph().draw_mermaid_png()
        
        # Save to file
        output_path = "assets/graph_diagram.png"
        with open(output_path, "wb") as f:
            f.write(graph_png)
        
        logger.info(f"[GraphVisualizer] Graph saved to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"[GraphVisualizer] Failed to generate graph: {str(e)}")
        return None


if __name__ == "__main__":
    # Generate visualization when run directly
    result = generate_graph_visualization()
    if result:
        print(f"✅ Graph visualization saved to: {result}")
    else:
        print("❌ Failed to generate graph visualization")
