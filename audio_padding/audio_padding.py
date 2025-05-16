import os
import sys
import time
import logging
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

# 配置日志
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"audio_padding_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_audio_duration(file_path):
    """获取音频文件时长（秒）"""
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(file_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())
    except Exception as e:
        logger.error(f"获取音频时长失败 {file_path}: {str(e)}")
        return None

def process_audio_file(input_file, target_duration=3.1):
    """处理单个音频文件"""
    try:
        # 获取当前音频时长
        current_duration = get_audio_duration(input_file)
        if current_duration is None:
            return False
        
        # 如果音频时长已经大于等于目标时长，跳过处理
        if current_duration >= target_duration:
            logger.info(f"文件 {input_file} 时长 {current_duration:.2f}秒，无需处理")
            return True
        
        # 计算需要添加的静音时长
        silence_duration = target_duration - current_duration
        
        # 创建临时文件
        temp_file = str(input_file) + '.temp'
        
        # 使用ffmpeg添加静音
        cmd = [
            'ffmpeg',
            '-y',  # 覆盖输出文件
            '-i', str(input_file),  # 输入文件
            '-af', f'apad=pad_dur={silence_duration}',  # 添加静音
            '-c:a', 'copy',  # 保持原始编码
            temp_file
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        # 重试机制：如果文件被占用，使用指数退避策略重试
        max_retries = 10  # 最大重试次数
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # 尝试覆盖原文件
                shutil.move(temp_file, input_file)
                logger.info(f"成功处理文件 {input_file}，时长从 {current_duration:.2f}秒 增加到 {target_duration:.2f}秒")
                return True
            except (PermissionError, OSError, IOError) as e:
                retry_count += 1
                # 使用指数退避策略，最大等待5秒
                retry_delay = min(2 ** retry_count, 5)
                logger.warning(f"尝试覆盖文件 {input_file} 失败 (尝试 {retry_count}/{max_retries}): {str(e)}")
                logger.info(f"等待 {retry_delay} 秒后重试...")
                
                if retry_count >= max_retries:
                    logger.error(f"无法覆盖文件 {input_file}，已达到最大重试次数")
                    return False
                    
                time.sleep(retry_delay)
                continue
            except Exception as e:
                logger.error(f"处理文件 {input_file} 时发生未知错误: {str(e)}")
                return False
                
    except Exception as e:
        logger.error(f"处理文件 {input_file} 时发生错误: {str(e)}")
        return False

def process_directory(directory_path):
    """处理目录中的所有音频文件"""
    directory = Path(directory_path)
    if not directory.exists():
        logger.error(f"目录不存在: {directory_path}")
        return
    
    # 支持的音频格式
    audio_extensions = {'.wav', '.mp3', '.flac', '.m4a', '.ogg'}
    
    # 获取所有音频文件
    audio_files = [f for f in directory.glob('**/*') if f.suffix.lower() in audio_extensions]
    total_files = len(audio_files)
    
    if total_files == 0:
        logger.info(f"在目录 {directory_path} 中未找到音频文件")
        return
    
    logger.info(f"找到 {total_files} 个音频文件")
    
    # 处理每个文件
    success_count = 0
    for i, file in enumerate(audio_files, 1):
        logger.info(f"正在处理 [{i}/{total_files}]: {file}")
        if process_audio_file(file):
            success_count += 1
    
    # 输出处理结果
    logger.info(f"处理完成！成功: {success_count}/{total_files}")

def get_input_directory():
    """获取用户输入的音频文件夹路径"""
    while True:
        print("\n请输入音频文件夹路径（支持拖拽文件夹到此处）：")
        directory_path = input().strip()
        
        # 处理拖拽路径（去除引号）
        directory_path = directory_path.strip('"').strip("'")
        
        # 转换为Path对象
        directory = Path(directory_path)
        
        if not directory.exists():
            print(f"错误：目录 '{directory_path}' 不存在，请重新输入")
            continue
            
        if not directory.is_dir():
            print(f"错误：'{directory_path}' 不是一个文件夹，请重新输入")
            continue
            
        return directory_path

def main():
    print("=" * 50)
    print("音频文件静音填充工具")
    print("=" * 50)
    print("说明：")
    print("1. 此工具会自动处理指定文件夹中的所有音频文件")
    print("2. 支持的音频格式：.wav, .mp3, .flac, .m4a, .ogg")
    print("3. 会将小于3.1秒的音频文件填充到3.1秒")
    print("4. 处理日志将保存在 logs 文件夹中")
    print("=" * 50)
    
    # 获取音频文件夹路径
    directory_path = get_input_directory()
    
    # 处理音频文件
    process_directory(directory_path)
    
    print("\n处理完成！详细日志请查看 logs 文件夹")
    input("\n按回车键退出...")

if __name__ == "__main__":
    main() 