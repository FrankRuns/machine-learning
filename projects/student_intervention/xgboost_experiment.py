# Import libraries
import numpy as np
import pandas as pd
from time import time
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score

# Pretty display for notebooks
%matplotlib inline
import matplotlib.pyplot as plt
plt.style.use(['bmh'])

# Read student data
student_data = pd.read_csv("student-data.csv")
print "Student data read successfully!"

# TODO: Calculate number of students
n_students = student_data.shape[0]

# TODO: Calculate number of features
n_features = student_data.shape[1] - 1 # -1 as to not count the target column

# TODO: Calculate passing students
n_passed = len(student_data[student_data['passed'] == 'yes'])

# TODO: Calculate failing students
n_failed = len(student_data[student_data['passed'] == 'no'])

# TODO: Calculate graduation rate
grad_rate = (n_passed / float(n_students)) * 100

# Combining Fedu and Medu into one variable
student_data["Pedu"] = student_data["Fedu"] + student_data["Medu"]
student_data = student_data.drop("Fedu", axis=1)
student_data = student_data.drop("Medu", axis=1)

# Extract feature columns
feature_cols = list(student_data.ix[:, student_data.columns != "passed"].columns)

# Extract target column 'passed'
target_col = list(student_data[["passed"]].columns)[0]

# Show the list of columns
print "Feature columns:\n{}".format(feature_cols)
print "\nTarget column: {}".format(target_col)

# Separate the data into feature data and target data (X_all and y_all, respectively)
X_all = student_data[feature_cols]
y_all = student_data[target_col]

def preprocess_features(X):
    ''' Preprocesses the student data and converts non-numeric binary variables into
        binary (0/1) variables. Converts categorical variables into dummy variables. '''
    
    # Initialize new output DataFrame
    output = pd.DataFrame(index = X.index)

    # Investigate each feature column for the data
    for col, col_data in X.iteritems():
        
        # If data type is non-numeric, replace all yes/no values with 1/0
        if col_data.dtype == object:
            col_data = col_data.replace(['yes', 'no'], [1, 0])

        # If data type is categorical, convert to dummy variables
        if col_data.dtype == object:
            # Example: 'school' => 'school_GP' and 'school_MS'
            col_data = pd.get_dummies(col_data, prefix = col)  
        
        # Collect the revised columns
        output = output.join(col_data)
    
    return output

X_all = preprocess_features(X_all)

# TODO: Import any additional functionality you may need here
from sklearn.cross_validation import train_test_split

# TODO: Set the number of training points
num_train = 300

# Set the number of testing points
num_test = X_all.shape[0] - num_train

# TODO: Determine proportion of dataset allocated to test set
test_size = num_test / float(X_all.shape[0])

# TODO: Shuffle and split the dataset into the number of training and testing points above
X_train, X_test, y_train, y_test = train_test_split(X_all, y_all, stratify=y_all, test_size=test_size, random_state=42)

# another pro tip from Udacity coach is to try xgboost
import xgboost as xgb

dtrain = xgb.DMatrix(X_train, label=np.array([1 if y=='yes' else 0 for y in y_train]))
dtest  = xgb.DMatrix(X_test, label=np.array([1 if y=='yes' else 0 for y in y_test]))

params = {
    'bst:max_depth':2,
    'bst:eta':1,
    'silent':1,
    'objective':'binary:logistic',
    'eval_metric': 'auc'
}

evallist  = [(dtest,'test'), (dtrain,'train')]

num_round = 15
bst = xgb.train(params, dtrain, num_round, evallist)

testdmat = xgb.DMatrix(X_test)

predictions = bst.predict(testdmat)

fpredictions = []
for el in predictions:
    if el >= 0.50:
        p = "yes"
    else:
        p = "no"
    fpredictions.append(p)

f1_score(y_test, fpredictions, pos_label='yes')