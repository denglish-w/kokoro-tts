import os
import random
import tempfile
import zipfile
import soundfile as sf
import gradio as gr
import logging
import numpy as np

from core.engine import generate_first, tokenize_first, generate_all, CUDA_AVAILABLE, pipelines
from core.text import split_text_into_chapters

logger = logging.getLogger(__name__)

# Load default voices
CHOICES = {
    '🇺🇸 🚺 Heart ❤️': 'af_heart',
    '🇺🇸 🚺 Bella 🔥': 'af_bella',
    '🇺🇸 🚺 Nicole 🎧': 'af_nicole',
    '🇺🇸 🚺 Aoede': 'af_aoede',
    '🇺🇸 🚺 Kore': 'af_kore',
    '🇺🇸 🚺 Sarah': 'af_sarah',
    '🇺🇸 🚺 Nova': 'af_nova',
    '🇺🇸 🚺 Sky': 'af_sky',
    '🇺🇸 🚺 Alloy': 'af_alloy',
    '🇺🇸 🚺 Jessica': 'af_jessica',
    '🇺🇸 🚺 River': 'af_river',
    '🇺🇸 🚹 Michael': 'am_michael',
    '🇺🇸 🚹 Fenrir': 'am_fenrir',
    '🇺🇸 🚹 Puck': 'am_puck',
    '🇺🇸 🚹 Echo': 'am_echo',
    '🇺🇸 🚹 Eric': 'am_eric',
    '🇺🇸 🚹 Liam': 'am_liam',
    '🇺🇸 🚹 Onyx': 'am_onyx',
    '🇺🇸 🚹 Santa': 'am_santa',
    '🇺🇸 🚹 Adam': 'am_adam',
    '🇬🇧 🚺 Emma': 'bf_emma',
    '🇬🇧 🚺 Isabella': 'bf_isabella',
    '🇬🇧 🚺 Alice': 'bf_alice',
    '🇬🇧 🚺 Lily': 'bf_lily',
    '🇬🇧 🚹 George': 'bm_george',
    '🇬🇧 🚹 Fable': 'bm_fable',
    '🇬🇧 🚹 Lewis': 'bm_lewis',
    '🇬🇧 🚹 Daniel': 'bm_daniel',
}

# Pre-load voices
for v in CHOICES.values():
    pipelines[v[0]].load_voice(v)

# Read demo texts
if os.path.exists('en.txt'):
    with open('en.txt', 'r') as r:
        random_quotes = [line.strip() for line in r]
else:
    random_quotes = ["The best way to predict the future is to invent it."]

def get_random_quote():
    return random.choice(random_quotes)

def get_gatsby():
    if os.path.exists('gatsby5k.md'):
        with open('gatsby5k.md', 'r') as r:
            return r.read().strip()
    return "The Great Gatsby content not found."

def get_frankenstein():
    if os.path.exists('frankenstein5k.md'):
        with open('frankenstein5k.md', 'r') as r:
            return r.read().strip()
    return "Frankenstein content not found."

def parse_custom_dict(text):
    if not text or not text.strip():
        return None
    d = {}
    for line in text.split('\n'):
        if ':' in line:
            k, v = line.split(':', 1)
            d[k.strip()] = v.strip()
    return d

def export_chapters_ui(file_obj, voice, speed, chapter_regex, combine_audio, save_dir, sec_voice, dict_text, skip_references, skip_chapters_regex, progress=gr.Progress()):
    if not file_obj:
        raise gr.Error("Please upload a text file.")
    
    import time
    logger.info(f"Exporting chapters for file: {file_obj.name}")
    with open(file_obj.name, 'r', encoding='utf-8') as f:
        text = f.read()
        
    custom_dict = parse_custom_dict(dict_text)
    chapters = split_text_into_chapters(text, chapter_regex, custom_dict, skip_references=skip_references, skip_chapters_regex=skip_chapters_regex)
                
    output_dir = save_dir if save_dir and os.path.isdir(save_dir) else tempfile.mkdtemp()
    zip_path = os.path.join(tempfile.mkdtemp(), "audiobook.zip")
    
    total_chars = sum(len(c[1]) for c in chapters)
    if total_chars == 0:
        total_chars = 1 # avoid div by zero
        
    processed_chars = [0] # mutable reference
    start_time = time.time()
    
    def update_progress(chunk_chars):
        processed_chars[0] += chunk_chars
        pct = min(processed_chars[0] / total_chars, 1.0)
        elapsed = time.time() - start_time
        if pct > 0:
            total_est = elapsed / pct
            remaining = max(total_est - elapsed, 0)
            mins, secs = divmod(int(remaining), 60)
            hrs, mins = divmod(mins, 60)
            if hrs > 0:
                eta_str = f"{hrs}h {mins}m {secs}s"
            else:
                eta_str = f"{mins}m {secs}s"
        else:
            eta_str = "Calculating..."
            
        progress(pct, desc=f"Rendering... ETA: {eta_str}")

    all_audio_chunks = []
    global_sample_rate = 24000
    
    should_zip = not (save_dir and os.path.isdir(save_dir))
    zipf = zipfile.ZipFile(zip_path, 'w') if should_zip else None

    try:
        for idx, (title, chapter_text) in enumerate(chapters):
            filename = f"{title}.wav"
            
            # Alternate voices
            current_voice = voice
            if sec_voice and sec_voice != 'None' and idx % 2 != 0:
                current_voice = sec_voice
            
            audio_data, _ = generate_first(
                chapter_text, 
                current_voice, 
                speed, 
                use_gpu=CUDA_AVAILABLE,
                progress_callback=update_progress,
                custom_dict=custom_dict,
                skip_references=skip_references
            )
            if audio_data:
                sample_rate, audio_np = audio_data
                global_sample_rate = sample_rate
                
                if combine_audio:
                    all_audio_chunks.append(audio_np)
                else:
                    wav_path = os.path.join(output_dir, filename)
                    sf.write(wav_path, audio_np, sample_rate)
                    if should_zip:
                        zipf.write(wav_path, arcname=filename)
        
        if combine_audio and all_audio_chunks:
            combined_audio = np.concatenate(all_audio_chunks, axis=0)
            wav_path = os.path.join(output_dir, "full_audiobook.wav")
            sf.write(wav_path, combined_audio, global_sample_rate)
            if should_zip:
                zipf.write(wav_path, arcname="full_audiobook.wav")
                
    finally:
        if zipf:
            zipf.close()
            
    if should_zip:
        logger.info(f"Finished exporting chapters to {zip_path}")
        return zip_path
    else:
        logger.info(f"Finished exporting chapters to {output_dir}")
        return None

