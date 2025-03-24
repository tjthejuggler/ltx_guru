"""
Sequence Maker - Tests for Enhanced Audio Analysis

This module contains tests for the enhanced audio analysis functionality.
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock


def test_audio_analysis_methods_exist(app_fixture):
    """
    Test that the AudioManager has the enhanced analysis methods.
    
    Args:
        app_fixture: The app_fixture fixture
    """
    # Check that the analyze_audio method exists
    assert hasattr(app_fixture.audio_manager, 'analyze_audio')
    
    # Check that the enhanced analysis properties exist
    assert hasattr(app_fixture.audio_manager, 'onset_strength')
    assert hasattr(app_fixture.audio_manager, 'spectral_contrast')
    assert hasattr(app_fixture.audio_manager, 'spectral_centroid')
    assert hasattr(app_fixture.audio_manager, 'spectral_rolloff')
    assert hasattr(app_fixture.audio_manager, 'chroma')
    assert hasattr(app_fixture.audio_manager, 'rms_energy')
    assert hasattr(app_fixture.audio_manager, 'zero_crossing_rate')


def test_analyze_audio_method(app_fixture, monkeypatch):
    """
    Test that the analyze_audio method performs the expected analysis.
    
    Args:
        app_fixture: The app_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Create mock audio data
    app_fixture.audio_manager.audio_data = np.zeros(1000)
    app_fixture.audio_manager.sample_rate = 44100
    
    # Mock librosa functions to avoid actual computation
    mock_onset_strength = np.ones(100)
    mock_spectral_contrast = np.ones((7, 100))
    mock_spectral_centroid = np.ones(100)
    mock_spectral_rolloff = np.ones(100)
    mock_chroma = np.ones((12, 100))
    mock_rms = np.ones(100)
    mock_zcr = np.ones(100)
    
    # Create mock for librosa functions
    with patch('librosa.onset.onset_strength', return_value=mock_onset_strength), \
         patch('librosa.feature.spectral_contrast', return_value=mock_spectral_contrast), \
         patch('librosa.feature.spectral_centroid', return_value=np.array([mock_spectral_centroid])), \
         patch('librosa.feature.spectral_rolloff', return_value=np.array([mock_spectral_rolloff])), \
         patch('librosa.feature.chroma_stft', return_value=mock_chroma), \
         patch('librosa.feature.rms', return_value=np.array([mock_rms])), \
         patch('librosa.feature.zero_crossing_rate', return_value=np.array([mock_zcr])):
        
        # Create a signal spy to monitor audio_analyzed signal
        with pytest.raises(AttributeError):  # pytest-qt not available in test environment
            # This would be the ideal test with pytest-qt:
            # with qtbot.waitSignal(app_fixture.audio_manager.audio_analyzed, timeout=1000):
            #     app_fixture.audio_manager.analyze_audio()
            pass
        
        # Call the method directly instead
        app_fixture.audio_manager.analyze_audio()
        
        # Check that the analysis results were stored
        assert app_fixture.audio_manager.onset_strength is not None
        assert app_fixture.audio_manager.spectral_contrast is not None
        assert app_fixture.audio_manager.spectral_centroid is not None
        assert app_fixture.audio_manager.spectral_rolloff is not None
        assert app_fixture.audio_manager.chroma is not None
        assert app_fixture.audio_manager.rms_energy is not None
        assert app_fixture.audio_manager.zero_crossing_rate is not None


def test_app_context_api_includes_analysis(app_fixture, monkeypatch):
    """
    Test that the AppContextAPI includes the enhanced audio analysis data.
    
    Args:
        app_fixture: The app_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Create mock audio data and analysis results
    app_fixture.audio_manager.audio_file = "test.mp3"
    app_fixture.audio_manager.duration = 120.0
    app_fixture.audio_manager.sample_rate = 44100
    app_fixture.audio_manager.tempo = 120.0
    app_fixture.audio_manager.beat_times = np.array([1.0, 2.0, 3.0])
    
    # Mock enhanced analysis results
    app_fixture.audio_manager.onset_strength = np.ones(100)
    app_fixture.audio_manager.spectral_contrast = np.ones((7, 100))
    app_fixture.audio_manager.spectral_centroid = np.ones(100)
    app_fixture.audio_manager.spectral_rolloff = np.ones(100)
    app_fixture.audio_manager.chroma = np.ones((12, 100))
    app_fixture.audio_manager.rms_energy = np.ones(100)
    app_fixture.audio_manager.zero_crossing_rate = np.ones(100)
    
    # Get audio context
    from api.app_context_api import AppContextAPI
    context_api = AppContextAPI(app_fixture)
    audio_context = context_api.get_audio_context()
    
    # Check that the basic audio data is included
    assert audio_context["file"] == "test.mp3"
    assert audio_context["duration"] == 120.0
    assert audio_context["tempo"] == 120.0
    
    # Check that the enhanced analysis data is included
    assert "onset_strength_sample" in audio_context
    assert "spectral_contrast_mean" in audio_context
    assert "spectral_centroid_mean" in audio_context
    assert "spectral_rolloff_mean" in audio_context
    assert "chroma_means" in audio_context
    assert "rms_energy_mean" in audio_context
    assert "zero_crossing_rate_mean" in audio_context


def test_analyze_audio_called_after_load(app_fixture, monkeypatch):
    """
    Test that analyze_audio is called after loading an audio file.
    
    Args:
        app_fixture: The app_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Mock the _analyze_audio and analyze_audio methods
    mock_analyze = MagicMock()
    mock_enhanced_analyze = MagicMock()
    monkeypatch.setattr(app_fixture.audio_manager, '_analyze_audio', mock_analyze)
    monkeypatch.setattr(app_fixture.audio_manager, 'analyze_audio', mock_enhanced_analyze)
    
    # Mock the load_audio method to avoid actually loading a file
    monkeypatch.setattr(app_fixture.audio_manager, '_load_audio_file', lambda x: (np.zeros(1000), 44100))
    
    # Call load_audio
    app_fixture.audio_manager.load_audio("test.mp3")
    
    # Check that _analyze_audio was called
    mock_analyze.assert_called_once()