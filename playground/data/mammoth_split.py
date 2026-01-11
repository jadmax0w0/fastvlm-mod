import ijson
import random
import os
import sys
import json
from typing import List
from tqdm import tqdm

def init_output_files(output_dir: str, n: int, prefix: str = "split_") -> List[os.PathLike]:
    """
    初始化输出文件，创建输出目录（如果不存在），并返回n个输出文件的路径
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    file_paths = []
    for i in range(n):
        file_path = os.path.join(output_dir, f"{prefix}{i+1}.json")
        # 清空文件（如果已存在）并写入JSON数组开头
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("[")
        file_paths.append(file_path)
    return file_paths

def close_output_files(file_paths: List[os.PathLike], counters: List[int]):
    """
    关闭输出文件，写入JSON数组结尾，并打印统计信息
    """
    for idx, file_path in enumerate(file_paths):
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write("]")
        print(f"输出文件 {file_path} 共写入 {counters[idx]} 条数据")

def split_large_json(input_file: str, output_dir: str, n: int, random_seed: int = 42):
    """
    核心函数：流式读取超大JSON文件，随机分成n份输出
    
    Args:
        input_file: 输入超大JSON文件路径
        output_dir: 输出文件目录
        n: 要分割的份数
        random_seed: 随机种子（保证结果可复现）
    """
    # 设置随机种子，保证可复现（可选，注释掉则每次结果不同）
    random.seed(random_seed)
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"输入文件不存在: {input_file}")
    
    # 初始化输出文件（写入JSON数组开头）
    output_files = init_output_files(output_dir, n)
    
    # 打开n个文件句柄（追加模式），并初始化计数器
    file_handles = [open(f, 'a', encoding='utf-8') for f in output_files]
    counters = [0] * n
    
    try:
        # 流式读取JSON数组中的每个元素（核心：ijson避免加载全部数据）
        with open(input_file, 'r', encoding='utf-8') as f:
            # 'item' 对应JSON数组的每个元素（如 [{}, {}, ...] 中的每个{}）
            items = ijson.items(f, 'item')
            
            for idx, item in tqdm(enumerate(items), desc="Loading samples", total=10140972):
                # 随机分配到0~n-1的分组
                group_idx = random.randint(0, n-1)
                counter = counters[group_idx]
                
                # 保证JSON格式合法：非第一条数据前加逗号
                if counter > 0:
                    file_handles[group_idx].write(",")
                
                # 将当前元素写入对应文件（转为JSON字符串）
                json.dump(item, file_handles[group_idx], ensure_ascii=False)
                
                # 更新计数器
                counters[group_idx] += 1
                
                # 每处理10万条打印进度（可选，监控进度）
                if (idx + 1) % 100000 == 0:
                    print(f"已处理 {idx + 1:,} 条数据 | 各分组当前条数: {counters}")
        
        print(f"\n全部处理完成！总处理条数: {sum(counters):,}")
    
    except Exception as e:
        raise RuntimeError(f"处理过程中出错: {str(e)}")
    
    finally:
        # 关闭所有文件句柄
        for fh in file_handles:
            fh.close()
        # 写入JSON数组结尾并打印统计
        close_output_files(output_files, counters)

if __name__ == "__main__":
    # 命令行参数说明：python script.py <输入JSON文件> <分割份数n> <输出目录>
    if len(sys.argv) != 4:
        print("用法: python split_large_json.py <input_json_file> <n> <output_directory>")
        print("示例: python split_large_json.py data.json 10 ./output")
        sys.exit(1)
    
    input_file = sys.argv[1]
    n = int(sys.argv[2])
    output_dir = sys.argv[3]
    
    # 校验n的合法性
    if n <= 0:
        print("分割份数n必须是正整数")
        sys.exit(1)
    
    try:
        split_large_json(input_file, output_dir, n)
    except Exception as e:
        print(f"执行失败: {str(e)}")
        sys.exit(1)