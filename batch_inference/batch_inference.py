import os
import sys
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime

# 配置日志
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"batch_inference_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 模型路径配置
GPT_MODEL_PATH = "GPT_weights/your_gpt_model.ckpt"  # 请替换为实际的GPT模型路径
SOVITS_MODEL_PATH = "SoVITS_weights/your_sovits_model.pth"  # 请替换为实际的SoVITS模型路径

# 版本后缀
VERSION_SUFFIXES = ['_a', '_b', '_c', '_d']

def get_text_file():
    """获取文本文件路径"""
    while True:
        print("\n请输入文本文件路径（支持拖拽文件到此处）：")
        file_path = input().strip()
        
        # 处理拖拽路径（去除引号）
        file_path = file_path.strip('"').strip("'")
        
        # 转换为Path对象
        text_file = Path(file_path)
        
        if not text_file.exists():
            print(f"错误：文件 '{file_path}' 不存在，请重新输入")
            continue
            
        if not text_file.is_file():
            print(f"错误：'{file_path}' 不是一个文件，请重新输入")
            continue
            
        return file_path

def get_reference_audio_dir():
    """获取参考音频目录"""
    while True:
        print("\n请输入参考音频目录路径（支持拖拽文件夹到此处）：")
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

def extract_text_from_filename(filename):
    """从文件名中提取文本（最后一个下划线后的内容）"""
    filename = Path(filename).stem  # 获取不含扩展名的文件名
    parts = filename.split('_')
    if len(parts) > 1:
        return parts[-1]
    return filename

def process_tts(text_file, reference_dir):
    """处理TTS合成"""
    try:
        # 读取文本文件
        with open(text_file, 'r', encoding='utf-8') as f:
            texts = [line.strip() for line in f.readlines() if line.strip()]
        
        # 获取参考音频文件
        reference_files = sorted([f for f in Path(reference_dir).glob('*.wav')])
        
        if len(texts) != len(reference_files):
            logger.error(f"文本数量({len(texts)})与参考音频数量({len(reference_files)})不匹配")
            return
        
        # 创建输出目录
        output_dir = Path(__file__).parent / "export"
        output_dir.mkdir(exist_ok=True)
        
        # 处理每个文本
        total_files = len(texts) * len(VERSION_SUFFIXES)
        current_file = 0
        
        for i, (text, ref_file) in enumerate(zip(texts, reference_files), 1):
            ref_text = extract_text_from_filename(ref_file)
            
            # 为每个文本生成4个版本
            for suffix in VERSION_SUFFIXES:
                current_file += 1
                output_file = output_dir / f"{ref_file.stem}{suffix}.wav"
                
                # 构建推理命令
                cmd = [
                    'python',
                    'GPT_SoVITS/inference.py',
                    '--text', text,
                    '--reference_audio', str(ref_file),
                    '--reference_text', ref_text,
                    '--language', 'ja',
                    '--gpt_model_path', GPT_MODEL_PATH,
                    '--sovits_model_path', SOVITS_MODEL_PATH,
                    '--output_path', str(output_file),
                    '--steps', '32',
                    '--speed', '1',
                    '--pause_time', '0.3',
                    '--top_k', '15',
                    '--top_p', '1',
                    '--temperature', '1'
                ]
                
                logger.info(f"正在处理 [{current_file}/{total_files}]: {text} (版本{suffix})")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info(f"成功处理: {text} (版本{suffix})")
                else:
                    logger.error(f"处理失败: {text} (版本{suffix})\n错误信息: {result.stderr}")
                
                # 添加短暂延迟，避免系统负载过高
                time.sleep(0.5)
            
    except Exception as e:
        logger.error(f"处理过程中发生错误: {str(e)}")

def main():
    print("=" * 50)
    print("GPT-SoVITS 批量TTS推理工具")
    print("=" * 50)
    print("说明：")
    print("1. 此工具将根据文本文件和参考音频进行批量TTS合成")
    print("2. 文本文件中的每一行将对应一个参考音频")
    print("3. 每个文本将生成4个不同版本的音频（_a, _b, _c, _d）")
    print("4. 处理日志将保存在 logs 文件夹中")
    print("5. 输出文件将保存在 export 文件夹中")
    print("=" * 50)
    
    # 获取输入参数
    text_file = get_text_file()
    reference_dir = get_reference_audio_dir()
    
    # 处理TTS合成
    process_tts(text_file, reference_dir)
    
    print("\n处理完成！详细日志请查看 logs 文件夹")
    input("\n按回车键退出...")

if __name__ == "__main__":
    main() 