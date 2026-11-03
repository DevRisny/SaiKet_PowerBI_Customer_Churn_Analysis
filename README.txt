SaiKet Systems - Power BI Internship
Project: Customer Churn Analysis and Prediction
Intern: Junaideen Risny Suha | Offer Ref No: SKS/A2/C166315
Duration: 25/09/2026 to 25/10/2026

FILES (one file for each level)
Task1_Data_Connection.pbix       Level 1 - Telco customer CSV imported into Power BI (7,043 rows, 21 columns)
Task2_Data_Transformation.pbix   Level 2 - Power Query cleaning: trimmed text, duplicate check, 11 blank TotalCharges fixed,
                                 data types, Churn Flag, Tenure Group, Yes/No labels
Task3_Dashboard.pbix             Level 3 - dashboard, 5 pages:
                                   1 Churn Rate Overview   2 Customer Demographics   3 Customer Tenure Analysis
                                   4 Churn Analysis (contract, payment method, internet service; stacked bars + heatmap)
                                   5 Churn Prediction (logistic regression, risk levels, drivers, retention list)
Telco_Customer_Churn_Dataset.csv Source data
Model_Output/                    Prediction files used by page 5
   train.py                      Python script (scikit-learn) that creates the scores
   Customer_Risk_Scores.csv, Model_Drivers.csv, Retention_Priority_List.csv, Model_Metrics.json

KEY RESULTS
Customers 7,043 | Churned 1,869 | Churn rate 26.54%
Month-to-month contracts 42.7% churn vs two-year 2.8%; fiber optic 41.9% vs DSL 19.0%; electronic check 45.3%
Model: logistic regression, 5-fold cross-validated - ROC AUC 0.845, accuracy 80.5%, precision 65.9%, recall 55.3%

NOTE
The .pbix files contain the imported data and open without refresh. To refresh Task3, keep the Model_Output folder and the CSV
at the paths used in Power Query (or update the file paths in Transform data > Data source settings).
