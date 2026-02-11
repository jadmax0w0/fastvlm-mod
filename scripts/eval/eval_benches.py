import os
import argparse

special_bench_names = {
    "g": "gqa",
    "docvqa": "docvqa_val",
    "doc": "docvqa_val",
    "m3u": "mmmu",
    "v2": "vqav2",
    "vq2": "vqav2",
}

model_names = {
    "3": "ckpt/llava_fastvithd_0.5b_stage3/checkpoint-79226",
    "3o": "/data2/lyx/ckpts/fastvlm/llava_fastvithd_0.5b_stage3",
    "2": "/data2/lyx/ckpts/fastvlm/llava_fastvithd_0.5b_stage2",
}

run_name_prefix = "fvlm_qwen2_stg"  # + model_name

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bench_name", type=str)
    parser.add_argument("model", type=str, default="3")
    parser.add_argument("-g", "--gpu", "--cuda", type=str, default="0,1,2,3,4,5,6,7")
    parser.add_argument("-p", "--port", type=int, default=30010)
    parser.add_argument("--run_name", type=str, default=None, help="Default to be '{run_name_prefix}{model}'; `run_name_prefix` can be set in the code")
    parser.add_argument("--result_dir", type=str, default=None, help="Default to be 'ckpt/result_{bench_name}'")
    args = parser.parse_args()

    bench_name = None
    if args.bench_name not in special_bench_names:
        bench_name = args.bench_name
    else:
        bench_name = special_bench_names[args.bench_name]
    
    model_name = None
    if args.model not in model_names:
        assert os.path.exists(args.model), f"Path '{args.model}' does not exist"
        model_name = args.model
    else:
        model_name = model_names[args.model]
    
    model_dispname = args.run_name
    if model_dispname is None:
        model_dispname = args.model
        if os.path.exists(model_dispname):
            model_dispname = os.path.split(model_dispname)[-1]

    run_name = f"{run_name_prefix}{model_dispname}"

    result_dir = args.result_dir
    if result_dir is None:
        result_dir = f"ckpt/result_{bench_name}"

    num_procs = len(args.gpu.split(","))

    proc_port = int(args.port)

    print("Running arguments:")
    print({
        "Bench name": bench_name,
        "Model name": f"{model_name} (displayed as '{model_dispname}')",
        "Run name": run_name,
        "Result dir": result_dir,
        "CUDAs": f"{args.gpu} ({num_procs} devices)",
        "Process port": proc_port,
    })
    print()

    cmd_args = [
        "python -m accelerate.commands.launch",
        f"--num_processes {num_procs}",
        f"--main_process_port {proc_port}",
        "-m lmms_eval",
        "--model llava",
        f"--model_args pretrained={model_name},conv_template=qwen_2",
        f"--tasks {bench_name}",
        "--batch_size 1",
        "--gen_kwargs until=\"<|im_end|>\"",
        "--log_samples",
        f"--log_samples_suffix {run_name}",
        f"--output_path {result_dir}/log",
    ]
    cmd = f"CUDA_VISIBLE_DEVICES={args.gpu} " + " ".join(cmd_args)
    print(f"Command line:\n{cmd}")
    print()

    n = input("Is this cli input right? [y]/n ")
    if n == 'n' or n == 'N':
        return

    os.system(cmd)

if __name__ == "__main__":
    main()