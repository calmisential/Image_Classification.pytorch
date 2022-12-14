from pathlib import Path

import torch
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm

from core.data import load_dataset
from core.loss import cross_entropy_loss
from core.metrics import MeanMetric
from core.models import select_model
from core.parse_yaml import Yaml
from evaluate import evaluate_loop


def train_loop(cfg, model, train_loader, test_loader, device):
    print("Pytorch version: {}, Train on {}".format(torch.__version__, device))
    print("训练参数如下：")
    for k, v in cfg["Train"].items():
        print(f"{k} : {v}")
    # 训练轮数
    start_epoch = cfg["Train"]["start_epoch"]
    epochs = cfg["Train"]["epochs"]
    save_frequency = cfg["Train"]["save_frequency"]
    save_path = cfg["Train"]["save_path"]
    load_weights = cfg["Train"]["load_weights"]
    tensorboard_on = cfg["Train"]["tensorboard_on"]
    input_size = cfg["Train"]["input_size"]
    batch_size = cfg["Train"]["batch_size"]
    # 优化器
    optimizer = torch.optim.Adam(params=model.parameters(), lr=cfg["Train"]["learning_rate"])
    # 损失函数
    loss_fn = cross_entropy_loss()
    loss_mean = MeanMetric()
    correct_mean = MeanMetric()  # 一个epoch的平均正确率

    if load_weights != "":
        print(f"加载权重文件{load_weights}成功！")
        model.load_state_dict(torch.load(load_weights, map_location=device))
    else:
        start_epoch = 0

    if tensorboard_on:
        # 在控制台使用命令 tensorboard --logdir=runs 进入tensorboard面板
        writer = SummaryWriter()
        writer.add_graph(model, torch.randn(batch_size, *input_size, dtype=torch.float32, device=device))

    for epoch in range(start_epoch, epochs):
        model.train()  # 切换为训练模式
        with tqdm(train_loader, desc="Epoch-{}/{}".format(epoch, epochs)) as pbar:
            for i, (images, targets) in enumerate(pbar):
                batch_size = images.size(0)
                images = images.to(device)
                targets = targets.to(device)

                optimizer.zero_grad()
                preds = model(images)
                loss = loss_fn(preds, targets)
                loss.backward()
                optimizer.step()
                loss_mean.update(loss.item())
                correct_mean.update((preds.argmax(1) == targets).type(torch.float).sum().item() / batch_size)

                if tensorboard_on:
                    writer.add_scalar(tag="Loss", scalar_value=loss_mean.result(),
                                      global_step=epoch * len(train_loader) + i)
                    writer.add_scalar(tag="Accuracy", scalar_value=correct_mean.result(),
                                      global_step=epoch * len(train_loader) + i)

                pbar.set_postfix({"loss": "{}".format(loss_mean.result()),
                                  "accuracy": "{:.4f}%".format(100 * correct_mean.result())})
        loss_mean.reset()
        correct_mean.reset()

        # 验证
        evaluate_loop(model, test_loader, device)

        if epoch % save_frequency == 0:
            torch.save(model.state_dict(),
                       Path(save_path).joinpath("{}_{}_epoch-{}.pth".format(model.model_name, cfg["dataset"], epoch)))

    if tensorboard_on:
        writer.close()

    torch.save(model.state_dict(),
               Path(save_path).joinpath("{}_{}_weights.pth".format(model.model_name, cfg["dataset"])))
    torch.save(model, Path(save_path).joinpath("{}_{}_entire_model.pth".format(model.model_name, cfg["dataset"])))


if __name__ == '__main__':
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 读取配置文件
    cfg = Yaml(yaml_filepath=["./experiments/config.yaml", "./experiments/data.yaml"]).parse()
    print(cfg)

    # 加载数据集
    dataset_name, classes, num_classes, train_dataloader, test_dataloader = load_dataset(cfg)
    cfg.update({"dataset": dataset_name})
    cfg.update({"num_classes": num_classes})

    # 创建网络模型
    model = select_model()(cfg)
    model.to(device=device)

    train_loop(cfg, model, train_dataloader, test_dataloader, device)
