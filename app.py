try:
    import spaces
except ImportError:
    class spaces:
        @staticmethod
        def GPU(duration=None):
            return lambda x: x

from kokoro import KModel, KPipeline
import gradio as gr
import os
import random
import torch
import re
import tempfile
import zipfile
import argparse
import soundfile as sf
from tqdm import tqdm
from num2words import num2words

CUDA_AVAILABLE = torch.cuda.is_available()
models = {gpu: KModel().to('cuda' if gpu else 'cpu').eval() for gpu in [False] + ([True] if CUDA_AVAILABLE else [])}
pipelines = {lang_code: KPipeline(lang_code=lang_code, model=False) for lang_code in 'ab'}
pipelines['a'].g2p.lexicon.golds['kokoro'] = 'kˈOkəɹO'
pipelines['b'].g2p.lexicon.golds['kokoro'] = 'kˈQkəɹQ'

@spaces.GPU(duration=30)
def forward_gpu(ps, ref_s, speed):
    return models[True](ps, ref_s, speed)

def normalize_text(text):
    # Standardize line endings and whitespace
    text = text.replace('\r\n', '\n').strip()
    
    # Remove footnote markers like [1], [12], (1), ^1
    text = re.sub(r'\[\d+\]|\(\d+\)|\^\d+', '', text)
    
    # Remove page numbers (standalone numbers on their own line)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    
    # Normalize 4-digit years (1000-2099) to read as "sixteen forty-five"
    def year_to_words(match):
        year = int(match.group(0))
        return num2words(year, to='year')
    
    text = re.sub(r'\b(1[0-9]{3}|20[0-9]{2})\b', year_to_words, text)
    
    # Expand abbreviations (case-sensitive, whole-word only)
    expansions = {
        r'\bNT\b': 'New Testament',
        r'\bOT\b': 'Old Testament',
    }
    
    for pattern, replacement in expansions.items():
        text = re.sub(pattern, replacement, text)
        
    return text

def generate_first(text, voice='af_heart', speed=1, use_gpu=CUDA_AVAILABLE):
    text = normalize_text(text)
    if not text:
        return None, ''
    pipeline = pipelines[voice[0]]
    pack = pipeline.load_voice(voice)
    use_gpu = use_gpu and CUDA_AVAILABLE
    all_audio = []
    all_ps = []
    for _, ps, _ in pipeline(text, voice, speed):
        ref_s = pack[len(ps)-1]
        try:
            if use_gpu:
                audio = forward_gpu(ps, ref_s, speed)
            else:
                audio = models[False](ps, ref_s, speed)
        except gr.exceptions.Error as e:
            if use_gpu:
                gr.Warning(str(e))
                gr.Info('Retrying with CPU. To avoid this error, change Hardware to CPU.')
                audio = models[False](ps, ref_s, speed)
            else:
                raise gr.Error(e)
        all_audio.append(audio)
        all_ps.append(ps)
    
    if not all_audio:
        return None, ''
        
    full_audio = torch.cat(all_audio)
    return (24000, full_audio.numpy()), ' '.join(all_ps)

# Arena API
def predict(text, voice='af_heart', speed=1):
    res = generate_first(text, voice, speed, use_gpu=False)
    return res[0] if res else None

def tokenize_first(text, voice='af_heart'):
    text = normalize_text(text)
    pipeline = pipelines[voice[0]]
    all_ps = []
    for _, ps, _ in pipeline(text, voice):
        all_ps.append(ps)
    return ' '.join(all_ps)

def generate_all(text, voice='af_heart', speed=1, use_gpu=CUDA_AVAILABLE):
    text = normalize_text(text)
    pipeline = pipelines[voice[0]]
    pack = pipeline.load_voice(voice)
    use_gpu = use_gpu and CUDA_AVAILABLE
    first = True
    for _, ps, _ in pipeline(text, voice, speed):
        ref_s = pack[len(ps)-1]
        try:
            if use_gpu:
                audio = forward_gpu(ps, ref_s, speed)
            else:
                audio = models[False](ps, ref_s, speed)
        except gr.exceptions.Error as e:
            if use_gpu:
                gr.Warning(str(e))
                gr.Info('Switching to CPU')
                audio = models[False](ps, ref_s, speed)
            else:
                raise gr.Error(e)
        yield 24000, audio.numpy()
        if first:
            first = False
            yield 24000, torch.zeros(1).numpy()

