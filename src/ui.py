"""Gradio chat interface — clean layout with a sidebar of frequently asked questions."""
from __future__ import annotations

import gradio as gr

EXAMPLES = [
    "I need a florist in New York for under $500",
    "Compare the top-rated photographers",
    "Which vendors offer vegan catering?",
    "Who can handle weddings with 300+ guests?",
    "What are the cheapest DJ options under $1000?",
]

CUSTOM_CSS = """
.gradio-container {
    max-width: 1120px !important;
    margin: 0 auto !important;
    padding: 2.5rem 1.5rem 3rem !important;
}

/* ── Header ─────────────────────────────────────────────── */
#header {
    display: flex;
    align-items: center;
    gap: 0.9rem;
    margin-bottom: 1.75rem;
}
#header .logo {
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    box-shadow: 0 6px 14px -4px rgba(99, 102, 241, 0.4);
}
#header h1 {
    font-size: 1.15rem;
    font-weight: 600;
    margin: 0;
    letter-spacing: -0.01em;
    color: var(--body-text-color);
}
#header .subtitle {
    font-size: 0.83rem;
    color: var(--body-text-color-subdued);
    margin: 0.15rem 0 0;
}

/* ── Sidebar (Frequently Asked) ─────────────────────────── */
#faq-header {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--body-text-color-subdued);
    margin: 0.4rem 0 0.85rem;
}
#faq-buttons button {
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 0.75rem 0.9rem !important;
    font-size: 0.85rem !important;
    line-height: 1.4 !important;
    font-weight: 400 !important;
    background: var(--background-fill-secondary) !important;
    border: 1px solid var(--border-color-primary) !important;
    border-radius: 10px !important;
    color: var(--body-text-color) !important;
    transition: all 0.15s ease !important;
    box-shadow: none !important;
    margin-bottom: 0.55rem;
    white-space: normal !important;
    height: auto !important;
    min-height: unset !important;
}
#faq-buttons button:hover {
    border-color: #6366f1 !important;
    background: var(--background-fill-primary) !important;
    transform: translateY(-1px);
    box-shadow: 0 2px 8px -2px rgba(99, 102, 241, 0.15) !important;
}

/* ── Chat polish ────────────────────────────────────────── */
.message-wrap { box-shadow: none !important; }
footer { display: none !important; }
"""

HEADER_HTML = """
<div id="header">
    <div class="logo">🎯</div>
    <div>
        <h1>Event Planning Assistant</h1>
        <p class="subtitle">Find vendors by budget, location, capacity, or any soft criteria.</p>
    </div>
</div>
"""


def launch_demo(chat_fn, **launch_kwargs) -> None:
    theme = gr.themes.Soft(
        primary_hue="indigo",
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
        radius_size=gr.themes.sizes.radius_md,
    )

    def respond(message: str, history: list[dict]) -> tuple[str, list[dict]]:
        if not message or not message.strip():
            return "", history or []
        answer = chat_fn(message, history or [])
        new_history = (history or []) + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": answer},
        ]
        return "", new_history

    with gr.Blocks(title="Event Planning Assistant") as demo:
        gr.HTML(HEADER_HTML)

        with gr.Row(equal_height=False):
            # ── Chat column ────────────────────────────────
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    height=540,
                    show_label=False,
                    avatar_images=(None, None),
                )
                with gr.Row():
                    textbox = gr.Textbox(
                        placeholder="Ask about catering, DJs, photographers, florists…",
                        show_label=False,
                        scale=8,
                        container=False,
                    )
                    submit_btn = gr.Button("Send", variant="primary", scale=1, min_width=90)

            # ── Sidebar: Frequently asked ──────────────────
            with gr.Column(scale=1, min_width=260):
                gr.HTML("<div id='faq-header'>💡 Frequently asked</div>")
                with gr.Column(elem_id="faq-buttons"):
                    for example in EXAMPLES:
                        btn = gr.Button(example)
                        btn.click(
                            lambda x=example: x,
                            outputs=textbox,
                        ).then(
                            respond,
                            [textbox, chatbot],
                            [textbox, chatbot],
                        )

        submit_btn.click(respond, [textbox, chatbot], [textbox, chatbot])
        textbox.submit(respond, [textbox, chatbot], [textbox, chatbot])

    demo.launch(theme=theme, css=CUSTOM_CSS, inbrowser=True, **launch_kwargs)