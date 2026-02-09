#!/bin/bash

# Args to note:
# --include: 在哪几个 GPU 上跑
# --version: 控制 conversation template 用谁的，在 conversation.py 里面可以看都有哪些可选项
# --vision_tower: 控制使用什么 vision encoder, 可以用 predict.py 读一下检查点，然后查看里面 model.config，对应项填到这里
# --mm*, --image_aspect_ratio: 都可以在 predict.py 里面查看 model.config 获取

    # --pretrain_mm_mlp_adapter ./checkpoints/llava-v1.5-13b-pretrain/mm_projector.bin \
    # --data_path playground/data/mammoth_si_10M.json \
    # --image_folder playground/data/mammoth_single_image \
    # --resume_checkpoint_dir ./ckpt/llava_fastvithd_0.5b_stage3_split1/checkpoint-3971 \
    # --data_path playground/data/mammoth_si_anno_split/split_2.json \

    # --data_path playground/data/mammoth_si_10M.jsonl \
    # --image_folder playground/data/mammoth_single_image \
# deepspeed --include localhost:0,1,2,3,4,5,6,7 \
deepspeed --include localhost:1 \
    llava/train/train_mem.py \
    --deepspeed ./scripts/zero3.json \
    --model_name_or_path /data2/lyx/ckpts/fastvlm/llava_fastvithd_0.5b_stage2 \
    --version qwen_2 \
    --data_path playground/data/llava_v1_5_mix665k.jsonl \
    --image_folder playground/data/llava1.5-665k-data \
    --use_datasets_loader True \
    --vision_tower mobileclip_l_1024 \
    --mm_projector_type mlp2x_gelu \
    --mm_vision_select_layer -2 \
    --mm_use_im_start_end False \
    --mm_use_im_patch_token False \
    --image_aspect_ratio pad \
    --group_by_modality_length True \
    --bf16 True \
    --output_dir ./ckpt/llava_fastvithd_0.5b_stage3_llava665k \
    --num_train_epochs 1 \
    --per_device_train_batch_size 4 \
    --per_device_eval_batch_size 4 \
    --gradient_accumulation_steps 4 \
    --evaluation_strategy "no" \
    --save_strategy "steps" \
    --save_steps 200 \
    --save_total_limit 1 \
    --learning_rate 2e-5 \
    --weight_decay 0. \
    --warmup_ratio 0.03 \
    --lr_scheduler_type "cosine" \
    --logging_steps 50 \
    --tf32 True \
    --model_max_length 2048 \
    --gradient_checkpointing True \
    --dataloader_num_workers 4 \
    --lazy_preprocess True #\
    # --report_to wandb