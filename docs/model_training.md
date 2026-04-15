# 自训练食物识别模型指南

本文档介绍如何获取数据集、训练食物识别模型，以及将其集成到 Food Calories Calculator 应用中。

## 1. 数据集获取

### 推荐数据集

| 数据集 | 描述 | 类别数 | 图片数 | 链接 |
|--------|------|--------|--------|------|
| Food-101 | 101 种食物类别 | 101 | 101,000 | [ETH Zurich](https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/) |
| UECFOOD-256 | 256 种日本及亚洲食物 | 256 | 31,651 | [UEC](http://foodcam.mobi/dataset256.html) |
| Nutrition5k | 带有详细营养信息的食物图片 | 多类 | 5,000+ | [Google Research](https://github.com/google-research-datasets/Nutrition5k) |
| Food2K | 大规模中国食物数据集 | 2,000 | 1,036,564 | [论文](https://arxiv.org/abs/2107.12580) |

### 自建数据集

如果需要针对特定场景（如中国家常菜）训练模型，可以：

1. **收集图片**：使用手机拍摄不同角度、光照条件下的食物照片
2. **标注数据**：使用 [LabelImg](https://github.com/HumanSignal/labelImg) 或 [CVAT](https://github.com/opencv/cvat) 标注工具
3. **记录营养信息**：参考 [中国食物成分表](http://www.chinanutri.cn/) 获取热量数据

## 2. 模型训练

### 方案 A：使用 Python (PyTorch / TensorFlow)

#### 环境准备

```bash
pip install torch torchvision pillow numpy
```

#### 训练示例（基于 ResNet 迁移学习）

```python
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader

# 1. 数据预处理
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

# 2. 加载数据集（按 类别名/图片.jpg 组织目录结构）
train_dataset = ImageFolder("data/train", transform=transform)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

# 3. 加载预训练 ResNet 并修改分类层
num_classes = len(train_dataset.classes)
model = models.resnet50(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, num_classes)

# 4. 训练
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

for epoch in range(10):
    for images, labels in train_loader:
        outputs = model(images)
        loss = criterion(outputs, labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    print(f"Epoch {epoch+1} completed")

# 5. 保存模型
torch.save(model.state_dict(), "food_model.pth")
```

#### 导出 ONNX 格式（便于跨平台部署）

```python
dummy_input = torch.randn(1, 3, 224, 224)
torch.onnx.export(model, dummy_input, "food_model.onnx",
                  input_names=["image"], output_names=["prediction"])
```

### 方案 B：使用 .NET ML (ML.NET)

#### 环境准备

```bash
dotnet add package Microsoft.ML
dotnet add package Microsoft.ML.Vision
dotnet add package Microsoft.ML.ImageAnalytics
```

#### 训练示例

```csharp
using Microsoft.ML;
using Microsoft.ML.Vision;

var mlContext = new MLContext();

// 1. 加载数据
var data = mlContext.Data.LoadFromTextFile<ImageData>(
    "data/tags.tsv", hasHeader: true);

// 2. 构建训练管道
var pipeline = mlContext.Transforms.Conversion
    .MapValueToKey("Label")
    .Append(mlContext.Transforms.LoadRawImageBytes(
        "Image", "data", "ImagePath"))
    .Append(mlContext.MulticlassClassification.Trainers
        .ImageClassification(new ImageClassificationTrainer.Options
        {
            Arch = ImageClassificationTrainer.Architecture.ResnetV2101,
            Epoch = 10,
            BatchSize = 16,
        }))
    .Append(mlContext.Transforms.Conversion
        .MapKeyToValue("PredictedLabel"));

// 3. 训练模型
var model = pipeline.Fit(data);

// 4. 保存模型
mlContext.Model.Save(model, data.Schema, "FoodModel.zip");
```

## 3. 集成到应用中

### 修改 `backend/app/services/local_model.py`

将 demo 实现替换为实际的模型推理：

```python
import torch
import torchvision.transforms as transforms
from PIL import Image
import io
import json

# 加载模型和类别映射
MODEL_PATH = "models/food_model.pth"
CLASSES_PATH = "models/classes.json"
CALORIES_PATH = "models/calories.json"

model = None
classes = []
calorie_db = {}

def load_model():
    global model, classes, calorie_db
    # 加载类别映射
    with open(CLASSES_PATH) as f:
        classes = json.load(f)
    # 加载热量数据库
    with open(CALORIES_PATH) as f:
        calorie_db = json.load(f)
    # 加载 PyTorch 模型
    model = models.resnet50(num_classes=len(classes))
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()

# 图像预处理（与训练时一致）
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

async def recognize_single(image_bytes: bytes) -> RecognitionResult:
    if model is None:
        load_model()

    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        output = model(tensor)
        probabilities = torch.softmax(output, dim=1)
        top_k = torch.topk(probabilities, k=5)

    foods = []
    for idx, prob in zip(top_k.indices[0], top_k.values[0]):
        if prob.item() < 0.1:
            continue
        name = classes[idx.item()]
        cal = calorie_db.get(name, 100)
        estimated_grams = 150  # 需要额外的重量估计模型
        foods.append(FoodItem(
            name=name,
            calories_per_100g=cal,
            estimated_grams=estimated_grams,
            estimated_calories=cal * estimated_grams / 100,
        ))

    total = sum(f.estimated_calories for f in foods)
    return RecognitionResult(
        foods=foods,
        total_calories=total,
        model_used="local-resnet50",
        description=f"识别到 {len(foods)} 种食物",
    )
```

### 重量估计

食物重量估计是一个独立的视觉任务，可以通过以下方式改进：

1. **参照物法**：在照片中放置已知大小的参照物（如硬币）来估算食物体积
2. **深度估计模型**：使用单目深度估计模型（如 MiDaS）估算食物的三维体积
3. **查找表法**：根据食物类别和典型份量建立查找表（本项目默认方案）

## 4. 目录结构

训练好的模型文件应放置在以下位置：

```
backend/
  models/
    food_model.pth       # PyTorch 模型权重
    food_model.onnx      # ONNX 格式（可选）
    classes.json          # 类别名称列表
    calories.json         # 食物热量数据库 (kcal/100g)
```

## 5. 注意事项

- 食物识别的准确性很大程度上取决于训练数据的质量和多样性
- 重量估计是一个更具挑战性的问题，目前主要依赖经验值
- 建议结合 OpenRouter 的多模态模型使用，获得更好的效果
- 饭前饭后对比功能可以显著提高摄入量的估计精度
