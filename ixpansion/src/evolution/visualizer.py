"""Evolution Visualizer - Creates visual representations of module evolution."""

import json
from typing import Dict, Any, List, Optional
from .tracker import EvolutionTracker, ModuleSnapshot


class EvolutionVisualizer:
    """Creates visual representations of module evolution."""
    
    def __init__(self, tracker: EvolutionTracker):
        self.tracker = tracker
    
    def generate_ascii_lineage(self, root_module: str, max_depth: int = 5) -> str:
        """Generate ASCII representation of module lineage tree."""
        tree = self.tracker.get_lineage_tree(root_module)
        lines = []
        
        def render(node: Dict[str, Any], prefix: str = "", is_last: bool = True, depth: int = 0):
            if depth > max_depth:
                lines.append(f"{prefix}{'└── ' if is_last else '├── '}... (max depth reached)")
                return
            
            connector = "└── " if is_last else "├── "
            module_id = node["module_id"]
            history_len = node["history_length"]
            lines.append(f"{prefix}{connector}{module_id} (history: {history_len})")
            
            children = node["children"]
            for i, child in enumerate(children):
                is_last_child = (i == len(children) - 1)
                new_prefix = prefix + ("    " if is_last else "│   ")
                render(child, new_prefix, is_last_child, depth + 1)
        
        render(tree)
        return "\n".join(lines)
    
    def generate_mutation_timeline(self, module_id: str) -> str:
        """Generate a timeline visualization of module mutations."""
        history = self.tracker.get_module_history(module_id)
        if not history:
            return f"No history found for {module_id}"
        
        lines = [f"═══ Mutation Timeline: {module_id} ═══", ""]
        
        for i, snap in enumerate(history):
            marker = "●" if i == 0 else "→"
            parent = f" ← {snap.parent_module}" if snap.parent_module else ""
            lines.append(
                f"  {marker} Wave {snap.wave} [{snap.mutation_type}]{parent}"
            )
            lines.append(f"     Hash: {snap.hash_signature}")
            
            # Show key data changes
            if i > 0:
                prev = history[i-1]
                if snap.hash_signature != prev.hash_signature:
                    lines.append("     ⚡ DATA CHANGED")
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_wave_heatmap(self, start_wave: int = 401, end_wave: int = 410) -> str:
        """Generate a heatmap of module activity across waves."""
        lines = ["═══ Wave Activity Heatmap ═══", ""]
        
        # Collect all waves and modules
        wave_modules = {}
        for module_id, snapshots in self.tracker.snapshots.items():
            for snap in snapshots:
                if start_wave <= snap.wave <= end_wave:
                    if snap.wave not in wave_modules:
                        wave_modules[snap.wave] = []
                    wave_modules[snap.wave].append(module_id)
        
        # Create heatmap
        for wave in range(start_wave, end_wave + 1):
            modules = wave_modules.get(wave, [])
            activity = "█" * min(len(modules), 20)
            meta = self.tracker.wave_metadata.get(wave, {})
            meta_str = f" ({meta.get('theme', 'unknown')})" if meta else ""
            lines.append(f"  Wave {wave:4d}: {activity} [{len(modules)} modules]{meta_str}")
        
        return "\n".join(lines)
    
    def generate_html_dashboard(self, output_path: str = "evolution_dashboard.html") -> str:
        """Generate an interactive HTML dashboard."""
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Module Evolution Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #1a1a2e; color: #eaeaea; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #00d9ff; text-align: center; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }
        .card { background: #16213e; border-radius: 10px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        .card h2 { color: #ff6b6b; margin-top: 0; }
        canvas { max-height: 300px; }
        .module-list { max-height: 300px; overflow-y: auto; }
        .module-item { padding: 8px; border-bottom: 1px solid #2a2a4a; }
        .module-item:last-child { border-bottom: none; }
        .wave-badge { background: #0f3460; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; }
        .mutation-badge { background: #e94560; padding: 2px 6px; border-radius: 3px; font-size: 0.7em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧬 Module Evolution Dashboard</h1>
        
        <div class="grid">
            <div class="card">
                <h2>📊 Wave Activity</h2>
                <canvas id="waveChart"></canvas>
            </div>
            
            <div class="card">
                <h2>🔬 Mutation Types</h2>
                <canvas id="mutationChart"></canvas>
            </div>
            
            <div class="card">
                <h2>📈 Module Count per Wave</h2>
                <canvas id="countChart"></canvas>
            </div>
            
            <div class="card">
                <h2>🧬 Lineage Explorer</h2>
                <div id="lineageTree" class="module-list"></div>
            </div>
        </div>
    </div>
    
    <script>
        // Data injected from Python
        const EVOLUTION_DATA = %s;
        
        // Initialize charts
        const waveLabels = Object.keys(EVOLUTION_DATA.wave_activity).sort((a,b) => a-b);
        const waveCounts = waveLabels.map(w => EVOLUTION_DATA.wave_activity[w].length);
        
        new Chart(document.getElementById('waveChart'), {
            type: 'bar',
            data: {
                labels: waveLabels,
                datasets: [{
                    label: 'Modules per Wave',
                    data: waveCounts,
                    backgroundColor: 'rgba(0, 217, 255, 0.6)',
                    borderColor: 'rgba(0, 217, 255, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: { y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.1)' } } }
            }
        });
        
        // Mutation types chart
        const mutTypes = EVOLUTION_DATA.mutation_types;
        new Chart(document.getElementById('mutationChart'), {
            type: 'doughnut',
            data: {
                labels: Object.keys(mutTypes),
                datasets: [{
                    data: Object.values(mutTypes),
                    backgroundColor: ['#ff6b6b', '#4ecdc4', '#ffe66d', '#95e1d3', '#f38181', '#aa96da']
                }]
            },
            options: { responsive: true }
        });
        
        // Module count per wave
        new Chart(document.getElementById('countChart'), {
            type: 'line',
            data: {
                labels: waveLabels,
                datasets: [{
                    label: 'Total Modules',
                    data: waveCounts,
                    borderColor: '#ff6b6b',
                    fill: false,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                scales: { y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.1)' } } }
            }
        });
        
        // Lineage tree
        const treeContainer = document.getElementById('lineageTree');
        function renderTree(node, depth = 0) {
            const div = document.createElement('div');
            div.className = 'module-item';
            div.style.paddingLeft = (depth * 20) + 'px';
            div.innerHTML = `<span class="wave-badge">${node.module_id}</span> 
                           <span class="mutation-badge">${node.history_length} versions</span>`;
            treeContainer.appendChild(div);
            if (node.children) {
                node.children.forEach(child => renderTree(child, depth + 1));
            }
        }
        
        // Render first lineage tree
        if (EVOLUTION_DATA.lineage_trees.length > 0) {
            renderTree(EVOLUTION_DATA.lineage_trees[0]);
        }
    </script>
</body>
</html>""" % json.dumps(self._prepare_dashboard_data(), indent=2)
        
        with open(output_path, 'w') as f:
            f.write(html)
        
        return output_path
    
    def _prepare_dashboard_data(self) -> Dict[str, Any]:
        """Prepare data for HTML dashboard."""
        wave_activity = {}
        mutation_types = {}
        all_modules = set()
        
        for module_id, snapshots in self.tracker.snapshots.items():
            for snap in snapshots:
                all_modules.add(module_id)
                if snap.wave not in wave_activity:
                    wave_activity[snap.wave] = []
                wave_activity[snap.wave].append(module_id)
                
                mutation_types[snap.mutation_type] = mutation_types.get(snap.mutation_type, 0) + 1
        
        # Build lineage trees for root modules
        root_modules = set()
        for module_id in all_modules:
            # Check if this module has a parent
            has_parent = False
            for snap in self.tracker.snapshots.get(module_id, []):
                if snap.parent_module:
                    has_parent = True
                    break
            if not has_parent:
                root_modules.add(module_id)
        
        lineage_trees = []
        for root in list(root_modules)[:5]:  # Limit to 5 trees
            lineage_trees.append(self.tracker.get_lineage_tree(root))
        
        return {
            "wave_activity": wave_activity,
            "mutation_types": mutation_types,
            "total_modules": len(all_modules),
            "lineage_trees": lineage_trees,
        }
    
    def generate_mermaid_diagram(self, root_module: str) -> str:
        """Generate a Mermaid diagram for module lineage."""
        tree = self.tracker.get_lineage_tree(root_module)
        lines = ["```mermaid", "graph TD"]
        
        def add_nodes(node: Dict[str, Any], parent_id: str = None):
            node_id = node["module_id"].replace("-", "_").replace(".", "_")
            label = f"{node['module_id']}<br/>({node['history_length']} versions)"
            lines.append(f'    {node_id}["{label}"]')
            
            if parent_id:
                lines.append(f'    {parent_id} --> {node_id}')
            
            for child in node.get("children", []):
                add_nodes(child, node_id)
        
        add_nodes(tree)
        lines.append("```")
        return "\n".join(lines)


def create_visualizer(tracker: EvolutionTracker) -> EvolutionVisualizer:
    """Factory function to create visualizer."""
    return EvolutionVisualizer(tracker)
