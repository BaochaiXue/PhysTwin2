#!/bin/bash

# Render dynamic Gaussian splatting sequences and export videos

output_dir="./gaussian_output_dynamic"

# views=("0" "1" "2")
views=("0")  # indices of camera views to export

# scenes=("double_lift_cloth_1" "double_lift_cloth_3" "double_lift_sloth" "double_lift_zebra"
#         "double_stretch_sloth" "double_stretch_zebra"
#         "rope_double_hand"
#         "single_clift_cloth_1" "single_clift_cloth_3"
#         "single_lift_cloth" "single_lift_cloth_1" "single_lift_cloth_3" "single_lift_cloth_4"
#         "single_lift_dinosor" "single_lift_rope" "single_lift_sloth" "single_lift_zebra"
#         "single_push_rope" "single_push_rope_1" "single_push_rope_4"
#         "single_push_sloth"
#         "weird_package")

scenes=("double_stretch_sloth")  # scenes to simulate

exp_name='init=hybrid_iso=True_ldepth=0.001_lnormal=0.0_laniso_0.0_lseg=1.0'  # experiment directory name

for scene_name in "${scenes[@]}"; do

    # Simulate dynamics and render
    python gs_render_dynamics.py \
        -s ./data/gaussian_data/${scene_name} \
        -m ./gaussian_output/${scene_name}/${exp_name} \
        --name ${scene_name} \

    for view_name in "${views[@]}"; do
        # Convert rendered frames to video
        python gaussian_splatting/img2video.py \
            --image_folder ${output_dir}/${scene_name}/${view_name} \
            --video_path ${output_dir}/${scene_name}/${view_name}.mp4
    done

done
