from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
# 붓꽃 데이터셋 로드
iris = load_iris()
x = iris.data   # 붓꽃 퓨처 값
y = iris.target # 붓꽃 품종 값

# 데이터 랜덤으로 분리(테스트 데이터 0.3, 학습 데이터 0.7)
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)

# DT 모델 객체
dt_model = DecisionTreeClassifier(random_state=50)

# DT 모델 학습
dt_model.fit(x_train, y_train)

# 예측
y_pred_dt = dt_model.predict(x_test)

# 평가(정확도계산)
dt_accuracy = accuracy_score(y_test, y_pred_dt)
print("DT 모델 결과")
print(f"정확도 : {dt_accuracy * 100:.2f}%")


# RF 모델 객체(DT 개수 100)
rf_model = RandomForestClassifier(n_estimators=100, random_state=55)

# 학습
rf_model.fit(x_train, y_train)
# 예측
y_pred_rf = rf_model.predict(x_test)
# 평가(정확도)
rf_accuracy = accuracy_score(y_test, y_pred_rf)
print("RF 모델 결과")
print(f"정확도 : {rf_accuracy * 100:.2f}%")

