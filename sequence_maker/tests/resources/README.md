# Test Resources

This directory contains resources used for testing the Sequence Maker application.

## Audio Files

For tests that require audio files, you should place test audio files in this directory. The tests are designed to work with the following files:

- `test_audio.mp3`: A short MP3 file (1-2 seconds) for basic audio loading tests
- `test_audio_long.mp3`: A longer MP3 file (10-20 seconds) for timeline and playback tests

## Project Files

For tests that require project files, you should place test project files in this directory. The tests are designed to work with the following files:

- `test_project.smproj`: A basic project file with a single timeline and no audio
- `test_project_with_audio.smproj`: A project file with a single timeline and audio

## Creating Test Resources

When running the tests for the first time, you may need to create these resources manually. You can use the Sequence Maker application to create test projects and export them to this directory.

For audio files, you can use any short audio clips. The specific content of the audio is not important for most tests, as they mock the actual audio playback.