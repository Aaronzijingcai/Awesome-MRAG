

import moviepy as mp
import argparse
import os

def convert_to_gif(input_path, output_path, start, end, resize, fps):
    """
    使用 MoviePy 将 MP4 的指定片段转换为 GIF。

    :param input_path: 输入的MP4文件路径
    :param output_path: 输出的GIF文件路径
    :param start: GIF开始时间（秒）
    :param end: GIF结束时间（秒）
    :param resize: 尺寸缩放因子（例如 0.5 表示缩小一半）
    :param fps: GIF的帧率
    """
    # 如果未指定输出路径，则根据输入文件名自动生成
    if not output_path:
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}.gif"

    try:
        print(f"⏳ 正在加载视频: {input_path}")
        # 加载视频文件
        clip = mp.VideoFileClip(input_path)

        # 截取视频片段
        if start is not None or end is not None:
            start_time = start if start is not None else 0
            end_time = end if end is not None else clip.duration
            print(f"✂️ 正在截取从 {start_time:.2f}s 到 {end_time:.2f}s 的片段...")
            clip = clip.subclip(start_time, end_time)
        
        # 调整视频尺寸
        if resize:
            original_width, original_height = clip.size
            print(f"📏 正在将尺寸从 {original_width}x{original_height} 缩放 {resize} 倍...")
            clip = clip.resize(resize)

        print(f"⚙️ 正在以 {fps} FPS 的帧率生成 GIF...")
        # 写入GIF文件
        clip.write_gif(output_path, fps=fps)

        print(f"✅ 成功! GIF 已保存至: {output_path}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")
    finally:
        # 确保关闭视频文件句柄
        if 'clip' in locals():
            clip.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="一个功能强大的MP4转GIF工具")
    
    parser.add_argument("input", type=str, help="输入的MP4文件路径")
    parser.add_argument("-o", "--output", type=str, help="输出的GIF文件路径 (可选, 默认为 '输入文件名.gif')")
    parser.add_argument("-s", "--start", type=float, help="截取视频的开始时间 (单位: 秒, 可选)")
    parser.add_argument("-e", "--end", type=float, help="截取视频的结束时间 (单位: 秒, 可选)")
    parser.add_argument("-r", "--resize", type=float, help="尺寸缩放比例, 如 0.5 代表缩小到50% (可选)")
    parser.add_argument("--fps", type=int, default=10, help="GIF的帧率 (Frames Per Second), 默认: 10")

    args = parser.parse_args()

    convert_to_gif(args.input, args.output, args.start, args.end, args.resize, args.fps)