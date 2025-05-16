import os
import sys

def generate_list(audio_dir):
    """
    生成list文件
    :param audio_dir: 音频文件目录
    """
    # 确保输出目录存在
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "output", "asr_opt")
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取音频目录的文件夹名作为说话人名称
    speaker_name = os.path.basename(audio_dir)
    
    # 准备输出内容
    output_lines = []
    
    # 遍历音频文件
    for filename in os.listdir(audio_dir):
        if filename.endswith(('.wav', '.mp3', '.flac')):  # 支持的音频格式
            # 获取完整路径
            file_path = os.path.join(audio_dir, filename)
            # 获取文件名(不含后缀)
            filename_no_ext = os.path.splitext(filename)[0]
            # 从后往前找到第一个下划线的位置
            last_underscore_index = filename_no_ext.rfind('_')
            if last_underscore_index != -1:
                # 提取最后一个下划线后的内容作为文本
                text = filename_no_ext[last_underscore_index + 1:]
            else:
                # 如果没有下划线，则使用整个文件名
                text = filename_no_ext
            # 组合成list格式，使用ja作为语言标记
            line = f"{file_path}|{speaker_name}|JA|{text}"
            output_lines.append(line)
    
    # 写入文件
    output_file = os.path.join(output_dir, f"{speaker_name}.list")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    
    print(f"已生成list文件: {output_file}")
    print(f"共处理 {len(output_lines)} 个音频文件")

if __name__ == "__main__":
    print("\n=== GPT-SoVITS 音频列表生成工具 ===")
    print("请输入音频文件所在文件夹的完整路径")
    print("例如: D:\\GPT-SoVITS\\raw\\xxx 或 /home/user/GPT-SoVITS/raw/xxx")
    print("提示: 可以直接从文件资源管理器复制路径并粘贴到这里")
    print("=" * 40)
    
    if len(sys.argv) == 2:
        audio_dir = sys.argv[1]
    else:
        audio_dir = input("\n请输入音频文件夹路径: ").strip()
    
    # 处理Windows路径中的引号
    audio_dir = audio_dir.strip('"').strip("'")
    
    if not os.path.exists(audio_dir):
        print(f"\n错误: 目录 {audio_dir} 不存在")
        sys.exit(1)
    
    generate_list(audio_dir) 