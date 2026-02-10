export CUDA_VISIBLE_DEVICES=2,3,4,5,6,7

NUM_PROCESSES=6
MAIN_PROCESS_PORT=30100

TASK_NAME=gqa
RUN_NAME=fvlm_qwen2_stg3
CKPT_PATH=ckpt/llava_fastvithd_0.5b_stage3/checkpoint-79226
# CKPT_PATH=/data2/lyx/ckpts/fastvlm/llava_fastvithd_0.5b_stage2
RESULT_DIR=eval/result_gqa

export FVLM_CKTIME=0  # 控制模型检查 prepare input 和 llm forward 耗时
# export LMMSEVAL_LLAVA_SHOW_TEXTOUTPUT="${RESULT_DIR}/lmm_textout"  # 1: 控制 lmms-eval 在每个数据点评测完之后在控制台输出 doc id 和模型回答内容; 某具体目录：将前述内容放到对应目录的日志文件中

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