from .alexnet import AlexNet
from .vgg import VGG16, VGG19
from .resnet import ResNet18, ResNet34, ResNet50, ResNet101, ResNet152, ResNet18Pretrained, ResNet34Pretrained, ResNet50Pretrained, ResNet101Pretrained, ResNet152Pretrained

MODELS = {
    0: [AlexNet, "AlexNet"],
    1: [VGG16, "VGG16"],
    2: [VGG19, "VGG19"],
    3: [ResNet18, "ResNet18"],
    4: [ResNet34, "ResNet34"],
    5: [ResNet50, "ResNet50"],
    6: [ResNet101, "ResNet101"],
    7: [ResNet152, "ResNet152"],
    8: [ResNet18Pretrained, "ResNet18Pretrained"],
    9: [ResNet34Pretrained, "ResNet34Pretrained"],
    10: [ResNet50Pretrained, "ResNet50Pretrained"],
    11: [ResNet101Pretrained, "ResNet101Pretrained"],
    12: [ResNet152Pretrained, "ResNet152Pretrained"]
}


def select_model():
    # 选择网络模型
    print("请从下面的网络模型中选择一个：")
    for k, v in MODELS.items():
        print("序号：{}，网络模型名：{}".format(k, v[1]))
    idx = int(input("它的序号为："))
    if idx < 0 or idx >= len(MODELS):
        raise ValueError("输入序号<{}>非法".format(idx))
    print("已选择模型：{}".format(MODELS[idx][1]))
    return MODELS[idx][0]
