from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

# Load data
train_data = pd.read_csv('titanic.csv')
test_data = pd.read_csv('titanic_test.csv')
train_label = pd.read_csv('titanic.csv')
test_label = pd.read_csv('titanic_testlabel.csv')

# Train Decision Tree model
model = DecisionTreeClassifier()
model.fit(train_data, train_label)

# Predict test data
predictions = model.predict(test_data)

# Calculate error ratio
error_ratio = 1 - accuracy_score(test_label, predictions)

# Print error ratio
print("Error ratio:", error_ratio)