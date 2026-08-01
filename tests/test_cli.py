import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from cli import run_cli, build_parser


def _make_args(**overrides):
    args = build_parser().parse_args([])
    for k, v in overrides.items():
        setattr(args, k, v)
    return args


def _fake_generate_first(text, voice, speed, use_gpu=None, **kwargs):
    return (24000, np.zeros(240, dtype='float32')), 'ps'


class TestCliBatchSynthesis(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmpdir, ignore_errors=True)
        self.input_path = os.path.join(self.tmpdir, 'book.txt')
        with open(self.input_path, 'w', encoding='utf-8') as f:
            f.write("Chapter 1\nHello world.\n\nChapter 2\nGoodbye world.\n")
        self.output_dir = os.path.join(self.tmpdir, 'out')

    # @lat: [[cli#Secondary Voice Alternation]]
    def test_secondary_voice_alternates_by_chapter_parity(self):
        seen_voices = []

        def fake_generate_first(text, voice, speed, use_gpu=None, **kwargs):
            seen_voices.append(voice)
            return _fake_generate_first(text, voice, speed, use_gpu, **kwargs)

        args = _make_args(input=self.input_path, output_dir=self.output_dir,
                           secondary_voice='bf_emma')
        with patch('core.engine.generate_first', side_effect=fake_generate_first):
            run_cli(args)

        self.assertEqual(seen_voices, ['am_michael', 'bf_emma'])

    # @lat: [[cli#Batch Export and Resume]]
    def test_resume_skips_existing_chapter_output(self):
        call_count = {'n': 0}

        def fake_generate_first(text, voice, speed, use_gpu=None, **kwargs):
            call_count['n'] += 1
            return _fake_generate_first(text, voice, speed, use_gpu, **kwargs)

        args = _make_args(input=self.input_path, output_dir=self.output_dir)
        with patch('core.engine.generate_first', side_effect=fake_generate_first):
            run_cli(args)
        self.assertEqual(call_count['n'], 2)
        self.assertEqual(
            len([f for f in os.listdir(self.output_dir) if f.endswith('.wav')]), 2
        )

        # Second run: both chapter files already exist, so neither should regenerate.
        with patch('core.engine.generate_first', side_effect=fake_generate_first):
            run_cli(args)
        self.assertEqual(call_count['n'], 2)

    # @lat: [[cli#Batch Export and Resume]]
    def test_no_resume_regenerates_existing_chapter_output(self):
        call_count = {'n': 0}

        def fake_generate_first(text, voice, speed, use_gpu=None, **kwargs):
            call_count['n'] += 1
            return _fake_generate_first(text, voice, speed, use_gpu, **kwargs)

        args = _make_args(input=self.input_path, output_dir=self.output_dir, resume=False)
        with patch('core.engine.generate_first', side_effect=fake_generate_first):
            run_cli(args)
        self.assertEqual(call_count['n'], 2)

        with patch('core.engine.generate_first', side_effect=fake_generate_first):
            run_cli(args)
        self.assertEqual(call_count['n'], 4)


if __name__ == '__main__':
    unittest.main()