def split_text_into_chapters(text, chapter_regex):
    text = normalize_text(text)
    chapters = []
    if not chapter_regex.strip():
        chapters.append(("Full_Audio", text))
    else:
        matches = list(re.finditer(chapter_regex, text, flags=re.MULTILINE | re.IGNORECASE))
        if not matches:
            chapters.append(("Full_Audio", text))
        else:
            if matches[0].start() > 0:
                intro = text[:matches[0].start()].strip()
                if intro:
                    chapters.append(("00_Intro", intro))
            
            for i in range(len(matches)):
                start = matches[i].start()
                end = matches[i+1].start() if i + 1 < len(matches) else len(text)
                chapter_text = text[start:end].strip()
                
                title = matches[i].group(0).strip()
                title = re.sub(r'[\\/*?:"<>|]', "", title)
                title = title.replace(" ", "_")
                chapters.append((f"{i+1:02d}_{title}", chapter_text))
    return chapters

def export_chapters_ui(file_obj, voice, speed, chapter_regex, progress=gr.Progress()):
    if not file_obj:
        raise gr.Error("Please upload a text file.")
    
    with open(file_obj.name, 'r', encoding='utf-8') as f:
        text = f.read()
    
    chapters = split_text_into_chapters(text, chapter_regex)
                
    output_dir = tempfile.mkdtemp()
    zip_path = os.path.join(tempfile.mkdtemp(), "audiobook.zip")
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for idx, (title, chapter_text) in progress.tqdm(enumerate(chapters), total=len(chapters), desc="Generating Chapters"):
            filename = f"{title}.wav"
            
            audio_data, _ = generate_first(chapter_text, voice, speed, use_gpu=CUDA_AVAILABLE)
            if audio_data:
                sample_rate, audio_np = audio_data
                wav_path = os.path.join(output_dir, filename)
                sf.write(wav_path, audio_np, sample_rate)
                zipf.write(wav_path, arcname=filename)
                
    return zip_path

def run_cli(args):
    print(f"Reading {args.input}...")
    with open(args.input, 'r', encoding='utf-8') as f:
        text = f.read()
    
    chapters = split_text_into_chapters(text, args.regex)
    print(f"Found {len(chapters)} chapters. Starting synthesis...")
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    for title, chapter_text in tqdm(chapters, desc="Generating Chapters"):
        audio_data, _ = generate_first(chapter_text, args.voice, args.speed, use_gpu=args.gpu)
        if audio_data:
            sample_rate, audio_np = audio_data
            filename = f"{title}.wav"
            output_path = os.path.join(args.output_dir, filename)
            sf.write(output_path, audio_np, sample_rate)
    
    print(f"Done! Audio files saved to {args.output_dir}")

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

for v in CHOICES.values():
    pipelines[v[0]].load_voice(v)

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

TOKEN_NOTE = '''
💡 Customize pronunciation with Markdown link syntax and /slashes/ like `[Kokoro](/kˈOkəɹO/)`

💬 To adjust intonation, try punctuation `;:,.!?—…"()“”` or stress `ˈ` and `ˌ`

⬇️ Lower stress `[1 level](-1)` or `[2 levels](-2)`

⬆️ Raise stress 1 level `[or](+2)` 2 levels (only works on less stressed, usually short words)
'''

with gr.Blocks() as generate_tab:
    out_audio = gr.Audio(label='Output Audio', interactive=False, streaming=False, autoplay=True)
    generate_btn = gr.Button('Generate', variant='primary')
    with gr.Accordion('Output Tokens', open=True):
        out_ps = gr.Textbox(interactive=False, show_label=False, info='Tokens used to generate the audio, up to 510 context length.')
        tokenize_btn = gr.Button('Tokenize', variant='secondary')
        gr.Markdown(TOKEN_NOTE)

