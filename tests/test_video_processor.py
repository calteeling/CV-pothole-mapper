from detection.video_processor import VideoProcessor

processor = VideoProcessor(frame_skip=5)

# Test basic info
fps = processor.get_video_fps("data/clip_00_data_processing_automation.mp4")
count = processor.get_frame_count("data/clip_00_data_processing_automation.mp4")
print(f"FPS: {fps}")
print(f"Total frames: {count}")

# Test frame extraction
frames = list(processor.extract_frames("data/clip_00_data_processing_automation.mp4"))
print(f"Extracted {len(frames)} frames")
print(f"Frame shape: {frames[0].shape}")