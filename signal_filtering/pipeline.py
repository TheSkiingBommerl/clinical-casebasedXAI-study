"""
Provide pipeline used in filter_all_signals. When running this file plots will be shown in the browser comparing the unfiltered and filtered signal to each other
"""

from signal_filtering.filters import butterworth_high, butterworth_low, notch
from database.useful_queries import get_ecg_signals
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import math

def render_figures_overlay(fs, leads: list, names: list, cols: int = 2):
    """
    This function was created by Sonnet 4.6
    """
    SAMPLING_RATE = fs
    OVERLAY_COLORS = [
        "#ff4d4d",  # red
        "#4d9fff",  # blue
        "#ffaa00",  # amber
        "#cc44ff",  # purple
        "#ff66cc",  # pink
        "#00ccff",  # cyan
        "#ff8800",  # orange
    ]

    reference = leads[0]
    reference_name = names[0]
    t_ref = [s / SAMPLING_RATE for s in range(len(reference))]

    n = len(leads)
    rows = math.ceil(n / cols)

    fig = make_subplots(
        rows=rows, cols=cols,
        subplot_titles=names,
        vertical_spacing=0.15,
        horizontal_spacing=0.05
    )

    for i, (lead, name) in enumerate(zip(leads, names)):
        row = (i // cols) + 1
        col = (i % cols) + 1
        t = [s / SAMPLING_RATE for s in range(len(lead))]

        # Always draw the reference signal first (background layer)
        fig.add_trace(
            go.Scatter(
                x=t_ref,
                y=reference,
                mode="lines",
                line=dict(color="#00ff88", width=1.2),
                name=reference_name,
                legendgroup="reference",
                showlegend=(i == 0),  # only one legend entry for the reference
                opacity=0.5 if i != 0 else 1.0,  # dim reference when it's not the focus
            ),
            row=row, col=col
        )

        # Overlay the current signal (skip for index 0 — it IS the reference)
        if i != 0:
            overlay_color = OVERLAY_COLORS[(i - 1) % len(OVERLAY_COLORS)]
            fig.add_trace(
                go.Scatter(
                    x=t,
                    y=lead,
                    mode="lines",
                    line=dict(color=overlay_color, width=1.2),
                    name=name,
                    legendgroup=name,
                    showlegend=True,
                ),
                row=row, col=col
            )

    num_samples = max(len(lead) for lead in leads)

    fig.update_layout(
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font_color="white",
        height=300 * rows,
        showlegend=True,
        legend=dict(
            bgcolor="#1a1f2e",
            bordercolor="#2d3748",
            borderwidth=1,
            font=dict(color="white", size=11),
        ),
        margin=dict(l=40, r=20, t=40, b=40),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#1f2937", zeroline=False, title_text="Time (s)")
    fig.update_yaxes(showgrid=True, gridcolor="#1f2937", zeroline=False, title_text="Amplitude (mV)")
    return fig

def filter_pipeline(signal):

    # remove baseline wander
    signal = butterworth_high(signal)

    # remove high-frequency noise
    signal = butterworth_low(signal, 150)

    # remove powerline inference at 50 Hz (for PTB-XL)
    signal = notch(signal, 50)
    # remove powerline inference at 60 Hz (for Code-15)
    #signal = notch(signal, 60)
    
    return signal

if __name__ == '__main__':

    ids = [655]
    
    signal = get_ecg_signals(patient_ids=ids, dataset="ptb-xl")
    signal = signal["signal"].tolist()
    signal = np.squeeze(signal, axis=0)

    for idx, lead in enumerate(signal):

        filtered_lead = filter_pipeline(lead)
    
        name_list = ["Original Lead", "Filtered Lead"]
        signal_list = [lead, filtered_lead]

        # compare original and filtered signal to each other by overlaying them
        fig = render_figures_overlay(500, signal_list, name_list, cols=2)
        fig.show()