TOKEN_NOTE = '''
💡 Customize pronunciation with Markdown link syntax and /slashes/ like `[Kokoro](/kˈOkəɹO/)`

💬 To adjust intonation, try punctuation `;:,.!?—…"()“”` or stress `ˈ` and `ˌ`

⬇️ Lower stress `[1 level](-1)` or `[2 levels](-2)`

⬆️ Raise stress 1 level `[or](+2)` 2 levels (only works on less stressed, usually short words)
'''

STREAM_NOTE = '⚠️ There is an unknown Gradio bug that might yield no audio the first time you click `Stream`.'

custom_css = """
/* Custom styling for a modern, sleek aesthetic */
.gradio-container {
    font-family: 'Inter', 'Roboto', sans-serif !important;
}

/* Button enhancements */
button.primary {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
    border: none !important;
    box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2), 0 2px 4px -1px rgba(79, 70, 229, 0.1) !important;
    transition: all 0.2s ease-in-out !important;
}
button.primary:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3), 0 4px 6px -2px rgba(79, 70, 229, 0.15) !important;
}

button.secondary {
    background-color: var(--background-fill-secondary) !important;
    border: 1px solid var(--border-color-primary) !important;
    transition: all 0.2s ease-in-out !important;
}
button.secondary:hover {
    background-color: var(--background-fill-secondary-hover) !important;
}

/* Tab aesthetics */
.tabs {
    border-radius: 0.5rem !important;
    overflow: hidden !important;
}

/* Title adjustments */
h1 {
    font-weight: 800 !important;
    background: -webkit-linear-gradient(45deg, #4f46e5, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    padding-bottom: 10px;
}
"""

theme = gr.themes.Soft(
    primary_hue="indigo",
    secondary_hue="blue",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"]
).set(
    button_primary_background_fill="*primary_500",
    button_primary_background_fill_hover="*primary_600",
)

def generate_first_ui(text, voice, speed, use_gpu, dict_text, skip_references):
    custom_dict = parse_custom_dict(dict_text)
    return generate_first(text, voice, speed, use_gpu, custom_dict=custom_dict, skip_references=skip_references)

def tokenize_first_ui(text, voice, dict_text, skip_references):
    custom_dict = parse_custom_dict(dict_text)
    return tokenize_first(text, voice, custom_dict=custom_dict, skip_references=skip_references)

def generate_all_ui(text, voice, speed, use_gpu, dict_text, skip_references):
    custom_dict = parse_custom_dict(dict_text)
    yield from generate_all(text, voice, speed, use_gpu, custom_dict=custom_dict, skip_references=skip_references)

