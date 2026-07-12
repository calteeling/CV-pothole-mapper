import os
from detection.video_processor import VideoProcessor

video_path = "data/clip_00_data_processing_automation.mp4"

if not os.path.exists(video_path):
    print("No video file found — skipping video processor test in CI")
    exit(0)

processor = VideoProcessor(frame_skip=5)
fps = processor.get_video_fps(video_path)
count = processor.get_frame_count(video_path)
print(f"FPS: {fps}")
print(f"Total frames: {count}")

frames = list(processor.extract_frames(video_path))
print(f"Extracted {len(frames)} frames")
print(f"Frame shape: {frames[0].shape}")