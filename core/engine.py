import torch
import logging

try:
    import spaces
except ImportError:
    class spaces:
        @staticmethod
        def GPU(duration=None):
            return lambda x: x

from kokoro import KModel, KPipeline
import gradio as gr
from core.text import normalize_text

logger = logging.getLogger(__name__)

CUDA_AVAILABLE = torch.cuda.is_available()
MPS_AVAILABLE = hasattr(torch.backends, "mps") and torch.backends.mps.is_available()

if CUDA_AVAILABLE:
    DEVICE = 'cuda'
elif MPS_AVAILABLE:
    DEVICE = 'mps'
else:
    DEVICE = 'cpu'

logger.info(f"Hardware Device: {DEVICE}")

models = {}
def get_model(use_gpu):
    gpu_flag = use_gpu and DEVICE != 'cpu'
    if gpu_flag not in models:
        target_device = DEVICE if gpu_flag else 'cpu'
        logger.info(f"Loading KModel to {target_device}...")
        models[gpu_flag] = KModel().to(target_device).eval()
    return models[gpu_flag]

pipelines = {lang_code: KPipeline(lang_code=lang_code, model=False) for lang_code in 'ab'}
pipelines['a'].g2p.lexicon.golds['kokoro'] = 'kˈOkəɹO'
pipelines['b'].g2p.lexicon.golds['kokoro'] = 'kˈQkəɹQ'

@spaces.GPU(duration=30)
def forward_gpu(ps, ref_s, speed):
    return get_model(True)(ps, ref_s, speed)

def generate_first(text, voice='af_heart', speed=1, use_gpu=(DEVICE != 'cpu'), progress_callback=None, custom_dict=None, skip_references=True):
    text = normalize_text(text, custom_dict, skip_references=skip_references)
    if not text:
        return None, ''
    pipeline = pipelines[voice[0]]
    pack = pipeline.load_voice(voice)
    use_gpu = use_gpu and (DEVICE != 'cpu')
    all_audio = []
    all_ps = []
    
    logger.debug(f"Generating first audio segment for text: '{text[:50]}...' with voice {voice}")
    for graphemes, ps, _ in pipeline(text, voice, speed):
        ref_s = pack[len(ps)-1]
        if use_gpu:
            ref_s = ref_s.to(DEVICE)
            
        try:
            if use_gpu:
                audio = forward_gpu(ps, ref_s, speed)
            else:
                audio = get_model(False)(ps, ref_s, speed)
        except gr.exceptions.Error as e:
            logger.warning(f"Error during GPU generation: {e}. Falling back to CPU.")
            if use_gpu:
                gr.Warning(str(e))
                gr.Info('Retrying with CPU. To avoid this error, change Hardware to CPU.')
                audio = get_model(False)(ps, ref_s, speed)
            else:
                raise gr.Error(e)
        all_audio.append(audio)
        all_ps.append(ps)
        
        if progress_callback and graphemes:
            progress_callback(len(graphemes))
    
    if not all_audio:
        return None, ''
        
    full_audio = torch.cat(all_audio)
    return (24000, full_audio.numpy()), ' '.join(all_ps)

def tokenize_first(text, voice='af_heart', custom_dict=None, skip_references=True):
    text = normalize_text(text, custom_dict, skip_references=skip_references)
    pipeline = pipelines[voice[0]]
    all_ps = []
    for _, ps, _ in pipeline(text, voice):
        all_ps.append(ps)
    return ' '.join(all_ps)

def generate_all(text, voice='af_heart', speed=1, use_gpu=(DEVICE != 'cpu'), custom_dict=None, skip_references=True):
    text = normalize_text(text, custom_dict, skip_references=skip_references)
    pipeline = pipelines[voice[0]]
    pack = pipeline.load_voice(voice)
    use_gpu = use_gpu and (DEVICE != 'cpu')
    first = True
    
    logger.debug(f"Streaming generation for text: '{text[:50]}...' with voice {voice}")
    for _, ps, _ in pipeline(text, voice, speed):
        ref_s = pack[len(ps)-1]
        if use_gpu:
            ref_s = ref_s.to(DEVICE)
            
        try:
            if use_gpu:
                audio = forward_gpu(ps, ref_s, speed)
            else:
                audio = get_model(False)(ps, ref_s, speed)
        except gr.exceptions.Error as e:
            logger.warning(f"Error during GPU generation stream: {e}. Falling back to CPU.")
            if use_gpu:
                gr.Warning(str(e))
                gr.Info('Switching to CPU')
                audio = get_model(False)(ps, ref_s, speed)
            else:
                raise gr.Error(e)
        yield 24000, audio.numpy()
        if first:
            first = False
            yield 24000, torch.zeros(1).numpy()
