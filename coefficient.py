import streamlit as st

import pandas as pd
import numpy as np

import os

from lightgbm  import LGBMRegressor
from sklearn.model_selection import GridSearchCV

import plotly.express as px

def calculate_figure_number(*args,**kwargs):
    df=kwargs.get('df').copy()

    number_column=kwargs.get('number_column')
    title=f'{number_column}'

    fig = px.box(
        df,
        y=number_column,
        hover_data=df.columns,
        points="all",
        boxmode="overlay",
        title=title,
    )

    fig.add_hline(y=1, line_dash='dash')
    fig.add_hline(y=df[number_column].min(), line_dash='dash')
    fig.add_hline(y=df[number_column].max(), line_dash='dash')

    fig.for_each_annotation(lambda title: title.update(font=dict(size=15)))
    fig.for_each_xaxis(lambda axis: axis.title.update(font=dict(size=15)))
    fig.for_each_yaxis(lambda axis: axis.title.update(font=dict(size=15)))

    return fig 


def calculate_figure_categorical(*args,**kwargs):
    df=kwargs.get('df').copy()

    number_column=kwargs.get('number_column')
    categorical_column=kwargs.get('categorical_column')

    title=f'{categorical_column} {number_column}'

    fig = px.box(
        df,
        x=categorical_column,
        y=number_column,
        color=categorical_column,
        hover_data=df.columns,
        points="all",
        boxmode="overlay",
        title=title,
    )

    fig.add_hline(y=1, line_dash='dash')
    fig.add_hline(y=df[number_column].min(), line_dash='dash')
    fig.add_hline(y=df[number_column].max(), line_dash='dash')

    fig.for_each_annotation(lambda title: title.update(font=dict(size=15)))
    fig.for_each_xaxis(lambda axis: axis.title.update(font=dict(size=15)))
    fig.for_each_yaxis(lambda axis: axis.title.update(font=dict(size=15)))

    return fig 

def calculate_figure_date(*args,**kwargs):
    df=kwargs.get('df').copy()

    number_column=kwargs.get('number_column')
    date_column=kwargs.get('date_column')

    title=f'{date_column} {number_column}'

    fig = px.box(
        df,
        x=date_column,
        y=number_column,
        hover_data=df.columns,
        title=title,
    )

    fig.add_hline(y=1, line_dash='dash')
    fig.add_hline(y=df[number_column].min(), line_dash='dash')
    fig.add_hline(y=df[number_column].max(), line_dash='dash')

    fig.for_each_annotation(lambda title: title.update(font=dict(size=15)))
    fig.for_each_xaxis(lambda axis: axis.title.update(font=dict(size=15)))
    fig.for_each_yaxis(lambda axis: axis.title.update(font=dict(size=15)))

    return fig 


