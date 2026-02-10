export CUDA_VISIBLE_DEVICES=2,3,4,5,6,7

NUM_PROCESSES=6
MAIN_PROCESS_PORT=30100

TASK_NAME=mmmu_val
RUN_NAME=fvlm_qwen2_stg2
# CKPT_PATH=ckpt/llava_fastvithd_0.5b_stage3/checkpoint-79226
CKPT_PATH=/data2/lyx/ckpts/fastvlm/llava_fastvithd_0.5b_stage2
RESULT_DIR=eval/result_mmmu

export FVLM_CKTIME=0  # 控制模型检查 prepare input 和 llm forward 耗时

python -m accelerate.commands.launch \
    --num_processes $NUM_PROCESSES \
    --main_process_port $MAIN_PROCESS_PORT \
    -m lmms_eval \
    --model llava \
    --model_args pretrained=${CKPT_PATH},conv_template=qwen_2 \
    --tasks $TASK_NAME \
    --batch_size 1 \
    --gen_kwargs until="<|im_end|>" \
    --log_samples \
    --log_samples_suffix $RUN_NAME \
    --output_path ${RESULT_DIR}/log

## LLaVA args in LLMs-Eval
# self,
# pretrained: str = "liuhaotian/llava-v1.5-7b",
# truncation: Optional[bool] = True,
# device: Optional[str] = "cuda:0",
# batch_size: Optional[Union[int, str]] = 1,
# model_name=None,
# attn_implementation=best_fit_attn_implementation,
# device_map="cuda:0",
# conv_template="vicuna_v1",
# use_cache=True,
# tie_weights: bool = True,
# truncate_context=False,  # whether to truncate the context in generation, set it False for LLaVA-1.6
# customized_config=None,  # ends in json
# **kwargs,