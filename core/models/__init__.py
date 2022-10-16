from .alexnet import AlexNet

MODELS = {
    0: AlexNet,
}


def select_model():
    # 选择网络模型
    print("请从下面的网络模型中选择一个：")
    for k, v in MODELS.items():
        print("序号：{}，网络模型名：{}".format(k, v))
    idx = int(input("它的序号为："))
    if idx < 0 or idx >= len(MODELS):
        raise ValueError("输入序号<{}>非法".format(idx))
    return MODELS[idx]