def create_ui():
    dark_mode_js = """
    function() { 
        document.body.classList.add('dark'); 
    }
    """
    with gr.Blocks(title="Kokoro TTS", js=dark_mode_js) as app:
        gr.Markdown("# 🎙️ Kokoro Text-to-Speech")
        gr.Markdown("High-quality, fast TTS using the Kokoro-82M model. Enter text, select a voice, and generate!")
        
        with gr.Row():
            # Left Column - Inputs
            with gr.Column(scale=1, variant="panel"):
                gr.Markdown("### 📝 Input Settings")
                text = gr.Textbox(
                    label='Input Text', 
                    info="Type or paste your text here.",
                    lines=8,
                    placeholder="Enter text to synthesize..."
                )
                with gr.Row():
                    voice = gr.Dropdown(
                        list(CHOICES.items()), 
                        value='af_heart', 
                        label='Voice', 
                        info='Quality and availability vary by language'
                    )
                    use_gpu = gr.Dropdown(
                        [('ZeroGPU 🚀', True), ('CPU 🐌', False)],
                        value=CUDA_AVAILABLE,
                        label='Hardware',
                        info='GPU is usually faster',
                        interactive=CUDA_AVAILABLE
                    )
                speed = gr.Slider(minimum=0.5, maximum=2, value=1, step=0.1, label='Playback Speed')
                
                with gr.Accordion('⚙️ Advanced Settings', open=False):
                    skip_references = gr.Checkbox(
                        label="Auto-Skip Bibliographies & Abbreviations",
                        value=True,
                        info="Heuristically removes long reference lists before generation."
                    )
                    dict_text = gr.Textbox(
                        label='Custom Pronunciation Dictionary', 
                        info="Format: 'Key: Value' (one per line). e.g. 'NT: New Testament'",
                        lines=3,
                        placeholder="Jon: John\nNT: New Testament"
                    )
                
                with gr.Row():
                    random_btn = gr.Button('🎲 Random Quote', variant='secondary')
                    gatsby_btn = gr.Button('🥂 Gatsby', variant='secondary')
                    frankenstein_btn = gr.Button('💀 Frankenstein', variant='secondary')

            # Right Column - Outputs
            with gr.Column(scale=1):
                with gr.Tabs() as tabs:
                    # Generate Tab
                    with gr.Tab("▶️ Generate", id="generate_tab"):
                        out_audio = gr.Audio(label='Generated Audio', interactive=False, streaming=False, autoplay=True)
                        with gr.Row():
                            generate_btn = gr.Button('Synthesize Full Audio', variant='primary', size="lg")
                        with gr.Accordion('🔍 Output Tokens & Advanced Info', open=False):
                            out_ps = gr.Textbox(interactive=False, show_label=False, info='Tokens used to generate the audio (up to 510 context length).')
                            tokenize_btn = gr.Button('Tokenize Text Only', variant='secondary')
                            gr.Markdown(TOKEN_NOTE)

                    # Stream Tab
                    with gr.Tab("🌊 Stream", id="stream_tab"):
                        out_stream = gr.Audio(label='Streaming Audio Output', interactive=False, streaming=True, autoplay=True)
                        with gr.Row():
                            stream_btn = gr.Button('Start Streaming', variant='primary', size="lg")
                            stop_btn = gr.Button('🛑 Stop Stream', variant='secondary')
                        gr.Markdown(f"*{STREAM_NOTE}*")

                    # Batch Export Tab
                    with gr.Tab("📦 Batch Export", id="batch_tab"):
                        upload_file = gr.File(label='Upload Text File (.txt)', file_types=['.txt'])
                        chapter_regex = gr.Textbox(
                            label='Chapter Split Regex',
                            value=r'^(Part\s+[IVXLCDM]+|\d+)\s*$',
                            info='Regex to identify chapters (e.g. ^Chapter\\s+\\d+)'
                        )
                        skip_chapters_regex = gr.Textbox(
                            label='Skip Chapters Regex (Optional)',
                            value=r'(?i).*(bibliography|abbreviation).*',
                            info='Chapters whose title matches this regex will not be generated.'
                        )
                        with gr.Row():
                            combine_audio = gr.Checkbox(label="Combine into single audio file", value=False)
                            sec_voice_choices = [('None', 'None')] + list(CHOICES.items())
                            sec_voice = gr.Dropdown(sec_voice_choices, value='None', label='Secondary Voice (Alternating Chapters)')
                        save_dir = gr.Textbox(
                            label='Local Save Directory (Optional)',
                            info='If provided, saves files directly to this folder on your Mac instead of downloading a ZIP.',
                            placeholder='/Users/davidenglish/Desktop/Audiobooks'
                        )
                        export_btn = gr.Button('Generate & Export', variant='primary', size="lg")
                        download_file = gr.File(label='Download Audio (if no save dir)', interactive=False)

        # Event Listeners
        random_btn.click(fn=get_random_quote, inputs=[], outputs=[text])
        gatsby_btn.click(fn=get_gatsby, inputs=[], outputs=[text])
        frankenstein_btn.click(fn=get_frankenstein, inputs=[], outputs=[text])
        
        generate_btn.click(fn=generate_first_ui, inputs=[text, voice, speed, use_gpu, dict_text, skip_references], outputs=[out_audio, out_ps])
        tokenize_btn.click(fn=tokenize_first_ui, inputs=[text, voice, dict_text, skip_references], outputs=[out_ps])
        
        stream_event = stream_btn.click(fn=generate_all_ui, inputs=[text, voice, speed, use_gpu, dict_text, skip_references], outputs=[out_stream])
        stop_btn.click(fn=None, cancels=stream_event)
        
        export_btn.click(fn=export_chapters_ui, inputs=[upload_file, voice, speed, chapter_regex, combine_audio, save_dir, sec_voice, dict_text, skip_references, skip_chapters_regex], outputs=[download_file])

    return app
