import gradio as gr

def get_app():
    with gr.Blocks() as app:
        state = gr.BrowserState(default_value="apple")
        dd = gr.Dropdown(["apple", "banana"], label="Fruit")
        
        app.load(lambda x: x, state, dd)
        dd.change(lambda x: x, dd, state)
    return app

if __name__ == '__main__':
    get_app().launch(server_port=40002)