STREAM_NOTE = ['⚠️ There is an unknown Gradio bug that might yield no audio the first time you click `Stream`.']
STREAM_NOTE = '\n\n'.join(STREAM_NOTE)

with gr.Blocks() as stream_tab:
    out_stream = gr.Audio(label='Output Audio Stream', interactive=False, streaming=True, autoplay=True)
    with gr.Row():
        stream_btn = gr.Button('Stream', variant='primary')
        stop_btn = gr.Button('Stop', variant='stop')
    with gr.Accordion('Note', open=True):
        gr.Markdown(STREAM_NOTE)
        gr.DuplicateButton()

with gr.Blocks() as batch_tab:
    with gr.Row():
        with gr.Column():
            upload_file = gr.File(label='Upload Text File (.txt)', file_types=['.txt'])
            chapter_regex = gr.Textbox(
                label='Chapter Split Regex',
                value=r'^(Part\s+[IVXLCDM]+|\d+)\s*$',
                info='Regex to identify chapters (e.g. ^Chapter\\s+\\d+ or ^(Part\\s+[IVXLCDM]+|\\d+)\\s*$)'
            )
            export_btn = gr.Button('Generate & Export ZIP', variant='primary')
        with gr.Column():
            download_file = gr.File(label='Download Audio ZIP', interactive=False)

API_OPEN = True
with gr.Blocks() as app:
    with gr.Row():
        with gr.Column():
            text = gr.Textbox(label='Input Text', info=f"Arbitrarily many characters supported")
            with gr.Row():
                voice = gr.Dropdown(list(CHOICES.items()), value='af_heart', label='Voice', info='Quality and availability vary by language')
                use_gpu = gr.Dropdown(
                    [('ZeroGPU 🚀', True), ('CPU 🐌', False)],
                    value=CUDA_AVAILABLE,
                    label='Hardware',
                    info='GPU is usually faster, but has a usage quota',
                    interactive=CUDA_AVAILABLE
                )
            speed = gr.Slider(minimum=0.5, maximum=2, value=1, step=0.1, label='Speed')
            random_btn = gr.Button('🎲 Random Quote 💬', variant='secondary')
            with gr.Row():
                gatsby_btn = gr.Button('🥂 Gatsby 📕', variant='secondary')
                frankenstein_btn = gr.Button('💀 Frankenstein 📗', variant='secondary')
        with gr.Column():
            gr.TabbedInterface([generate_tab, stream_tab, batch_tab], ['Generate', 'Stream', 'Batch Export'])
    
    random_btn.click(fn=get_random_quote, inputs=[], outputs=[text])
    gatsby_btn.click(fn=get_gatsby, inputs=[], outputs=[text])
    frankenstein_btn.click(fn=get_frankenstein, inputs=[], outputs=[text])
    generate_btn.click(fn=generate_first, inputs=[text, voice, speed, use_gpu], outputs=[out_audio, out_ps])
    tokenize_btn.click(fn=tokenize_first, inputs=[text, voice], outputs=[out_ps])
    stream_event = stream_btn.click(fn=generate_all, inputs=[text, voice, speed, use_gpu], outputs=[out_stream])
    stop_btn.click(fn=None, cancels=stream_event)
    export_btn.click(fn=export_chapters_ui, inputs=[upload_file, voice, speed, chapter_regex], outputs=[download_file])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Kokoro-TTS CLI')
    parser.add_argument('--input', type=str, help='Input text file for batch processing')
    parser.add_argument('--output-dir', type=str, default='output_audio', help='Directory to save audio chapters')
    parser.add_argument('--regex', type=str, default=r'^Chapter\s+\d+', help='Regex for splitting chapters')
    parser.add_argument('--voice', type=str, default='af_heart', help='Voice ID to use')
    parser.add_argument('--speed', type=float, default=1.0, help='Playback speed')
    parser.add_argument('--gpu', action='store_true', help='Force use of GPU')
    
    args, unknown = parser.parse_known_args()
    
    if args.input:
        run_cli(args)
    else:
        app.queue(api_open=API_OPEN).launch(server_name="0.0.0.0", server_port=40001)
