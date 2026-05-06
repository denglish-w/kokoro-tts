# Audio Export Workflows Skill

This skill guides the extension and debugging of the audio export pipeline.

## Export Pipeline
1. **Text Splitting**: Verify `split_text_into_chapters` regex accuracy.
2. **Synthesis**: Ensure `generate_all` is used for efficient batch processing.
3. **Combination**: `np.concatenate` chunks before writing to file.
4. **Post-processing**: Use `ffmpeg` for MP3 conversion (192k bitrate standard).

## Common Tasks
- **Adding Formats**: Modify `export_chapters_ui` in `ui/app.py` to support OGG, FLAC, etc.
- **Path Customization**: Update the default `output_dir` logic to handle different OS environments.
- **Resume Logic**: Check for existing files in the output directory before synthesizing a chapter.

## Debugging
- Check `ffmpeg` availability using `subprocess`.
- Verify write permissions for the `Kokoro_Exports` directory.
- Monitor memory usage during `np.concatenate` for very large books.
