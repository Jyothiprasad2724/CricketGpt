import pandas as pd 
from app.services.sql_storage import main



df_test,df_odi,df_t20 = main()

print(df_test.columns.dtype)




