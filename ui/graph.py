import plotly.graph_objects as go
import json
from typing import Dict, List

def plot_confidence_scores(results_path: str = "results.json") -> go.Figure:
    """Generate an interactive bar chart of model confidence scores."""
    # Load results data
    with open(results_path) as f:
        data = json.load(f)
    
    # Extract confidence scores and model names
    model_confidences: Dict[str, List[float]] = {}
    for response in data["model_responses"]:
        model = response["model"]
        confidence = response["confidence"]
        if model not in model_confidences:
            model_confidences[model] = []
        model_confidences[model].append(confidence)
    
    # Calculate average confidence per model
    model_averages = {
        model: sum(confidences)/len(confidences)
        for model, confidences in model_confidences.items()
    }
    
    # Sort models by average confidence
    sorted_models = sorted(
        model_averages.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    # Create color scale
    max_confidence = max(model_averages.values())
    colors = []
    for model, avg in sorted_models:
        if avg >= max_confidence * 0.95:  # Top 5% in green
            colors.append("#2ecc71")
        elif avg >= max_confidence * 0.85:  # Above average in light green
            colors.append("#7fcdbb")
        else:  # Below average in red
            colors.append("#e74c3c")
    
    # Create figure
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=[model for model, _ in sorted_models],
        y=[avg for _, avg in sorted_models],
        marker_color=colors,
        text=[f"Avg: {avg:.2%}" for _, avg in sorted_models],
        textposition="auto",
        hovertext=[
            f"<b>{model}</b><br>"
            f"Instances: {len(model_confidences[model])}<br>"
            f"Min: {min(model_confidences[model]):.2%}<br>"
            f"Max: {max(model_confidences[model]):.2%}"
            for model, _ in sorted_models
        ],
        hoverinfo="text"
    ))
    
    fig.update_layout(
        title="Model Confidence Scores Comparison",
        xaxis_title="Models",
        yaxis_title="Average Confidence",
        yaxis=dict(tickformat=".0%"),
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(
            bgcolor="white",
            font_size=14
        )
    )
    
    return fig
