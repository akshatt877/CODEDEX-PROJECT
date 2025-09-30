import pygame
import numpy as np
import os

def generate_ambient_audio():
    """Generate simple ambient audio files for background music"""
    
    # Initialize pygame mixer
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    
    # Create audio directory
    audio_dir = "audio"
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
    
    # Audio parameters
    sample_rate = 22050
    duration = 30  # 30 seconds per track
    
    def create_tone_sequence(frequencies, duration, sample_rate):
        """Create a sequence of tones"""
        samples = int(sample_rate * duration)
        waves = []
        
        for i, freq in enumerate(frequencies):
            t = np.linspace(0, duration / len(frequencies), samples // len(frequencies))
            # Create a gentle sine wave with fade in/out
            wave = np.sin(2 * np.pi * freq * t)
            
            # Add fade in/out to prevent clicks
            fade_samples = int(0.1 * len(wave))
            fade_in = np.linspace(0, 1, fade_samples)
            fade_out = np.linspace(1, 0, fade_samples)
            
            wave[:fade_samples] *= fade_in
            wave[-fade_samples:] *= fade_out
            
            # Reduce volume
            wave *= 0.3
            
            waves.append(wave)
        
        return np.concatenate(waves)
    
    # Define different ambient tracks with different frequency patterns
    tracks = {
        "Ambient Autumn": [220, 165, 196, 147],  # Warm, low frequencies
        "Gentle Rain Sounds": [130, 98, 123, 110],  # Very low, rain-like
        "Forest Whispers": [174, 196, 220, 165],  # Natural, organic feel
        "September Breeze": [196, 220, 247, 185],  # Light, airy
        "Cozy Afternoon": [147, 165, 130, 196],  # Comfortable, warm
        "Productivity Flow": [185, 207, 233, 175],  # Focused, steady
        "Focus Zone": [233, 196, 220, 185]  # Clear, concentrated
    }
    
    print("Generating ambient audio files...")
    
    for track_name, frequencies in tracks.items():
        print(f"Creating: {track_name}")
        
        # Generate the audio wave
        audio_data = create_tone_sequence(frequencies, duration, sample_rate)
        
        # Convert to 16-bit integers
        audio_data = (audio_data * 32767).astype(np.int16)
        
        # Create stereo by duplicating mono and ensure C-contiguous
        stereo_data = np.column_stack((audio_data, audio_data))
        stereo_data = np.ascontiguousarray(stereo_data)
        
        # Save as wav file
        filename = os.path.join(audio_dir, f"{track_name.replace(' ', '_').lower()}.wav")
        
        # Create pygame sound and save
        try:
            # Convert numpy array to pygame sound
            sound_array = pygame.sndarray.make_sound(stereo_data)
            
            # Save the sound (note: pygame doesn't have direct wav export, so we'll use a different approach)
            # Instead, let's create a simple wav file manually
            import wave
            
            with wave.open(filename, 'w') as wav_file:
                wav_file.setnchannels(2)  # Stereo
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(stereo_data.tobytes())
            
            print(f"✓ Created: {filename}")
            
        except Exception as e:
            print(f"✗ Error creating {track_name}: {e}")
    
    print("Audio generation complete!")
    return True

if __name__ == "__main__":
    try:
        generate_ambient_audio()
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Please install: pip install numpy")
    except Exception as e:
        print(f"Error generating audio: {e}")