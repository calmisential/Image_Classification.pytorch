from typing import List

import cv2
import numpy as np
import torch
import torchvision.transforms.functional as F


def opencv_read_image(image_path):
    image_array = cv2.imread(image_path, cv2.IMREAD_COLOR | cv2.IMREAD_IGNORE_ORIENTATION)
    image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
    return image_array  # dtype = np.uint8


def read_image(image_paths: List[str], add_dim=False, convert_to_tensor=False, resize=False, size=None):
    n = len(image_paths)
    if n == 1:
        # 只有一张图片
        image_array = opencv_read_image(image_paths[0])
        if add_dim:
            image_array = np.expand_dims(image_array, axis=0)
    else:
        # 多张图片
        image_list = list()
        for i in range(n):
            image = opencv_read_image(image_paths[i])
            image_list.append(image)
        image_array = np.stack(image_list, axis=0)
    if convert_to_tensor:
        image_array = image_array.astype(np.float32)
        image_array /= 255.0
        image_tensor = torch.from_numpy(image_array)  # (N, H, W, C)
        image_tensor = torch.permute(image_tensor, dims=(0, 3, 1, 2))  # (N, C, H, W)
        if resize and size is not None:
            image_tensor = F.resize(image_tensor, size)
        return image_tensor
    return image_array
