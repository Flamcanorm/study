# MNIST 손글씨 숫자 분류를 위한 NeuralNet 설계

# 구조
MNIST 데이터셋은 28x28의 이미지로 0-255의 명암값을 가지며 0부터 9의 label을 가지고 있다. 효율을 위해 원본의 28x28 이미지를 2x2 크기로 묶어 가로 14, 세로 14의 사이즈로 축소된 196개의 픽셀 정보를 입력 노드로 사용한다.

비선형 패턴 학습을 위해 2개의 은닉층으로 구성하고 첫 번째 은닉층은 196개의 입력값을 받는 128개의 노드로 구성되며 두 번째 은닉층은 이를 64개의 노드로 압축한다. 각 노드는 이전 층의 모든 입력 값에 가중치를 곱해 더하는 선형 결합을 수행한다. 

이 선형 결합 뒤 Sigmoid 함수가 가지는 기울기 소실 문제를 해결하기 위해 ReLU 활성화 함수를 적용하였으며 1차 은닉층에 학습 시 20%를 무작위로 비활성화하는 드롭아웃을 적용하여 과적합 현상을 방지하였다.

마지막으로 추출된 64개의 값들은 출력층으로 전달되어 0부터 9까지의 최종 예측 점수로 변환된다.


# 학습법
60,000장의 훈련 데이터를 50,000장의 학습용과 10,000장의 Validation 으로 나누어 학습하며 최종 평가를 위해 별도의 10,000장 테스트 데이터를 사용했다. (과적합 방지, 하이퍼파라미터 수정을 위해)

학습 속도 향상을 위해 배치 크기 64를 적용하여 미니 배치 단위로 학습을 진행한다. 이렇게 5만장을 모두 학습하고 나면 에폭 10을 적용해 10번 반복 학습한다.

손실 함수로 Cross-Entropy를 사용했다. 기존의 MSE 방식을 사용할 경우 0부터 9 까지의 예측값과 정답 값 사이의 단순 수치적 차이를 계산하기 때문에 얼마나 정답에 가깝게 예측하였는지 나타낼 수 없기에 확률 분포로 오차를 계산하는 Cross-Entropy를 사용하였다.

최적화 알고리즘으로 기존의 경사하강법의 문제인 지역최적해 문제와 학습 속도를 위해 기울기의 모멘텀과 학습률을 동적으로 조절하는 Adam을 사용해 가중치 최적해를 구한다. (초기 설정 학습률 0.001) 그리고 ReLU 활성화 함수에 적합한 HE 가중치 초기화를 적용해 학습 초기 발생할 수 있는 기울기 소실을 방지하고 학습 효율을 높였다.



```python
import torch

import torch.nn as nn

import torch.optim as optim

from torchvision import datasets, transforms

from torch.utils.data import DataLoader, random_split

  

# 1. 데이터 준비 및 전처리

transform = transforms.Compose([transforms.ToTensor()])

  

full_train_data = datasets.MNIST(root='./data', train=True, download=True, transform=transform)

test_data = datasets.MNIST(root='./data', train=False, download=True, transform=transform)

  

train_size = 50000

val_size = 10000

train_data, val_data = random_split(full_train_data, [train_size, val_size])

  

train_loader = DataLoader(train_data, batch_size=64, shuffle=True)

val_loader = DataLoader(val_data, batch_size=64, shuffle=False)

test_loader = DataLoader(test_data, batch_size=64, shuffle=False)

  

# 2. He 가중치 초기화가 적용된 신경망 구조

class HeInitializedNN(nn.Module):

def __init__(self):

super(HeInitializedNN, self).__init__()

self.pool = nn.AvgPool2d(kernel_size=2, stride=2)

# 1차 은닉층 (196 -> 128) + Dropout

self.fc1 = nn.Linear(196, 128)

self.relu1 = nn.ReLU()

self.dropout = nn.Dropout(0.2)

# 2차 은닉층 (128 -> 64)

self.fc2 = nn.Linear(128, 64)

self.relu2 = nn.ReLU()

# 출력층 (64 -> 10)

self.fc3 = nn.Linear(64, 10)

# He 가중치 초기화 적용 메서드 호출

self._initialize_weights()

  

def _initialize_weights(self):

# 모델 안의 모든 레이어에 He 초기화 적용

for m in self.modules():

if isinstance(m, nn.Linear):

# 정규분포 초기화

nn.init.kaiming_normal_(m.weight, nonlinearity='relu')

if m.bias is not None:

nn.init.constant_(m.bias, 0) # 편향은 0으로 초기화

  

def forward(self, x):

x = self.pool(x)

x = x.view(x.size(0), -1) # [배치, 196]

x = self.fc1(x)

x = self.relu1(x)

x = self.dropout(x)

x = self.fc2(x)

x = self.relu2(x)

x = self.fc3(x)

return x

  

# 모델, 손실 함수, 옵티마이저 초기화

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = HeInitializedNN().to(device)

  

criterion = nn.CrossEntropyLoss()

optimizer = optim.Adam(model.parameters(), lr=0.001)

  

# 3. 모델 학습

epochs = 10

print("모델 학습 시작")

  

for epoch in range(epochs):

# 학습 페이즈

model.train()

running_loss = 0.0

for images, labels in train_loader:

images, labels = images.to(device), labels.to(device)

optimizer.zero_grad()

outputs = model(images)

loss = criterion(outputs, labels)

loss.backward()

optimizer.step()

running_loss += loss.item()

train_loss = running_loss / len(train_loader)

# 검증 페이즈

model.eval()

val_loss = 0.0

correct = 0

total = 0

with torch.no_grad():

for images, labels in val_loader:

images, labels = images.to(device), labels.to(device)

outputs = model(images)

loss = criterion(outputs, labels)

val_loss += loss.item()

_, predicted = torch.max(outputs.data, 1)

total += labels.size(0)

correct += (predicted == labels).sum().item()

val_accuracy = 100 * correct / total

avg_val_loss = val_loss / len(val_loader)

print(f"Epoch {epoch+1}/{epochs} | Train Loss: {train_loss:.4f} | Val Loss: {avg_val_loss:.4f} | Val Accuracy: {val_accuracy:.2f}%")

  

# 4. 최종 테스트

print("\n최종 성능 평가")

model.eval()

correct = 0

total = 0

with torch.no_grad():

for images, labels in test_loader:

images, labels = images.to(device), labels.to(device)

outputs = model(images)

_, predicted = torch.max(outputs.data, 1)

total += labels.size(0)

correct += (predicted == labels).sum().item()

  

test_accuracy = 100 * correct / total

print(f"최종 테스트 데이터 정확도: {test_accuracy:.2f}%")
```


# 결과

**학습률 : 0.001, 에폭 : 10, 배치 : 64, 드롭아웃 : 0.2**
![](../../img/Pasted%20image%2020261103050612.png)

**학습률 : 0.01, 에폭 : 5, 배치 : 64, 드롭아웃 : 0.2**
![](../../img/Pasted%20image%2020261103051549.png)

**학습률 : 0.01, 에폭 : 20, 배치 : 64, 드롭아웃 : 0.2**
![](../../img/Pasted%20image%2020261103051905.png)

**학습률 : 0.001, 에폭 : 10, 배치 : 32, 드롭아웃 : 0.3**
![](../../img/Pasted%20image%2020261103052226.png)
