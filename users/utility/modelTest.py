import pandas as pd
from django.conf import settings
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
from sklearn.tree import  DecisionTreeClassifier

import os


def startResults():
    path = os.path.join(settings.MEDIA_ROOT, 'nist_risk_management_policy_dataset.csv')
    df = pd.read_csv(path)
    print(df.head())

    # Step 2: Classify the data using Random Forest
    df['Status'] = df['Status'].map(
        {'Active': True, 'Inactive': False})
    # Encode categorical variables
    label_encoders = {}
    for column in df.columns[1:]:
        le = LabelEncoder()
        df[column] = le.fit_transform(df[column])
        label_encoders[column] = le
    print(df.head(110))
    # Prepare features and target variable
    df = df.drop(columns=["Policy ID"])
    X = df.iloc[:, :-1].values
    y = df.iloc[:, -1].values
    # y = df["Status"].map({"Active": 1, "Inactive": 0})  # Encoding 'Active' as 1, 'Inactive' as 0
    print(y)
    # Split the dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train a Random Forest classifier
    # rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_classifier = DecisionTreeClassifier()
    rf_classifier.fit(X_train, y_train)

    # Evaluate the model

    y_pred = rf_classifier.predict(X_test)
    accuracy = accuracy_score(y_pred, y_test)
    rf_report = classification_report(y_test, y_pred, output_dict=True)
    rf_report = pd.DataFrame(rf_report).transpose()
    rf_report = pd.DataFrame(rf_report)
    print(f"Random Forest model accuracy: {accuracy * 100:.2f}%")
    return rf_report
