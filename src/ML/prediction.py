import joblib
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.metrics import classification_report, accuracy_score

# Load data from JSON (assuming the data loading and training part)
data = pd.read_json('project_healthy\src\ML\data.json')
X = data[['Blood_Pressure', 'Body_Temperature']]
y = data['Dangerous']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the model
svm_model = SVC(kernel='linear', random_state=42)
svm_model.fit(X_train, y_train)

# Save the model to a file
joblib.dump(svm_model, 'svm_model.pkl')
print("Model saved to 'svm_model.pkl'")