class Prediction:
    def __init__(self, *args,**kwargs):
        self.df = kwargs.get('df')
        self.ignore_columns = kwargs.get('ignore_columns') 
        self.target_columns = kwargs.get('target_columns')

        self.calculate_data()
        self.calculate_predict()

    def calculate_data(self,*args,**kwargs):
        df=self.df.copy()

        self.predict_columns =[f'{column}_predict'for column in self.target_columns]
        self.coefficient_columns =[f'{column}_coefficient'for column in self.target_columns]

        columns=df.select_dtypes(include=['number']).columns.to_list()
        self.number_columns=list(set(columns).difference(set(self.ignore_columns)).difference(set(self.target_columns)))

        self.categorical_columns = df.select_dtypes(include=['object']).columns
        
        self.date_columns = df.select_dtypes(include=['datetime']).columns.to_list()
        self.date_columns=list(set(self.date_columns).difference(set(self.ignore_columns)))

        for column in self.date_columns:
            df[f'year_of_{column}'] = df[column].dt.year
            df[f'month_of_{column}'] = df[column].dt.month
            df[f'day_of_{column}'] = df[column].dt.day

        df[self.categorical_columns] = df[self.categorical_columns].astype('category')
        self.categorical_columns=list(set(self.categorical_columns).difference(set(self.ignore_columns)))

        columns=df.select_dtypes(include=['category','number']).columns.to_list()
        self.feature_columns=list(set(columns).difference(set(self.ignore_columns)).difference(set(self.target_columns)))

        self.df_train=df
    
    def calculate_predict(self,*args,**kwargs):
        df=self.df_train.copy()

        model = LGBMRegressor()

        parameters = {
            "max_depth": [3, 4, 6, 5, 10, 20],
            "learning_rate": [0.01, 0.05, 0.1, 0.2, 0.3],
            "n_estimators": [50, 100, 250],
            "colsample_bytree": [0.3, 0.5, 0.7, 1]
        }

        model = GridSearchCV(estimator=model, param_grid=parameters, cv=4)

        model.fit(df[self.feature_columns], df[self.target_columns])

        df_tmp=pd.DataFrame(data=model.predict(df[self.feature_columns]), columns=self.predict_columns)
        df_predict=pd.concat([df, df_tmp], axis=1)

        for i in zip(self.coefficient_columns, self.target_columns, self.predict_columns):
            df_predict[i[0]] = df_predict[i[1]] / df_predict[i[2]]

        self.df_predict=df_predict

        df_feature_importance = pd.DataFrame({'feature': self.feature_columns, 'importance': model.best_estimator_.feature_importances_})

        df_feature_importance.sort_values(by='importance', ascending=False, inplace=True)
        df_feature_importance['importance_percent']=df_feature_importance['importance']/df_feature_importance['importance'].sum()
        df_feature_importance['importance_percent_cumsum']=df_feature_importance['importance_percent'].cumsum()
        df_feature_importance.reset_index(drop=True, inplace=True)

        self.df_feature_importance=df_feature_importance


def calculate_results(*args,**kwargs):
    df=kwargs.get('df')
    ignore_columns=kwargs.get('ignore_columns')
    target_columns=kwargs.get('target_columns')


    prediction=Prediction(**dict(df=df, ignore_columns=ignore_columns, target_columns=target_columns))

    df_elements=[]

    df_prediction=prediction.df_predict.copy()
    df_elements.append(dict(name='prediction', df=df_prediction))

    df_feature_importance=prediction.df_feature_importance.copy()
    df_elements.append(dict(name='feature_importance', df=df_feature_importance))

    fig_number_elements=[]
    fig_categorical_elements=[]
    fig_date_elements=[]

    ignore_columns=prediction.ignore_columns
    feature_columns=prediction.feature_columns
    target_columns=prediction.target_columns
    coefficient_columns=prediction.coefficient_columns
    number_columns=prediction.number_columns
    predict_columns=prediction.predict_columns

    categorical_columns=prediction.categorical_columns
    date_columns=prediction.date_columns

    record_elements=[]

    record=dict(
        feature_columns=feature_columns,
        ignore_columns=prediction.ignore_columns,
        number_columns=number_columns,
        categorical_columns=categorical_columns,
        date_columns=date_columns,
        target_columns=target_columns,
        predict_columns=predict_columns,
        coefficient_columns=coefficient_columns,
    )

    record_elements.append(dict(name='columns', record=record))

    columns=coefficient_columns+predict_columns+target_columns+number_columns
    for number_column in columns:
        fig=calculate_figure_number(**dict(df=df_prediction, number_column=number_column))
        fig_number_elements.append(dict(name=number_column, fig=fig))

    for categorical_column in categorical_columns:
        for number_column in columns:
            fig=calculate_figure_categorical(**dict(df=df_prediction, number_column=number_column, categorical_column=categorical_column))
            fig_categorical_elements.append(dict(name=f'{categorical_column} {number_column}', fig=fig))

    for date_column in date_columns:
        for number_column in columns:
            fig=calculate_figure_date(**dict(df=df_prediction, number_column=number_column, date_column=date_column))
            fig_date_elements.append(dict(name=f'{date_column} {number_column}', fig=fig))

    rst=dict(
        df_elements=df_elements, 
        fig_number_elements=fig_number_elements, 
        fig_categorical_elements=fig_categorical_elements,
        fig_date_elements=fig_date_elements,
        record_elements=record_elements, 
    )
    return rst